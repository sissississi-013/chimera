"""
Enhanced Payment Manager - Handles x402, Budget Tracking, and Decision Logic
Implements autonomous cost/benefit analysis and Locus-style spending policies
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SpendingPolicy:
    """Locus-style spending policy enforcement"""

    def __init__(self, max_per_hour: float = 1.0, max_per_transaction: float = 0.5):
        self.max_per_hour = max_per_hour
        self.max_per_transaction = max_per_transaction
        self.transactions: List[Dict[str, Any]] = []
        self.start_time = datetime.now()

    def can_spend(self, amount: float, service: str) -> tuple[bool, str]:
        """Check if spending is allowed under policy"""
        # Check per-transaction limit
        if amount > self.max_per_transaction:
            return False, f"Transaction ${amount:.2f} exceeds per-transaction limit ${self.max_per_transaction:.2f}"

        # Check hourly limit
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_spend = sum(
            tx['amount'] for tx in self.transactions
            if datetime.fromisoformat(tx['timestamp']) > hour_ago
        )

        if recent_spend + amount > self.max_per_hour:
            return False, f"Would exceed hourly limit (${recent_spend:.2f} spent, ${amount:.2f} requested, ${self.max_per_hour:.2f} limit)"

        return True, "OK"

    def record_transaction(self, amount: float, service: str, method: str = "x402"):
        """Record a transaction"""
        tx = {
            'id': f"tx_{len(self.transactions) + 1}",
            'amount': amount,
            'service': service,
            'method': method,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
        self.transactions.append(tx)
        logger.info(f"💰 Transaction recorded: ${amount:.2f} to {service}")
        return tx

    def get_summary(self) -> Dict[str, Any]:
        """Get spending summary"""
        total_spent = sum(tx['amount'] for tx in self.transactions)
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_spend = sum(
            tx['amount'] for tx in self.transactions
            if datetime.fromisoformat(tx['timestamp']) > hour_ago
        )

        return {
            'total_spent': total_spent,
            'hourly_spend': recent_spend,
            'hourly_limit': self.max_per_hour,
            'remaining_budget': self.max_per_hour - recent_spend,
            'transaction_count': len(self.transactions),
            'transactions': self.transactions
        }


class X402Handler:
    """Handles HTTP 402 Payment Required responses"""

    @staticmethod
    def detect_402(response_data: Dict[str, Any]) -> bool:
        """Check if response indicates 402 payment required"""
        return response_data.get('status_code') == 402 or response_data.get('payment_required', False)

    @staticmethod
    def parse_payment_request(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse payment details from 402 response"""
        return {
            'amount': response_data.get('amount', 0.0),
            'currency': response_data.get('currency', 'USD'),
            'address': response_data.get('payment_address', '0x...'),
            'service': response_data.get('service_name', 'Unknown Service'),
            'description': response_data.get('description', 'API call payment')
        }

    @staticmethod
    def create_payment_proof(wallet_address: str, amount: float, tx_hash: str) -> str:
        """Create payment proof header for x402"""
        # In production, this would be a signed JWT or similar
        return f"X-Payment: wallet={wallet_address},amount={amount},tx={tx_hash}"


class CostBenefitAnalyzer:
    """Autonomous decision-making for cost vs value"""

    @staticmethod
    def should_pay(
        cost: float,
        service_name: str,
        expected_value: str,
        current_budget: float,
        context: Dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Agent decides whether to pay for a service based on cost/benefit

        Returns: (decision: bool, reasoning: str)
        """
        # Critical services (high priority)
        critical_services = ['docking', 'toxicity', 'efficacy']
        is_critical = any(svc in service_name.lower() for svc in critical_services)

        # Calculate cost as percentage of budget
        cost_pct = (cost / current_budget * 100) if current_budget > 0 else 100

        # Decision logic
        if cost > current_budget:
            return False, f"Cost ${cost:.2f} exceeds remaining budget ${current_budget:.2f}"

        if is_critical and cost_pct <= 60:
            return True, f"Critical service ({service_name}), cost is {cost_pct:.0f}% of budget - worthwhile investment"

        if cost_pct <= 30:
            return True, f"Low cost ({cost_pct:.0f}% of budget), acceptable risk"

        if is_critical and cost_pct <= 80:
            return True, f"High-priority service, cost {cost_pct:.0f}% of budget but necessary for quality"

        # Check if we have previous successful transactions
        if context.get('molecules_passed', 0) > 0 and cost_pct <= 50:
            return True, f"Previous success, cost {cost_pct:.0f}% reasonable for validation"

        # Otherwise, be conservative
        return False, f"Cost {cost_pct:.0f}% of budget seems high for non-critical service, skipping"


class EnhancedPaymentManager:
    """
    Comprehensive payment manager integrating:
    - x402 protocol handling
    - Locus-style spending policies
    - Autonomous cost/benefit decisions
    - CDP wallet integration (simulated for now)
    """

    def __init__(self, initial_budget: float = 5.0):
        self.policy = SpendingPolicy(max_per_hour=1.0, max_per_transaction=0.5)
        self.initial_budget = initial_budget
        self.wallet_address = "0xDemo1234567890abcdef" # Would be real CDP wallet
        self.analyzer = CostBenefitAnalyzer()
        self.decision_log: List[Dict[str, Any]] = []

    def handle_api_call(
        self,
        service_name: str,
        base_cost: float,
        expected_value: str,
        context: Dict[str, Any],
        simulate_402: bool = True
    ) -> Dict[str, Any]:
        """
        Autonomous API call with payment handling

        Returns result dict with:
        - success: bool
        - data: Any (API response data)
        - paid: bool
        - amount: float
        - decision_reasoning: str
        - transaction: Dict (if paid)
        """
        result = {
            'success': False,
            'paid': False,
            'amount': 0.0,
            'service': service_name,
            'decision_reasoning': ''
        }

        # Simulate 402 response
        if simulate_402:
            logger.info(f"🔄 Calling {service_name}...")
            logger.info(f"⚠️  HTTP 402 Payment Required: ${base_cost:.2f}")

            # Check policy first
            can_spend, policy_msg = self.policy.can_spend(base_cost, service_name)
            if not can_spend:
                result['decision_reasoning'] = f"Policy blocked: {policy_msg}"
                logger.warning(f"🚫 {result['decision_reasoning']}")
                self.log_decision(service_name, base_cost, False, result['decision_reasoning'])
                return result

            # Cost/benefit analysis
            budget_summary = self.policy.get_summary()
            remaining = budget_summary['remaining_budget']

            should_pay, reasoning = self.analyzer.should_pay(
                base_cost,
                service_name,
                expected_value,
                remaining,
                context
            )

            result['decision_reasoning'] = reasoning
            self.log_decision(service_name, base_cost, should_pay, reasoning)

            if not should_pay:
                logger.info(f"🤔 Agent decision: NO - {reasoning}")
                return result

            logger.info(f"✅ Agent decision: YES - {reasoning}")

            # Execute payment
            payment_result = self.execute_payment(base_cost, service_name)

            if payment_result['success']:
                result['paid'] = True
                result['amount'] = base_cost
                result['transaction'] = payment_result['transaction']
                result['success'] = True
                result['data'] = self.simulate_api_response(service_name)
                logger.info(f"💳 Payment successful. API call completed.")
                return result
            else:
                result['decision_reasoning'] = f"Payment failed: {payment_result.get('error')}"
                logger.error(f"❌ {result['decision_reasoning']}")
                return result

        # No payment required (free service)
        result['success'] = True
        result['data'] = self.simulate_api_response(service_name)
        logger.info(f"✅ {service_name} call succeeded (free service)")
        return result

    def execute_payment(self, amount: float, service: str) -> Dict[str, Any]:
        """
        Execute payment via CDP wallet (simulated for demo)
        In production: would call Coinbase CDP API
        """
        logger.info(f"💰 Initiating payment: ${amount:.2f} USDC to {service}")
        logger.info(f"🔐 Signing transaction with wallet {self.wallet_address[:10]}...")

        # Simulate blockchain transaction
        import time
        time.sleep(0.5)  # Simulate network delay

        tx_hash = f"0x{''.join([f'{i:02x}' for i in range(32)])}"  # Mock tx hash
        logger.info(f"✓ Transaction confirmed: {tx_hash[:16]}...")

        # Record in policy
        transaction = self.policy.record_transaction(amount, service, "x402_USDC")
        transaction['tx_hash'] = tx_hash

        return {
            'success': True,
            'transaction': transaction,
            'tx_hash': tx_hash
        }

    def log_decision(self, service: str, cost: float, approved: bool, reasoning: str):
        """Log agent decision for audit trail"""
        decision = {
            'timestamp': datetime.now().isoformat(),
            'service': service,
            'cost': cost,
            'approved': approved,
            'reasoning': reasoning
        }
        self.decision_log.append(decision)

    def simulate_api_response(self, service_name: str) -> Dict[str, Any]:
        """Simulate API responses for different services"""
        responses = {
            'docking': {
                'binding_affinity': 8.7,
                'binding_energy': -9.2,
                'confidence': 0.89,
                'analysis': 'Strong binding predicted to target site'
            },
            'toxicity': {
                'toxicity_score': 0.23,
                'risk_level': 'low',
                'ld50_predicted': '> 2000 mg/kg',
                'pass': True
            },
            'efficacy': {
                'predicted_efficacy': 0.78,
                'target_selectivity': 0.91,
                'off_target_effects': 'minimal'
            },
            'synthesizability': {
                'sa_score': 2.4,
                'synthetic_accessibility': 'easy',
                'estimated_steps': 4
            }
        }

        for key in responses:
            if key in service_name.lower():
                return responses[key]

        return {'result': 'success', 'data': 'completed'}

    def get_full_report(self) -> Dict[str, Any]:
        """Generate comprehensive payment report"""
        return {
            'budget_summary': self.policy.get_summary(),
            'decisions': self.decision_log,
            'wallet_address': self.wallet_address,
            'total_decisions': len(self.decision_log),
            'approved_count': sum(1 for d in self.decision_log if d['approved']),
            'denied_count': sum(1 for d in self.decision_log if not d['approved'])
        }
