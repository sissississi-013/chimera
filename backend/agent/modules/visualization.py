"""
Visualization Module - Generates 2D/3D visualizations of molecules
"""
from typing import List, Optional
import base64
import io
from .base import BaseModule
from ..models.agent_state import AgentState, AgentPhase
from ..models.molecule import Molecule


class VisualizationModule(BaseModule):
    """
    The Visualization Module creates visual representations of molecules:
    1. 2D structure diagrams (using RDKit)
    2. 3D conformer models (optional)
    3. Property visualizations

    In production, this would use:
    - RDKit for molecule rendering
    - Matplotlib for property plots
    - py3Dmol or similar for 3D visualization

    For now, we'll create placeholder visualizations.
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.generate_3d = config.get('generate_3d', False) if config else False

    async def execute(self, state: AgentState) -> AgentState:
        """
        Generate visualizations for top molecules

        Args:
            state: Agent state with evaluated molecules

        Returns:
            State with visualization URLs/data added to molecules
        """
        self.log(state, "Starting visualization generation")
        state.phase = AgentPhase.VISUALIZING

        # Get molecules that passed evaluation
        passed_molecules = [m for m in state.molecules if m.status.value == "passed"]

        if not passed_molecules:
            self.log(state, "No molecules to visualize")
            return state

        # Generate visualizations for top candidates (limit to top 5 to save resources)
        top_molecules = passed_molecules[:5]
        self.log(state, f"Generating visualizations for {len(top_molecules)} molecules")

        for mol in top_molecules:
            # Generate 2D structure
            image_data = await self._generate_2d_structure(mol, state)
            mol.visualization_url = image_data

            # Generate 3D if requested
            if self.generate_3d:
                # 3D generation would go here
                pass

            self.log(state, f"Visualization complete for {mol.name}")

        return state

    async def _generate_2d_structure(self, mol: Molecule, state: AgentState) -> str:
        """
        Generate 2D molecular structure diagram using RDKit
        """
        try:
            # Try to use RDKit for real molecule visualization
            from rdkit import Chem
            from rdkit.Chem import Draw
            from PIL import Image

            # Parse SMILES
            mol_obj = Chem.MolFromSmiles(mol.smiles)

            if mol_obj is None:
                self.log(state, f"⚠️  Invalid SMILES for {mol.name}, using placeholder")
                return self._generate_placeholder_svg(mol)

            # Generate 2D coordinates
            from rdkit.Chem import AllChem
            AllChem.Compute2DCoords(mol_obj)

            # Draw molecule with high resolution (1200x1200) for crisp, clear images
            # Modern RDKit API with high-quality settings
            img = Draw.MolToImage(
                mol_obj,
                size=(1200, 1200),
                kekulize=True,
                wedgeBonds=True,
                fitImage=True
            )

            # Convert to base64 for embedding with high quality
            buffered = io.BytesIO()
            img.save(buffered, format="PNG", optimize=False)
            img_str = base64.b64encode(buffered.getvalue()).decode()

            self.log(state, f"✅ Generated RDKit visualization for {mol.name}")
            return f"data:image/png;base64,{img_str}"

        except ImportError:
            # RDKit not available, use placeholder
            self.log(state, "⚠️  RDKit not available, using placeholder visualization")
            return self._generate_placeholder_svg(mol)
        except Exception as e:
            self.log(state, f"⚠️  Visualization error for {mol.name}: {str(e)}")
            return self._generate_placeholder_svg(mol)

    def _generate_placeholder_svg(self, mol: Molecule) -> str:
        """Generate fallback SVG placeholder"""
        toxicity_text = f'Toxicity: {mol.properties.toxicity_score:.2f}' if mol.properties.toxicity_score is not None else 'Toxicity: N/A'
        efficacy_text = f'<text x="150" y="200" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">Efficacy: {mol.properties.efficacy_score:.2f}</text>' if mol.properties.efficacy_score is not None else ''

        svg = f'''
        <svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="300" height="300" fill="#f0f0f0"/>
            <text x="150" y="130" text-anchor="middle" font-family="Arial" font-size="14" fill="#333">
                Molecule: {mol.name}
            </text>
            <text x="150" y="150" text-anchor="middle" font-family="monospace" font-size="11" fill="#666">
                {mol.smiles[:40]}...
            </text>
            <text x="150" y="180" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">
                {toxicity_text}
            </text>
            {efficacy_text}
            <circle cx="150" cy="240" r="30" fill="#4CAF50" opacity="0.3"/>
            <text x="150" y="248" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">
                Drug-like
            </text>
        </svg>
        '''

        # Convert to base64 data URI
        svg_bytes = svg.encode('utf-8')
        svg_b64 = base64.b64encode(svg_bytes).decode('utf-8')

        return f"data:image/svg+xml;base64,{svg_b64}"

    async def generate_property_chart(self, molecules: List[Molecule]) -> str:
        """
        Generate a chart comparing molecule properties

        In production, use matplotlib:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        names = [m.name for m in molecules]
        tox = [m.properties.toxicity_score for m in molecules]
        ax.bar(names, tox)
        ...
        """
        # For now, return a placeholder
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2YwZjBmMCIvPjx0ZXh0IHg9IjIwMCIgeT0iMTUwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiPk1vbGVjdWxlIFByb3BlcnR5IENoYXJ0PC90ZXh0Pjwvc3ZnPg=="

    async def can_execute(self, state: AgentState) -> bool:
        """Check if we can visualize"""
        return state.phase == AgentPhase.EVALUATING and len([m for m in state.molecules if m.status.value == "passed"]) > 0

    def get_required_budget(self, state: AgentState) -> float:
        """Visualization is mostly free (local)"""
        if state.plan:
            return state.plan.budget_allocation.visualization_budget
        return 0.0
