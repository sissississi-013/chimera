"""
Molecule Generation Module - Creates candidate drug molecules using NVIDIA NIMs
"""
from typing import List, Optional
import random
import os
from .base import BaseModule
from ..models.agent_state import AgentState, AgentPhase
from ..models.molecule import Molecule, MoleculeStatus
from ..integrations.nvidia_nims import MolMIMClient, GenMolClient, NVIDIANIMError


class MoleculeGenerationModule(BaseModule):
    """
    Generates candidate molecules using NVIDIA NIMs:
    1. MolMIM: Property-optimized molecule generation
    2. GenMol: Fragment-based generation
    3. Fallback: Scaffold-based generation if APIs fail
    """

    # Seed molecules for MolMIM (known drug-like starting points)
    SEED_MOLECULES = [
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",  # Ibuprofen-like
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine-like
        "CC(=O)Oc1ccccc1C(=O)O",  # Aspirin-like
        "c1ccc2c(c1)ccc3c2cccc3",  # Anthracene scaffold
        "c1ccc2[nH]ccc2c1",  # Indole scaffold
    ]

    # Molecular fragments for GenMol
    DRUG_FRAGMENTS = [
        "c1ccccc1",  # Benzene
        "c1cnc[nH]1",  # Imidazole
        "C1CCCCC1",  # Cyclohexane
        "c1ccc2ccccc2c1",  # Naphthalene
        "C(=O)N",  # Amide
        "S(=O)(=O)N",  # Sulfonamide
    ]

    def __init__(self):
        super().__init__()
        self.use_real_apis = os.getenv('USE_REAL_APIS', 'true').lower() == 'true'

        # Initialize NVIDIA NIM clients
        try:
            self.molmim_client = MolMIMClient() if self.use_real_apis else None
            self.genmol_client = GenMolClient() if self.use_real_apis else None
        except NVIDIANIMError as e:
            self.molmim_client = None
            self.genmol_client = None
            print(f"⚠️  NVIDIA NIMs unavailable: {e}")

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
        Generate molecules using NVIDIA NIMs or fallback methods

        Args:
            count: Number of molecules to generate
            target: Optional target protein/disease
            state: Agent state for logging

        Returns:
            List of generated molecules
        """
        molecules = []

        # Strategy 1: Try MolMIM for property-optimized generation
        if self.molmim_client and count > 0:
            try:
                mol_batch_size = min(count, 20)  # Generate in batches
                seed = random.choice(self.SEED_MOLECULES)

                self.log(state, f"🧬 Using MolMIM to generate {mol_batch_size} molecules optimized for QED")

                result = self.molmim_client.generate_molecules(
                    seed_smiles=seed,
                    property_name="QED",  # Drug-likeness
                    num_molecules=mol_batch_size,
                    min_similarity=0.3,
                    minimize=False,  # Maximize QED
                    iterations=3
                )

                # Parse MolMIM results
                generated_mols = result.get('molecules', [])
                for i, mol_data in enumerate(generated_mols[:count]):
                    smiles = mol_data.get('smiles', mol_data.get('smi', ''))
                    if smiles:
                        molecule = Molecule(
                            id=f"mol_{len(molecules)+1:03d}",
                            smiles=smiles,
                            name=f"MolMIM_{len(molecules)+1}",
                            status=MoleculeStatus.GENERATED,
                            generation_method="nvidia_molmim"
                        )
                        molecules.append(molecule)

                self.log(state, f"✅ MolMIM generated {len(molecules)} molecules")

            except Exception as e:
                self.log(state, f"⚠️  MolMIM error: {str(e)}, trying GenMol...")

        # Strategy 2: Try GenMol for fragment-based generation
        if self.genmol_client and len(molecules) < count:
            try:
                remaining = count - len(molecules)
                fragments = random.sample(self.DRUG_FRAGMENTS, min(3, len(self.DRUG_FRAGMENTS)))

                self.log(state, f"🧬 Using GenMol to generate {remaining} molecules from fragments")

                result = self.genmol_client.generate_from_fragments(
                    fragments=fragments,
                    num_molecules=remaining,
                    temperature=1.0
                )

                # Parse GenMol results
                generated_mols = result.get('molecules', [])
                for i, mol_data in enumerate(generated_mols[:remaining]):
                    smiles = mol_data.get('smiles', mol_data.get('smi', ''))
                    if smiles:
                        molecule = Molecule(
                            id=f"mol_{len(molecules)+1:03d}",
                            smiles=smiles,
                            name=f"GenMol_{len(molecules)+1}",
                            status=MoleculeStatus.GENERATED,
                            generation_method="nvidia_genmol"
                        )
                        molecules.append(molecule)

                self.log(state, f"✅ GenMol generated {len(molecules) - len(generated_mols)} molecules")

            except Exception as e:
                self.log(state, f"⚠️  GenMol error: {str(e)}, using fallback generation...")

        # Strategy 3: Fallback to local generation if APIs failed or not enough molecules
        if len(molecules) < count:
            self.log(state, f"🔄 Generating remaining {count - len(molecules)} molecules locally")
            local_mols = await self._generate_local_molecules(count - len(molecules), state)
            molecules.extend(local_mols)

        return molecules

    async def _generate_local_molecules(self, count: int, state: AgentState) -> List[Molecule]:
        """
        Fallback local generation using simple scaffold-based approach

        Args:
            count: Number of molecules to generate
            state: Agent state for logging

        Returns:
            List of generated molecules
        """
        molecules = []

        # Fallback scaffolds (used when APIs are unavailable)
        FALLBACK_SCAFFOLDS = [
            "c1ccccc1",  # Benzene
            "c1ccc2ccccc2c1",  # Naphthalene
            "c1ccc2[nH]ccc2c1",  # Indole
            "c1cnc[nH]1",  # Imidazole
        ]

        FUNCTIONAL_GROUPS = ["C(=O)O", "C(=O)N", "N", "O", "F", "Cl"]

        for i in range(count):
            try:
                scaffold = random.choice(FALLBACK_SCAFFOLDS)
                groups = random.sample(FUNCTIONAL_GROUPS, random.randint(1, 2))
                smiles = self._combine_fragments(scaffold, groups)

                molecule = Molecule(
                    id=f"mol_{i+1:03d}",
                    smiles=smiles,
                    name=f"Local_{i+1}",
                    status=MoleculeStatus.GENERATED,
                    generation_method="local_scaffold"
                )
                molecules.append(molecule)

            except Exception as e:
                self.log(state, f"Error in local generation: {str(e)}")
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
