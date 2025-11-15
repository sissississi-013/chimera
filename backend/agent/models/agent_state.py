"""
Agent state and execution models
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class AgentPhase(str, Enum):
    """Current phase of agent execution"""
    PLANNING = "planning"
    GENERATING = "generating"
    EVALUATING = "evaluating"
    VISUALIZING = "visualizing"
    MONETIZING = "monetizing"
    COMPLETED = "completed"
    FAILED = "failed"


class BudgetAllocation(BaseModel):
    """Budget allocation across different tasks"""
    total_budget: float = Field(..., description="Total available budget in USD")
    generation_budget: float = Field(0.0, description="Budget for molecule generation")
    evaluation_budget: float = Field(0.0, description="Budget for evaluation APIs")
    visualization_budget: float = Field(0.0, description="Budget for visualization")
    monetization_budget: float = Field(0.0, description="Budget for data sharing/upload")
    reserve_budget: float = Field(0.0, description="Reserve for unexpected needs")
    spent: float = Field(0.0, description="Amount spent so far")

    @property
    def remaining(self) -> float:
        """Calculate remaining budget"""
        return self.total_budget - self.spent

    def can_spend(self, amount: float) -> bool:
        """Check if we can afford to spend this amount"""
        return self.remaining >= amount

    def record_spend(self, amount: float, category: str) -> None:
        """Record a spending transaction"""
        self.spent += amount


class ExecutionPlan(BaseModel):
    """High-level execution plan created by Planning Module"""
    goal: str = Field(..., description="High-level goal for drug discovery")
    target: Optional[str] = Field(None, description="Target protein/disease if specified")
    num_molecules_to_generate: int = Field(10, description="Number of molecules to generate")
    evaluation_criteria: Dict[str, Any] = Field(default_factory=dict)
    budget_allocation: BudgetAllocation
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="Ordered list of execution steps")
    max_iterations: int = Field(2, description="Maximum generation/evaluation loops")
    success_criteria: str = Field("At least one molecule passes all filters")
    created_at: datetime = Field(default_factory=datetime.now)


class PaymentTransaction(BaseModel):
    """Record of a payment transaction"""
    transaction_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    amount: float
    currency: str = Field("USD")
    payment_method: str = Field(..., description="x402, stripe, etc.")
    service: str = Field(..., description="What service was paid for")
    status: str = Field("pending", description="pending, completed, failed")
    details: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    """Complete state of the autonomous agent"""
    run_id: str = Field(..., description="Unique ID for this execution run")
    phase: AgentPhase = Field(AgentPhase.PLANNING)
    plan: Optional[ExecutionPlan] = None
    molecules: List[Any] = Field(default_factory=list)  # List of Molecule objects
    transactions: List[PaymentTransaction] = Field(default_factory=list)
    current_iteration: int = Field(0)
    logs: List[str] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    final_results: Optional[Dict[str, Any]] = None
    error: Optional[str] = Field(None, description="Error message if failed")

    # Request fields (set from AgentRequest)
    goal: str = Field(default="", description="Drug discovery goal")
    target: Optional[str] = Field(None, description="Target protein/disease")
    total_budget: float = Field(5.0, description="Total budget in USD")
    constraints: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}

    def add_log(self, message: str) -> None:
        """Add a log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")

    def add_transaction(self, transaction: PaymentTransaction) -> None:
        """Record a payment transaction"""
        self.transactions.append(transaction)
        if self.plan:
            self.plan.budget_allocation.record_spend(transaction.amount, transaction.service)


class AgentRequest(BaseModel):
    """Request to start the autonomous agent"""
    goal: str = Field(..., description="What drug discovery task to accomplish")
    target: Optional[str] = Field(None, description="Target protein, enzyme, or disease")
    budget: float = Field(5.0, description="Total budget in USD")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Additional constraints")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration overrides")

    class Config:
        json_schema_extra = {
            "example": {
                "goal": "Find a novel molecule to inhibit EGFR kinase",
                "target": "EGFR",
                "budget": 5.0,
                "constraints": {
                    "max_toxicity": 0.5,
                    "min_drug_likeness": 0.6
                }
            }
        }


class AgentResponse(BaseModel):
    """Response from the agent"""
    run_id: str
    status: str
    phase: AgentPhase
    message: str
    budget_remaining: float
    molecules_generated: int
    molecules_passed: int
    logs: List[str]
    results: Optional[Dict[str, Any]] = None
