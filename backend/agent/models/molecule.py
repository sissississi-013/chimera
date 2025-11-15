"""
Molecule data models for Chimera agent
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class MoleculeStatus(str, Enum):
    """Status of molecule in the pipeline"""
    GENERATED = "generated"
    EVALUATING = "evaluating"
    PASSED = "passed"
    REJECTED = "rejected"
    MONETIZED = "monetized"


class MoleculeProperties(BaseModel):
    """Predicted/calculated properties of a molecule"""
    toxicity_score: Optional[float] = Field(None, description="Toxicity prediction (0-1, lower is better)")
    drug_likeness: Optional[float] = Field(None, description="Drug-likeness score")
    molecular_weight: Optional[float] = Field(None, description="Molecular weight in Daltons")
    logp: Optional[float] = Field(None, description="Partition coefficient")
    h_bond_donors: Optional[int] = Field(None, description="Number of H-bond donors")
    h_bond_acceptors: Optional[int] = Field(None, description="Number of H-bond acceptors")
    predicted_activity: Optional[str] = Field(None, description="Predicted biological activity")
    efficacy_score: Optional[float] = Field(None, description="Predicted efficacy (0-1)")
    additional_properties: Dict[str, Any] = Field(default_factory=dict)


class Molecule(BaseModel):
    """Represents a drug candidate molecule"""
    id: str = Field(..., description="Unique identifier for the molecule")
    smiles: str = Field(..., description="SMILES string representation")
    name: Optional[str] = Field(None, description="Human-readable name")
    status: MoleculeStatus = Field(MoleculeStatus.GENERATED)
    properties: MoleculeProperties = Field(default_factory=MoleculeProperties)
    generation_method: Optional[str] = Field(None, description="How this molecule was generated")
    evaluation_history: List[Dict[str, Any]] = Field(default_factory=list)
    cost_incurred: float = Field(0.0, description="Total cost spent evaluating this molecule")
    rejection_reason: Optional[str] = Field(None, description="Why molecule was rejected if applicable")
    visualization_url: Optional[str] = Field(None, description="URL to 2D/3D visualization")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "mol_001",
                "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
                "name": "Ibuprofen",
                "status": "passed",
                "properties": {
                    "toxicity_score": 0.15,
                    "molecular_weight": 206.28,
                    "drug_likeness": 0.85
                }
            }
        }


class MoleculeEvaluationRequest(BaseModel):
    """Request to evaluate a molecule"""
    smiles: str
    checks: List[str] = Field(default=["toxicity", "drug_likeness"], description="Which checks to run")
    max_cost: Optional[float] = Field(None, description="Maximum cost willing to pay for evaluation")


class MoleculeEvaluationResult(BaseModel):
    """Result of molecule evaluation"""
    molecule_id: str
    passed: bool
    properties: MoleculeProperties
    cost: float
    checks_performed: List[str]
    messages: List[str] = Field(default_factory=list)
