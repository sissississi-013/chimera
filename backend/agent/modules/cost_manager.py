"""
Cost Management Module - Tracks and enforces spending limits
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class CostEntry:
    """Single cost entry"""
    timestamp: datetime
    service: str  # 'molmim', 'genmol', 'neurosnap', 'diffdock', etc.
    operation: str  # 'generate', 'toxicity', 'admet', etc.
    amount: float
    molecule_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostLimits:
    """Cost limits configuration"""
    max_total_cost: float = 10.0  # Maximum total spend per run
    max_cost_per_molecule: float = 0.50  # Max spend evaluating a single molecule
    max_generation_cost: float = 2.0  # Max spend on generation phase
    max_evaluation_cost: float = 5.0  # Max spend on evaluation phase
    warn_threshold: float = 0.75  # Warn when reaching 75% of limit


class CostManager:
    """
    Manages cost tracking and enforcement for API calls
    """

    def __init__(self, limits: Optional[CostLimits] = None):
        self.limits = limits or CostLimits()
        self.entries: List[CostEntry] = []
        self.total_cost = 0.0
        self.cost_by_service: Dict[str, float] = {}
        self.cost_by_phase: Dict[str, float] = {'generation': 0.0, 'evaluation': 0.0}
        self.warnings_issued: List[str] = []

    def add_cost(
        self,
        service: str,
        operation: str,
        amount: float,
        phase: str = 'unknown',
        molecule_id: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> bool:
        """
        Add a cost entry and check if limits are exceeded

        Args:
            service: API service name
            operation: Operation type
            amount: Cost amount in USD
            phase: 'generation' or 'evaluation'
            molecule_id: Optional molecule ID
            details: Additional details

        Returns:
            True if cost was added, False if limit would be exceeded
        """
        # Check if adding this cost would exceed limits
        new_total = self.total_cost + amount

        if new_total > self.limits.max_total_cost:
            logger.error(f"❌ Cost limit exceeded: ${new_total:.3f} > ${self.limits.max_total_cost:.2f}")
            return False

        if phase == 'generation':
            new_gen_cost = self.cost_by_phase['generation'] + amount
            if new_gen_cost > self.limits.max_generation_cost:
                logger.error(f"❌ Generation cost limit exceeded: ${new_gen_cost:.3f} > ${self.limits.max_generation_cost:.2f}")
                return False

        if phase == 'evaluation':
            new_eval_cost = self.cost_by_phase['evaluation'] + amount
            if new_eval_cost > self.limits.max_evaluation_cost:
                logger.error(f"❌ Evaluation cost limit exceeded: ${new_eval_cost:.3f} > ${self.limits.max_evaluation_cost:.2f}")
                return False

        # Add the cost
        entry = CostEntry(
            timestamp=datetime.now(),
            service=service,
            operation=operation,
            amount=amount,
            molecule_id=molecule_id,
            details=details or {}
        )

        self.entries.append(entry)
        self.total_cost += amount

        if service not in self.cost_by_service:
            self.cost_by_service[service] = 0.0
        self.cost_by_service[service] += amount

        if phase in self.cost_by_phase:
            self.cost_by_phase[phase] += amount

        logger.info(f"💰 Cost added: ${amount:.3f} ({service}/{operation}) - Total: ${self.total_cost:.3f}")

        # Check for warnings
        self._check_warnings()

        return True

    def can_afford(self, amount: float, phase: str = 'unknown') -> bool:
        """
        Check if we can afford a given amount

        Args:
            amount: Amount to check
            phase: 'generation' or 'evaluation'

        Returns:
            True if within limits
        """
        if self.total_cost + amount > self.limits.max_total_cost:
            return False

        if phase == 'generation':
            if self.cost_by_phase['generation'] + amount > self.limits.max_generation_cost:
                return False

        if phase == 'evaluation':
            if self.cost_by_phase['evaluation'] + amount > self.limits.max_evaluation_cost:
                return False

        return True

    def get_remaining_budget(self, phase: Optional[str] = None) -> float:
        """
        Get remaining budget

        Args:
            phase: Optional phase to check ('generation' or 'evaluation')

        Returns:
            Remaining budget in USD
        """
        if phase:
            if phase not in self.cost_by_phase:
                return 0.0

            if phase == 'generation':
                return max(0.0, self.limits.max_generation_cost - self.cost_by_phase['generation'])
            elif phase == 'evaluation':
                return max(0.0, self.limits.max_evaluation_cost - self.cost_by_phase['evaluation'])

        return max(0.0, self.limits.max_total_cost - self.total_cost)

    def _check_warnings(self):
        """Check if we should issue warnings about approaching limits"""
        # Total cost warning
        if self.total_cost / self.limits.max_total_cost >= self.limits.warn_threshold:
            warning = f"Total cost approaching limit: ${self.total_cost:.2f} / ${self.limits.max_total_cost:.2f}"
            if warning not in self.warnings_issued:
                logger.warning(f"⚠️  {warning}")
                self.warnings_issued.append(warning)

        # Generation phase warning
        gen_ratio = self.cost_by_phase['generation'] / self.limits.max_generation_cost
        if gen_ratio >= self.limits.warn_threshold:
            warning = f"Generation cost approaching limit: ${self.cost_by_phase['generation']:.2f} / ${self.limits.max_generation_cost:.2f}"
            if warning not in self.warnings_issued:
                logger.warning(f"⚠️  {warning}")
                self.warnings_issued.append(warning)

        # Evaluation phase warning
        eval_ratio = self.cost_by_phase['evaluation'] / self.limits.max_evaluation_cost
        if eval_ratio >= self.limits.warn_threshold:
            warning = f"Evaluation cost approaching limit: ${self.cost_by_phase['evaluation']:.2f} / ${self.limits.max_evaluation_cost:.2f}"
            if warning not in self.warnings_issued:
                logger.warning(f"⚠️  {warning}")
                self.warnings_issued.append(warning)

    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary"""
        return {
            'total_cost': round(self.total_cost, 3),
            'remaining_budget': round(self.get_remaining_budget(), 3),
            'cost_by_service': {k: round(v, 3) for k, v in self.cost_by_service.items()},
            'cost_by_phase': {k: round(v, 3) for k, v in self.cost_by_phase.items()},
            'num_operations': len(self.entries),
            'limits': {
                'max_total': self.limits.max_total_cost,
                'max_generation': self.limits.max_generation_cost,
                'max_evaluation': self.limits.max_evaluation_cost
            },
            'warnings': self.warnings_issued
        }

    def get_detailed_report(self) -> List[Dict[str, Any]]:
        """Get detailed cost report"""
        return [
            {
                'timestamp': entry.timestamp.isoformat(),
                'service': entry.service,
                'operation': entry.operation,
                'amount': round(entry.amount, 3),
                'molecule_id': entry.molecule_id,
                'details': entry.details
            }
            for entry in self.entries
        ]


# Estimated API costs (in USD)
API_COSTS = {
    'molmim': {
        'generate': 0.02,  # Per batch of molecules
    },
    'genmol': {
        'generate': 0.015,  # Per batch
    },
    'alphafold2': {
        'predict': 0.10,  # Per structure prediction
    },
    'diffdock': {
        'dock': 0.05,  # Per docking simulation
    },
    'neurosnap': {
        'toxicity': 0.005,  # Per molecule
        'synthesizability': 0.003,  # Per molecule
        'admet': 0.007,  # Per molecule
        'comprehensive': 0.015,  # All three
    }
}
