"""
Planning Module - Creates execution strategy and budget allocation
"""
from typing import Dict, Any
from .base import BaseModule
from ..models.agent_state import AgentState, ExecutionPlan, BudgetAllocation, AgentPhase


class PlanningModule(BaseModule):
    """
    The Planning Module analyzes the goal and creates a detailed execution plan.
    It determines:
    - How many molecules to generate
    - Which evaluation criteria to apply
    - Budget allocation across tasks
    - Success criteria and thresholds
    """

    async def execute(self, state: AgentState) -> AgentState:
        """
        Create an execution plan based on the goal and constraints

        Args:
            state: Current agent state with goal and budget

        Returns:
            Updated state with execution plan
        """
        self.log(state, "Starting planning phase")
        state.phase = AgentPhase.PLANNING

        # Extract goal and constraints from state
        # In practice, these would come from the AgentRequest
        goal = getattr(state, 'goal', 'Generate safe drug candidates')
        budget = getattr(state, 'total_budget', 5.0)
        constraints = getattr(state, 'constraints', {})

        # Analyze goal to determine strategy
        self.log(state, f"Goal: {goal}")
        self.log(state, f"Total budget: ${budget:.2f}")

        # Create budget allocation
        budget_allocation = self._allocate_budget(budget, constraints)

        # Determine evaluation criteria
        eval_criteria = self._determine_criteria(goal, constraints)

        # Determine number of molecules to generate
        num_molecules = self._determine_molecule_count(budget_allocation, constraints)

        # Create execution steps
        steps = self._create_execution_steps(num_molecules, eval_criteria)

        # Create the execution plan
        plan = ExecutionPlan(
            goal=goal,
            target=constraints.get('target'),
            num_molecules_to_generate=num_molecules,
            evaluation_criteria=eval_criteria,
            budget_allocation=budget_allocation,
            steps=steps,
            max_iterations=constraints.get('max_iterations', 2),
            success_criteria=constraints.get('success_criteria',
                                            'At least one molecule passes all safety and efficacy checks')
        )

        state.plan = plan
        self.log(state, f"Plan created: Generate {num_molecules} molecules")
        self.log(state, f"Budget allocation: Gen=${budget_allocation.generation_budget:.2f}, "
                       f"Eval=${budget_allocation.evaluation_budget:.2f}, "
                       f"Viz=${budget_allocation.visualization_budget:.2f}, "
                       f"Mon=${budget_allocation.monetization_budget:.2f}")

        return state

    def _allocate_budget(self, total_budget: float, constraints: Dict[str, Any]) -> BudgetAllocation:
        """
        Allocate budget across different tasks

        Strategy:
        - 5% for generation (mostly free with local methods)
        - 60% for evaluation (most expensive part - toxicity and efficacy APIs)
        - 5% for visualization (mostly free with RDKit)
        - 20% for monetization/data sharing
        - 10% reserve for unexpected needs or retries
        """
        return BudgetAllocation(
            total_budget=total_budget,
            generation_budget=total_budget * 0.05,
            evaluation_budget=total_budget * 0.60,
            visualization_budget=total_budget * 0.05,
            monetization_budget=total_budget * 0.20,
            reserve_budget=total_budget * 0.10,
            spent=0.0
        )

    def _determine_criteria(self, goal: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine evaluation criteria based on goal and constraints
        """
        criteria = {
            # Default safety thresholds
            'max_toxicity': constraints.get('max_toxicity', 0.5),
            'min_drug_likeness': constraints.get('min_drug_likeness', 0.6),

            # Lipinski's Rule of Five parameters
            'max_molecular_weight': constraints.get('max_molecular_weight', 500),
            'max_logp': constraints.get('max_logp', 5),
            'max_h_donors': constraints.get('max_h_donors', 5),
            'max_h_acceptors': constraints.get('max_h_acceptors', 10),

            # Efficacy (if applicable)
            'min_efficacy_score': constraints.get('min_efficacy_score', 0.5),

            # Cost controls
            'max_cost_per_molecule': constraints.get('max_cost_per_molecule', 1.0),
        }

        return criteria

    def _determine_molecule_count(self, budget: BudgetAllocation,
                                  constraints: Dict[str, Any]) -> int:
        """
        Determine how many molecules to generate based on budget

        If we have limited eval budget and each toxicity check costs ~$0.05,
        we can afford to check fewer molecules. Balance quantity vs quality.
        """
        # Default
        count = constraints.get('num_molecules', 10)

        # Adjust based on evaluation budget
        # Assume each molecule costs ~$0.10 to evaluate on average
        avg_eval_cost = 0.10
        affordable_count = int(budget.evaluation_budget / avg_eval_cost)

        # Use the minimum of requested and affordable
        count = min(count, affordable_count, 20)  # Cap at 20 to avoid too many

        return max(count, 3)  # At least 3 molecules

    def _create_execution_steps(self, num_molecules: int,
                                criteria: Dict[str, Any]) -> list:
        """
        Create ordered list of execution steps
        """
        steps = [
            {
                "step": 1,
                "module": "generation",
                "action": f"Generate {num_molecules} candidate molecules",
                "description": "Use algorithmic methods or AI to create novel molecular structures"
            },
            {
                "step": 2,
                "module": "evaluation",
                "action": "Run basic filters (Lipinski's rules, known toxic substructures)",
                "description": "Quick local checks to eliminate obviously unsuitable candidates",
                "cost": "free"
            },
            {
                "step": 3,
                "module": "evaluation",
                "action": "Predict toxicity for remaining molecules",
                "description": "Call toxicity prediction API (paid)",
                "cost": "~$0.05 per molecule"
            },
            {
                "step": 4,
                "module": "evaluation",
                "action": "Apply evaluation criteria and filter",
                "description": f"Keep only molecules meeting criteria (toxicity < {criteria['max_toxicity']})",
                "cost": "free"
            },
            {
                "step": 5,
                "module": "evaluation",
                "action": "Predict efficacy for passing molecules (if applicable)",
                "description": "Estimate biological activity",
                "cost": "~$0.10 per molecule",
                "optional": True
            },
            {
                "step": 6,
                "module": "evaluation",
                "action": "Select top candidate(s)",
                "description": "Rank and choose best molecule(s) to move forward",
                "cost": "free"
            },
            {
                "step": 7,
                "module": "visualization",
                "action": "Generate 2D/3D visualizations",
                "description": "Create images of final candidates",
                "cost": "free (using RDKit)"
            },
            {
                "step": 8,
                "module": "monetization",
                "action": "Upload to data marketplace",
                "description": "Share/sell the discovered molecule data",
                "cost": "~$0.20 listing fee (simulated)"
            }
        ]

        return steps
