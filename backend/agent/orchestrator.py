"""
Agent Orchestrator - Coordinates all modules and manages execution flow
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from .models.agent_state import (
    AgentState, AgentRequest, AgentResponse, AgentPhase
)
from .models.molecule import MoleculeStatus
from .modules.planning import PlanningModule
from .modules.generation import MoleculeGenerationModule
from .modules.evaluation import EvaluationModule
from .modules.visualization import VisualizationModule
from .modules.data_sharing import DataSharingModule
from .modules.payment import PaymentModule


class AgentOrchestrator:
    """
    The Orchestrator is the "brain" of Chimera.
    It coordinates all modules, manages state, makes decisions about iteration,
    and ensures the autonomous agent follows its plan while adapting to results.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize orchestrator with modules

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

        # Initialize all modules
        self.planning_module = PlanningModule(config)
        self.generation_module = MoleculeGenerationModule(config)
        self.evaluation_module = EvaluationModule(config)
        self.visualization_module = VisualizationModule(config)
        self.data_sharing_module = DataSharingModule(config)
        self.payment_module = PaymentModule(config)

    async def run(self, request: AgentRequest) -> AgentState:
        """
        Execute the full autonomous agent workflow

        Args:
            request: Agent request with goal and budget

        Returns:
            Final agent state with results
        """
        # Initialize state
        state = AgentState(
            run_id=f"run_{uuid.uuid4().hex[:12]}",
            phase=AgentPhase.PLANNING
        )

        # Store request parameters in state
        state.goal = request.goal
        state.target = request.target
        state.total_budget = request.budget
        state.constraints = request.constraints

        state.add_log(f"Starting Chimera run: {state.run_id}")
        state.add_log(f"Goal: {request.goal}")
        state.add_log(f"Budget: ${request.budget:.2f}")

        try:
            # Phase 1: Planning
            state = await self.planning_module.execute(state)

            if not state.plan:
                raise Exception("Planning failed - no execution plan created")

            # Main execution loop (allows for iterations)
            max_iterations = state.plan.max_iterations
            iteration = 0

            while iteration < max_iterations:
                state.current_iteration = iteration
                state.add_log(f"\n=== Iteration {iteration + 1}/{max_iterations} ===")

                # Phase 2: Generation
                state = await self.generation_module.execute(state)

                if not state.molecules:
                    state.add_log("No molecules generated. Cannot continue.")
                    break

                # Phase 3: Evaluation
                state = await self.evaluation_module.execute(state)

                # Check if we have successful candidates
                passed_molecules = [m for m in state.molecules if m.status == MoleculeStatus.PASSED]

                if passed_molecules:
                    state.add_log(f"Success! {len(passed_molecules)} molecule(s) passed all criteria.")
                    break  # Success - exit iteration loop

                # No successful candidates - decide whether to retry
                state.add_log(f"No molecules passed criteria in iteration {iteration + 1}")

                if iteration + 1 < max_iterations:
                    # Check if we have budget for another iteration
                    budget_remaining = state.plan.budget_allocation.remaining
                    generation_cost = self.generation_module.get_required_budget(state)
                    eval_cost_estimate = state.plan.budget_allocation.evaluation_budget / max_iterations

                    if budget_remaining >= (generation_cost + eval_cost_estimate):
                        state.add_log(f"Retrying with adjusted parameters (Budget remaining: ${budget_remaining:.2f})")
                        iteration += 1
                        # Could adjust generation parameters here for next iteration
                        self._adjust_generation_strategy(state)
                    else:
                        state.add_log("Insufficient budget for another iteration")
                        break
                else:
                    state.add_log("Max iterations reached")
                    break

            # Phase 4: Visualization (if we have passing molecules)
            passed_molecules = [m for m in state.molecules if m.status == MoleculeStatus.PASSED]

            if passed_molecules:
                state = await self.visualization_module.execute(state)

                # Phase 5: Monetization
                state = await self.data_sharing_module.execute(state)

                state.phase = AgentPhase.COMPLETED
                state.add_log("\n=== Run Completed Successfully ===")
            else:
                state.phase = AgentPhase.FAILED
                state.add_log("\n=== Run Failed: No suitable molecules found ===")

            # Generate final report
            state.final_results = self._generate_final_report(state)

        except Exception as e:
            state.phase = AgentPhase.FAILED
            state.error = str(e)
            state.add_log(f"ERROR: {str(e)}")

        finally:
            state.end_time = datetime.now()
            duration = (state.end_time - state.start_time).total_seconds()
            state.add_log(f"\nTotal execution time: {duration:.2f} seconds")
            if state.plan:
                state.add_log(f"Budget spent: ${state.plan.budget_allocation.spent:.2f} / "
                            f"${state.plan.budget_allocation.total_budget:.2f}")

        return state

    def _adjust_generation_strategy(self, state: AgentState) -> None:
        """
        Adjust generation strategy based on previous iteration results

        This could involve:
        - Changing scaffold selection
        - Adjusting functional groups
        - Modifying generation parameters

        For now, just log that we're adjusting
        """
        state.add_log("Adjusting generation strategy for next iteration")
        # In production, analyze why molecules failed and adjust accordingly

    def _generate_final_report(self, state: AgentState) -> Dict[str, Any]:
        """
        Generate final report summarizing the run

        Args:
            state: Final agent state

        Returns:
            Report dictionary
        """
        passed_molecules = [m for m in state.molecules if m.status == MoleculeStatus.PASSED]
        monetized_molecules = [m for m in state.molecules if m.status == MoleculeStatus.MONETIZED]

        report = {
            'run_id': state.run_id,
            'status': state.phase.value,
            'success': state.phase == AgentPhase.COMPLETED,
            'goal': getattr(state, 'goal', None),
            'target': getattr(state, 'target', None),

            'execution_summary': {
                'iterations': state.current_iteration + 1,
                'total_molecules_generated': len(state.molecules),
                'molecules_passed': len(passed_molecules),
                'molecules_monetized': len(monetized_molecules),
            },

            'budget_summary': {
                'total_budget': state.plan.budget_allocation.total_budget if state.plan else 0,
                'spent': state.plan.budget_allocation.spent if state.plan else 0,
                'remaining': state.plan.budget_allocation.remaining if state.plan else 0,
                'transactions': len(state.transactions)
            },

            'top_molecules': [
                {
                    'id': m.id,
                    'name': m.name,
                    'smiles': m.smiles,
                    'toxicity_score': m.properties.toxicity_score,
                    'efficacy_score': m.properties.efficacy_score,
                    'composite_score': m.properties.additional_properties.get('composite_score'),
                    'cost': m.cost_incurred,
                    'visualization_url': m.visualization_url,
                    'listing_id': m.properties.additional_properties.get('listing_id'),
                    'listing_url': m.properties.additional_properties.get('listing_url'),
                }
                for m in passed_molecules[:3]  # Top 3
            ],

            'transactions': [
                {
                    'id': t.transaction_id,
                    'amount': t.amount,
                    'service': t.service,
                    'method': t.payment_method,
                    'status': t.status
                }
                for t in state.transactions
            ],

            'timing': {
                'start_time': state.start_time.isoformat(),
                'end_time': state.end_time.isoformat() if state.end_time else None,
                'duration_seconds': (state.end_time - state.start_time).total_seconds() if state.end_time else None
            }
        }

        # Add monetization results if available
        if state.final_results and 'monetization' in state.final_results:
            report['monetization'] = state.final_results['monetization']

        return report

    async def get_status(self, run_id: str) -> Optional[AgentResponse]:
        """
        Get current status of a running agent (for async monitoring)

        Args:
            run_id: Run ID to check

        Returns:
            Agent response with current status
        """
        # In production, this would check a state store (Redis, DB, etc.)
        # For now, this is a placeholder
        return None

    def create_response(self, state: AgentState) -> AgentResponse:
        """
        Create API response from agent state

        Args:
            state: Agent state

        Returns:
            Agent response
        """
        passed = len([m for m in state.molecules if m.status == MoleculeStatus.PASSED])

        return AgentResponse(
            run_id=state.run_id,
            status="success" if state.phase == AgentPhase.COMPLETED else "failed" if state.phase == AgentPhase.FAILED else "running",
            phase=state.phase,
            message=self._get_status_message(state),
            budget_remaining=state.plan.budget_allocation.remaining if state.plan else 0.0,
            molecules_generated=len(state.molecules),
            molecules_passed=passed,
            logs=state.logs[-20:],  # Last 20 log entries
            results=state.final_results
        )

    def _get_status_message(self, state: AgentState) -> str:
        """Get human-readable status message"""
        if state.phase == AgentPhase.COMPLETED:
            return f"Successfully completed! Found {len([m for m in state.molecules if m.status == MoleculeStatus.PASSED])} suitable molecule(s)."
        elif state.phase == AgentPhase.FAILED:
            return f"Failed: {state.error if state.error else 'No suitable molecules found'}"
        else:
            return f"Running: {state.phase.value}"
