"""
NVIDIA NIM Integrations for Chimera
Supports: MolMIM, GenMol, AlphaFold2, DiffDock, Evo2
"""
import os
import requests
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class NVIDIANIMError(Exception):
    """Base exception for NVIDIA NIM API errors"""
    pass


class MolMIMClient:
    """Client for NVIDIA MolMIM - Guided Molecule Generation"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('MOLMIM_API_KEY')
        self.base_url = os.getenv('MOLMIM_API_URL', 'https://health.api.nvidia.com/v1/biology/nvidia/molmim/generate')

        if not self.api_key:
            raise NVIDIANIMError("MOLMIM_API_KEY not found in environment")

    def generate_molecules(
        self,
        seed_smiles: str,
        property_name: str = "QED",
        num_molecules: int = 10,
        min_similarity: float = 0.3,
        minimize: bool = False,
        algorithm: str = "CMA-ES",
        particles: int = 20,
        iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Generate molecules optimized for a specific property

        Args:
            seed_smiles: Starting SMILES string
            property_name: Property to optimize (QED, SAS, LogP, etc.)
            num_molecules: Number of molecules to generate
            min_similarity: Minimum Tanimoto similarity to seed
            minimize: Whether to minimize (False = maximize)
            algorithm: Optimization algorithm (CMA-ES, PSO, etc.)
            particles: Number of particles for optimization
            iterations: Number of optimization iterations

        Returns:
            Dict with generated molecules and properties
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'smi': seed_smiles,
            'algorithm': algorithm,
            'num_molecules': num_molecules,
            'property_name': property_name,
            'minimize': minimize,
            'min_similarity': min_similarity,
            'particles': particles,
            'iterations': iterations
        }

        logger.info(f"🧬 MolMIM: Generating {num_molecules} molecules optimized for {property_name}")

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=300  # 5 minute timeout for generation
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ MolMIM: Generated {len(result.get('molecules', []))} molecules")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ MolMIM API error: {str(e)}")
            raise NVIDIANIMError(f"MolMIM generation failed: {str(e)}")


class GenMolClient:
    """Client for NVIDIA GenMol - Fragment-based Molecule Generation"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GENMOL_API_KEY')
        self.base_url = os.getenv('GENMOL_API_URL', 'https://health.api.nvidia.com/v1/biology/nvidia/genmol/generate')

        if not self.api_key:
            raise NVIDIANIMError("GENMOL_API_KEY not found in environment")

    def generate_from_fragments(
        self,
        fragments: List[str],
        num_molecules: int = 10,
        temperature: float = 1.0,
        top_k: int = 50
    ) -> Dict[str, Any]:
        """
        Generate molecules from molecular fragments

        Args:
            fragments: List of fragment SMILES
            num_molecules: Number of molecules to generate
            temperature: Sampling temperature (higher = more diversity)
            top_k: Top-k sampling parameter

        Returns:
            Dict with generated molecules
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'fragments': fragments,
            'num_molecules': num_molecules,
            'temperature': temperature,
            'top_k': top_k
        }

        logger.info(f"🧬 GenMol: Generating {num_molecules} molecules from {len(fragments)} fragments")

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ GenMol: Generated {len(result.get('molecules', []))} molecules")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ GenMol API error: {str(e)}")
            raise NVIDIANIMError(f"GenMol generation failed: {str(e)}")


class AlphaFold2Client:
    """Client for NVIDIA AlphaFold2 - Protein Structure Prediction"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ALPHAFOLD2_API_KEY')
        self.base_url = os.getenv('ALPHAFOLD2_API_URL', 'https://health.api.nvidia.com/v1/biology/alphafold2/predict')

        if not self.api_key:
            raise NVIDIANIMError("ALPHAFOLD2_API_KEY not found in environment")

    def predict_structure(
        self,
        sequence: str,
        relax_prediction: bool = False,
        databases: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Predict 3D protein structure from amino acid sequence

        Args:
            sequence: Amino acid sequence (single letter codes)
            relax_prediction: Whether to relax the structure
            databases: Databases for MSA (default: ['small_bfd'])

        Returns:
            Dict with PDB structure and confidence metrics
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'sequence': sequence,
            'relax_prediction': relax_prediction,
            'databases': databases or ['small_bfd'],
            'algorithm': 'mmseqs2',
            'e_value': 0.000001
        }

        logger.info(f"🧬 AlphaFold2: Predicting structure for {len(sequence)} residue sequence")

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=600  # 10 minute timeout for structure prediction
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ AlphaFold2: Structure predicted successfully")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ AlphaFold2 API error: {str(e)}")
            raise NVIDIANIMError(f"AlphaFold2 prediction failed: {str(e)}")


class DiffDockClient:
    """Client for NVIDIA DiffDock - Protein-Ligand Docking"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('DIFFDOCK_API_KEY')
        self.base_url = os.getenv('DIFFDOCK_API_URL', 'https://health.api.nvidia.com/v1/biology/diffdock/dock')

        if not self.api_key:
            raise NVIDIANIMError("DIFFDOCK_API_KEY not found in environment")

    def dock_ligand(
        self,
        protein_pdb: str,
        ligand_smiles: str,
        num_poses: int = 10
    ) -> Dict[str, Any]:
        """
        Dock a ligand to a protein target

        Args:
            protein_pdb: PDB structure of protein
            ligand_smiles: SMILES string of ligand
            num_poses: Number of binding poses to generate

        Returns:
            Dict with docking poses and binding scores
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'protein': protein_pdb,
            'ligand': ligand_smiles,
            'num_poses': num_poses
        }

        logger.info(f"🧬 DiffDock: Docking ligand {ligand_smiles[:20]}... with {num_poses} poses")

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=600  # 10 minute timeout for docking
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ DiffDock: Docking completed with {len(result.get('poses', []))} poses")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ DiffDock API error: {str(e)}")
            raise NVIDIANIMError(f"DiffDock docking failed: {str(e)}")


class NVIDIANIMOrchestrator:
    """Orchestrator for all NVIDIA NIM services"""

    def __init__(self):
        self.molmim = None
        self.genmol = None
        self.alphafold2 = None
        self.diffdock = None

        # Initialize clients only if API keys are available
        try:
            self.molmim = MolMIMClient()
        except NVIDIANIMError as e:
            logger.warning(f"MolMIM not available: {e}")

        try:
            self.genmol = GenMolClient()
        except NVIDIANIMError as e:
            logger.warning(f"GenMol not available: {e}")

        try:
            self.alphafold2 = AlphaFold2Client()
        except NVIDIANIMError as e:
            logger.warning(f"AlphaFold2 not available: {e}")

        try:
            self.diffdock = DiffDockClient()
        except NVIDIANIMError as e:
            logger.warning(f"DiffDock not available: {e}")

    def get_available_services(self) -> List[str]:
        """Get list of available NVIDIA NIM services"""
        services = []
        if self.molmim:
            services.append('molmim')
        if self.genmol:
            services.append('genmol')
        if self.alphafold2:
            services.append('alphafold2')
        if self.diffdock:
            services.append('diffdock')
        return services
