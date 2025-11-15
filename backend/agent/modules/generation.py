"""
Molecule Generation Module - Creates candidate drug molecules
"""
from typing import List, Optional
import random
from .base import BaseModule
from ..models.agent_state import AgentState, AgentPhase
from ..models.molecule import Molecule, MoleculeStatus


class MoleculeGenerationModule(BaseModule):
    """
    Generates candidate molecules using various strategies:
    1. Scaffold-based: Start with known drug scaffolds and modify
    2. Random generation: Create random drug-like molecules
    3. AI-based: Use ML models (future enhancement)

    For now, we'll use a combination of known scaffolds and modifications.
    """

    # Common drug scaffolds (SMILES)
    DRUG_SCAFFOLDS = [
        "c1ccccc1",  # Benzene ring
        "C1CCCCC1",  # Cyclohexane
        "c1ccc2ccccc2c1",  # Naphthalene
        "c1cnc2ccccc2c1",  # Quinoline
        "c1ccc2c(c1)ccc1ccccc21",  # Anthracene
        "C1CCC2=C(C1)C=CC=C2",  # Tetralin
        "c1ccc2[nH]ccc2c1",  # Indole
        "c1cnc[nH]1",  # Imidazole
    ]

    # Functional groups to add (SMILES fragments)
    FUNCTIONAL_GROUPS = [
        "C(=O)O",  # Carboxylic acid
        "C(=O)N",  # Amide
        "N",  # Amine
        "O",  # Hydroxyl
        "C(=O)C",  # Ketone
        "S(=O)(=O)N",  # Sulfonamide
        "F",  # Fluoro
        "Cl",  # Chloro
        "CF3",  # Trifluoromethyl
        "OC",  # Methoxy
    ]

    async def execute(self, state: AgentState) -> AgentState:
        """
        Generate candidate molecules

        Args:
            state: Agent state with execution plan

        Returns:
            State with generated molecules
        """
        self.log(state, "Starting molecule generation")
        state.phase = AgentPhase.GENERATING

        if not state.plan:
            self.log(state, "ERROR: No execution plan found!")
            return state

        num_to_generate = state.plan.num_molecules_to_generate
        target = state.plan.target

        self.log(state, f"Generating {num_to_generate} candidate molecules")
        if target:
            self.log(state, f"Target: {target}")

        # Generate molecules
        molecules = await self._generate_molecules(num_to_generate, target, state)

        # Perform basic validation
        valid_molecules = self._basic_validation(molecules, state)

        state.molecules = valid_molecules
        self.log(state, f"Generated {len(valid_molecules)} valid molecules (from {len(molecules)} candidates)")

        return state

    async def _generate_molecules(self, count: int, target: Optional[str],
                                  state: AgentState) -> List[Molecule]:
        """
        Generate molecules using scaffold-based approach

        Args:
            count: Number of molecules to generate
            target: Optional target protein/disease
            state: Agent state for logging

        Returns:
            List of generated molecules
        """
        molecules = []

        for i in range(count):
            try:
                # Select a random scaffold
                scaffold = random.choice(self.DRUG_SCAFFOLDS)

                # Add 1-3 functional groups
                num_groups = random.randint(1, 3)
                modifications = random.sample(self.FUNCTIONAL_GROUPS, num_groups)

                # For now, simple concatenation (in real implementation, would use RDKit properly)
                # This is a simplified approach; real chemistry would be more sophisticated
                smiles = self._combine_fragments(scaffold, modifications)

                # Create molecule object
                molecule = Molecule(
                    id=f"mol_{i+1:03d}",
                    smiles=smiles,
                    name=f"Candidate_{i+1}",
                    status=MoleculeStatus.GENERATED,
                    generation_method="scaffold_based_random"
                )

                molecules.append(molecule)

            except Exception as e:
                self.log(state, f"Error generating molecule {i+1}: {str(e)}")
                continue

        return molecules

    def _combine_fragments(self, scaffold: str, groups: List[str]) -> str:
        """
        Combine scaffold and functional groups into a SMILES string

        Note: This is a simplified implementation. In production, we would:
        1. Parse scaffold with RDKit
        2. Find attachment points
        3. Properly attach functional groups
        4. Validate the resulting molecule
        5. Generate canonical SMILES

        For demonstration, we'll create plausible SMILES strings.
        """
        # Simple concatenation for demo (not chemically rigorous)
        smiles = scaffold

        # Add some alkyl spacers and functional groups
        for group in groups:
            if random.random() > 0.5:
                smiles += "C" * random.randint(0, 2)  # Alkyl spacer
            smiles += group

        return smiles

    def _basic_validation(self, molecules: List[Molecule],
                         state: AgentState) -> List[Molecule]:
        """
        Perform basic validation on generated molecules

        - Remove duplicates
        - Check SMILES validity (would use RDKit)
        - Basic drug-likeness quick checks

        Args:
            molecules: Generated molecules
            state: Agent state for logging

        Returns:
            Valid molecules
        """
        valid = []
        seen_smiles = set()

        for mol in molecules:
            # Remove duplicates
            if mol.smiles in seen_smiles:
                self.log(state, f"Duplicate molecule {mol.id}, skipping")
                continue

            # Basic checks (in production, would use RDKit for proper validation)
            if not self._is_plausible_smiles(mol.smiles):
                self.log(state, f"Invalid SMILES for {mol.id}, skipping")
                continue

            seen_smiles.add(mol.smiles)
            valid.append(mol)

        return valid

    def _is_plausible_smiles(self, smiles: str) -> bool:
        """
        Quick plausibility check for SMILES
        In production, would use RDKit: Chem.MolFromSmiles(smiles) is not None

        Args:
            smiles: SMILES string

        Returns:
            True if plausible, False otherwise
        """
        # Basic checks
        if not smiles or len(smiles) < 3:
            return False

        if len(smiles) > 200:  # Too large
            return False

        # Check for balanced parentheses
        if smiles.count('(') != smiles.count(')'):
            return False

        if smiles.count('[') != smiles.count(']'):
            return False

        return True

    async def can_execute(self, state: AgentState) -> bool:
        """Check if we can generate molecules"""
        return state.plan is not None and state.phase == AgentPhase.PLANNING

    def get_required_budget(self, state: AgentState) -> float:
        """Generation is mostly free (local computation)"""
        if state.plan:
            return state.plan.budget_allocation.generation_budget
        return 0.0
