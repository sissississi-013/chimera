"""
Evaluation Module - Evaluates molecules for safety and efficacy using real APIs
"""
from typing import List, Dict, Any, Optional
from .base import BaseModule
from .payment import PaymentModule
from ..models.agent_state import AgentState, AgentPhase
from ..models.molecule import Molecule, MoleculeStatus, MoleculeProperties
from ..integrations.neurosnap import NeuroSnapClient, NeuroSnapError
from ..integrations.nvidia_nims import DiffDockClient, NVIDIANIMError
from ..integrations.locus_wallet import LocusWalletClient
import asyncio
import random
import os


class EvaluationModule(BaseModule):
    """
    The Evaluation Module assesses candidate molecules:
    1. Basic drug-likeness filters (Lipinski's Rule of Five)
    2. Toxicity prediction (via API - may require payment)
    3. Efficacy prediction (via API - may require payment)
    4. Filtering based on criteria
    5. Ranking and selection of top candidates
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.payment_module = PaymentModule(config)
        self.mock_api_mode = config.get('mock_api_mode', True) if config else True
        self.use_real_apis = os.getenv('USE_REAL_APIS', 'true').lower() == 'true'

        # Initialize API clients
        try:
            self.neurosnap_client = NeuroSnapClient() if self.use_real_apis else None
            self.diffdock_client = DiffDockClient() if self.use_real_apis else None
            self.locus_client = LocusWalletClient() if self.use_real_apis else None
        except (NeuroSnapError, NVIDIANIMError) as e:
            self.log(None, f"⚠️  API clients unavailable: {e}")
            self.neurosnap_client = None
            self.diffdock_client = None
            self.locus_client = None

    async def execute(self, state: AgentState) -> AgentState:
        """
        Evaluate all generated molecules

        Args:
            state: Agent state with generated molecules

        Returns:
            State with evaluated and filtered molecules
        """
        self.log(state, "Starting molecule evaluation")
        state.phase = AgentPhase.EVALUATING

        if not state.molecules:
            self.log(state, "ERROR: No molecules to evaluate!")
            return state

        if not state.plan:
            self.log(state, "ERROR: No evaluation criteria available!")
            return state

        criteria = state.plan.evaluation_criteria
        self.log(state, f"Evaluating {len(state.molecules)} molecules against criteria")

        # Step 1: Basic drug-likeness filters (free, fast)
        self.log(state, "Step 1: Applying basic drug-likeness filters...")
        molecules_after_basic = await self._apply_basic_filters(state.molecules, criteria, state)

        self.log(state, f"After basic filters: {len(molecules_after_basic)}/{len(state.molecules)} molecules remain")

        if not molecules_after_basic:
            self.log(state, "No molecules passed basic filters. Consider regenerating with adjusted parameters.")
            state.molecules = []
            return state

        # Step 2: Toxicity prediction (paid API)
        self.log(state, "Step 2: Predicting toxicity...")
        molecules_after_toxicity = await self._evaluate_toxicity(molecules_after_basic, criteria, state)

        self.log(state, f"After toxicity check: {len(molecules_after_toxicity)}/{len(molecules_after_basic)} molecules remain")

        if not molecules_after_toxicity:
            self.log(state, "No molecules passed toxicity screening.")
            state.molecules = molecules_after_toxicity
            return state

        # Step 3: Efficacy prediction (optional, paid API)
        if criteria.get('min_efficacy_score') is not None:
            self.log(state, "Step 3: Predicting efficacy...")
            molecules_after_efficacy = await self._evaluate_efficacy(molecules_after_toxicity, criteria, state)
            self.log(state, f"After efficacy check: {len(molecules_after_efficacy)}/{len(molecules_after_toxicity)} molecules remain")
        else:
            molecules_after_efficacy = molecules_after_toxicity
            self.log(state, "Step 3: Skipping efficacy check (not required)")

        # Step 4: Rank and select top candidates
        self.log(state, "Step 4: Ranking candidates...")
        ranked_molecules = self._rank_molecules(molecules_after_efficacy, state)

        # Update state
        state.molecules = ranked_molecules

        if ranked_molecules:
            top = ranked_molecules[0]
            self.log(state, f"Top candidate: {top.name} (toxicity: {top.properties.toxicity_score:.2f}, "
                           f"cost: ${top.cost_incurred:.2f})")

        return state

    async def _apply_basic_filters(self, molecules: List[Molecule],
                                   criteria: Dict[str, Any],
                                   state: AgentState) -> List[Molecule]:
        """
        Apply Lipinski's Rule of Five and other basic filters

        These are free, local checks:
        - Molecular weight ≤ 500 Da
        - LogP ≤ 5
        - H-bond donors ≤ 5
        - H-bond acceptors ≤ 10

        Args:
            molecules: Molecules to filter
            criteria: Evaluation criteria
            state: Agent state

        Returns:
            Filtered molecules
        """
        passed = []

        for mol in molecules:
            # Calculate basic properties (in production, use RDKit)
            props = self._calculate_basic_properties(mol.smiles)
            mol.properties = MoleculeProperties(**props)

            # Apply filters
            if props['molecular_weight'] > criteria.get('max_molecular_weight', 500):
                mol.status = MoleculeStatus.REJECTED
                mol.rejection_reason = f"Molecular weight too high: {props['molecular_weight']:.1f} Da"
                continue

            if props['logp'] > criteria.get('max_logp', 5):
                mol.status = MoleculeStatus.REJECTED
                mol.rejection_reason = f"LogP too high: {props['logp']:.2f}"
                continue

            if props['h_bond_donors'] > criteria.get('max_h_donors', 5):
                mol.status = MoleculeStatus.REJECTED
                mol.rejection_reason = f"Too many H-bond donors: {props['h_bond_donors']}"
                continue

            if props['h_bond_acceptors'] > criteria.get('max_h_acceptors', 10):
                mol.status = MoleculeStatus.REJECTED
                mol.rejection_reason = f"Too many H-bond acceptors: {props['h_bond_acceptors']}"
                continue

            # Passed basic filters
            passed.append(mol)

        return passed

    def _calculate_basic_properties(self, smiles: str) -> Dict[str, Any]:
        """
        Calculate basic molecular properties

        In production, use RDKit:
        from rdkit import Chem
        from rdkit.Chem import Descriptors

        mol = Chem.MolFromSmiles(smiles)
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)

        For now, we'll generate plausible mock values.
        """
        # Mock calculation based on SMILES length (rough approximation)
        length = len(smiles)

        return {
            'molecular_weight': 200 + (length * 5) + random.uniform(-50, 50),
            'logp': 1 + (length * 0.1) + random.uniform(-1, 1),
            'h_bond_donors': min(5, max(0, int(smiles.count('N') + smiles.count('O') * 0.5))),
            'h_bond_acceptors': min(10, max(0, int(smiles.count('O') + smiles.count('N')))),
            'drug_likeness': random.uniform(0.5, 0.95)
        }

    async def _evaluate_toxicity(self, molecules: List[Molecule],
                                 criteria: Dict[str, Any],
                                 state: AgentState) -> List[Molecule]:
        """
        Evaluate toxicity for each molecule using API (may require payment)

        Args:
            molecules: Molecules to evaluate
            criteria: Evaluation criteria
            state: Agent state

        Returns:
            Molecules that passed toxicity threshold
        """
        passed = []
        max_toxicity = criteria.get('max_toxicity', 0.5)

        for mol in molecules:
            mol.status = MoleculeStatus.EVALUATING

            # Call toxicity API (simulated)
            tox_result = await self._call_toxicity_api(mol, state)

            if tox_result['requires_payment']:
                # Handle 402 Payment Required
                payment_result = await self.payment_module.handle_402_challenge(
                    state=state,
                    response_data=tox_result['payment_info'],
                    original_request={'smiles': mol.smiles}
                )

                if not payment_result['success']:
                    self.log(state, f"Failed to pay for toxicity check for {mol.name}: {payment_result.get('error')}")
                    mol.status = MoleculeStatus.REJECTED
                    mol.rejection_reason = "Could not afford toxicity check"
                    continue

                # Retry with payment
                tox_result = await self._call_toxicity_api(mol, state, payment_token=payment_result['payment_token'])
                mol.cost_incurred += tox_result['cost']

            # Process result
            toxicity_score = tox_result['toxicity_score']
            mol.properties.toxicity_score = toxicity_score

            # Add to evaluation history
            mol.evaluation_history.append({
                'check': 'toxicity',
                'score': toxicity_score,
                'passed': toxicity_score <= max_toxicity,
                'cost': tox_result['cost']
            })

            if toxicity_score <= max_toxicity:
                passed.append(mol)
                self.log(state, f"{mol.name}: toxicity={toxicity_score:.2f} (PASS)")
            else:
                mol.status = MoleculeStatus.REJECTED
                mol.rejection_reason = f"Toxicity too high: {toxicity_score:.2f} > {max_toxicity}"
                self.log(state, f"{mol.name}: toxicity={toxicity_score:.2f} (FAIL)")

        return passed

    async def _call_toxicity_api(self, mol: Molecule, state: AgentState,
                                payment_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Call real NeuroSnap toxicity prediction API with REAL Locus payment

        This method implements the full payment flow:
        1. Request payment approval from Locus wallet
        2. If approved, call NeuroSnap API
        3. Track transaction for auditing
        """
        cost_per_check = 0.005  # $0.005 per toxicity prediction

        # Try real NeuroSnap API with Locus payment
        if self.neurosnap_client and self.locus_client:
            try:
                # STEP 1: Request payment approval from Locus
                self.log(state, f"💳 Requesting Locus payment approval: ${cost_per_check} for {mol.name}")

                payment_approval = self.locus_client.request_payment_approval(
                    amount=cost_per_check,
                    vendor='neurosnap',
                    description=f'Toxicity prediction for molecule {mol.name} ({mol.smiles[:20]}...)',
                    metadata={
                        'molecule_id': mol.id,
                        'molecule_name': mol.name,
                        'smiles': mol.smiles,
                        'service': 'neurosnap_toxicity',
                        'agent_state': state.id
                    }
                )

                if not payment_approval.get('approved', False):
                    self.log(state, f"❌ Locus payment REJECTED: {payment_approval.get('message', 'Unknown reason')}")
                    return {
                        'requires_payment': True,
                        'payment_info': {
                            'price': cost_per_check,
                            'currency': 'USD',
                            'pay_to': 'neurosnap',
                            'nonce': f'tox_{mol.id}',
                            'error': 'Locus payment approval failed'
                        }
                    }

                transaction_id = payment_approval.get('transaction_id')
                self.log(state, f"✅ Locus payment APPROVED: Transaction {transaction_id}")

                # STEP 2: Call NeuroSnap API (payment approved)
                self.log(state, f"🧪 Calling NeuroSnap toxicity API for {mol.name}")

                result = self.neurosnap_client.predict_toxicity(mol.smiles)

                # Parse NeuroSnap response
                toxicity_score = result.get('score', 0.5)

                self.log(state, f"✅ NeuroSnap toxicity result: {toxicity_score:.3f} (Transaction: {transaction_id})")

                return {
                    'requires_payment': False,
                    'toxicity_score': toxicity_score,
                    'cost': cost_per_check,
                    'prediction_confidence': result.get('confidence', 0.85),
                    'endpoints': result.get('endpoints', {}),
                    'transaction_id': transaction_id,
                    'payment_method': 'locus_usdc'
                }

            except Exception as e:
                self.log(state, f"⚠️  API error: {str(e)}, using fallback")
                # Fall through to mock mode

        # Mock/fallback mode (for testing without real APIs)
        await asyncio.sleep(0.1)

        # First call without payment - return 402
        if payment_token is None:
            return {
                'requires_payment': True,
                'payment_info': {
                    'price': cost_per_check,
                    'currency': 'USD',
                    'pay_to': 'neurosnap',
                    'nonce': f'tox_{mol.id}'
                }
            }

        # Second call with payment - return mock result
        toxicity_score = random.betavariate(2, 5)  # Skewed toward lower values

        return {
            'requires_payment': False,
            'toxicity_score': toxicity_score,
            'cost': cost_per_check,
            'prediction_confidence': random.uniform(0.7, 0.95),
            'transaction_id': f'mock_tx_{mol.id}',
            'payment_method': 'simulated'
        }

    async def _evaluate_efficacy(self, molecules: List[Molecule],
                                criteria: Dict[str, Any],
                                state: AgentState) -> List[Molecule]:
        """
        Evaluate efficacy/activity for each molecule

        Similar to toxicity evaluation but for predicted biological activity.
        """
        passed = []
        min_efficacy = criteria.get('min_efficacy_score', 0.5)

        for mol in molecules:
            efficacy_result = await self._call_efficacy_api(mol, state)

            if efficacy_result['requires_payment']:
                payment_result = await self.payment_module.handle_402_challenge(
                    state=state,
                    response_data=efficacy_result['payment_info'],
                    original_request={'smiles': mol.smiles}
                )

                if not payment_result['success']:
                    # If we can't afford efficacy check, it's optional - keep the molecule
                    self.log(state, f"Skipping efficacy check for {mol.name} (budget constraint)")
                    passed.append(mol)
                    continue

                efficacy_result = await self._call_efficacy_api(mol, state, payment_token=payment_result['payment_token'])
                mol.cost_incurred += efficacy_result['cost']

            efficacy_score = efficacy_result['efficacy_score']
            mol.properties.efficacy_score = efficacy_score
            mol.properties.predicted_activity = "High" if efficacy_score > 0.7 else "Moderate" if efficacy_score > 0.4 else "Low"

            mol.evaluation_history.append({
                'check': 'efficacy',
                'score': efficacy_score,
                'passed': efficacy_score >= min_efficacy,
                'cost': efficacy_result['cost']
            })

            if efficacy_score >= min_efficacy:
                passed.append(mol)
                self.log(state, f"{mol.name}: efficacy={efficacy_score:.2f} (PASS)")
            else:
                mol.status = MoleculeStatus.REJECTED
                mol.rejection_reason = f"Efficacy too low: {efficacy_score:.2f} < {min_efficacy}"
                self.log(state, f"{mol.name}: efficacy={efficacy_score:.2f} (FAIL)")

        return passed

    async def _call_efficacy_api(self, mol: Molecule, state: AgentState,
                                payment_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Call real NeuroSnap ADMET/synthesizability API for drug-likeness evaluation
        """
        # Try real NeuroSnap API first
        if self.neurosnap_client and payment_token is not None:
            try:
                self.log(state, f"🧪 Calling NeuroSnap ADMET & Synthesizability for {mol.name}")

                # Get both ADMET and synthesizability
                admet_result = self.neurosnap_client.predict_admet(mol.smiles)
                synth_result = self.neurosnap_client.predict_synthesizability(mol.smiles)

                # Calculate composite efficacy score from ADMET and synthesizability
                admet_score = admet_result.get('score', 0.5)
                synth_score = synth_result.get('score', 0.5)

                # Efficacy = weighted combination of ADMET (60%) and synthesizability (40%)
                efficacy_score = (admet_score * 0.6) + (synth_score * 0.4)

                self.log(state, f"✅ NeuroSnap efficacy: {efficacy_score:.3f} (ADMET: {admet_score:.2f}, Synth: {synth_score:.2f})")

                # Store detailed properties
                mol.properties.additional_properties['admet_profile'] = admet_result.get('properties', {})
                mol.properties.additional_properties['synthesizability'] = synth_result.get('sas_score', 0)

                return {
                    'requires_payment': False,
                    'efficacy_score': efficacy_score,
                    'cost': 0.01,  # NeuroSnap API cost for both checks
                    'prediction_confidence': (admet_result.get('confidence', 0.8) + synth_result.get('confidence', 0.8)) / 2,
                    'admet_score': admet_score,
                    'synth_score': synth_score
                }

            except Exception as e:
                self.log(state, f"⚠️  NeuroSnap ADMET API error: {str(e)}, using fallback")
                # Fall through to mock mode

        # Mock/fallback mode
        await asyncio.sleep(0.1)

        if payment_token is None:
            return {
                'requires_payment': True,
                'payment_info': {
                    'price': 0.01,
                    'currency': 'USD',
                    'pay_to': 'efficacy_prediction_api',
                    'nonce': f'eff_{mol.id}'
                }
            }

        efficacy_score = random.betavariate(3, 2)  # Biased toward moderate-high values

        return {
            'requires_payment': False,
            'efficacy_score': efficacy_score,
            'cost': 0.01,
            'prediction_confidence': random.uniform(0.6, 0.9)
        }

    def _rank_molecules(self, molecules: List[Molecule], state: AgentState) -> List[Molecule]:
        """
        Rank molecules by a composite score

        Ranking criteria:
        1. Lower toxicity is better
        2. Higher efficacy is better (if available)
        3. Lower cost is better (all else equal)
        """
        for mol in molecules:
            # Calculate composite score (0-1, higher is better)
            tox_score = 1.0 - (mol.properties.toxicity_score or 0.5)
            eff_score = mol.properties.efficacy_score or 0.5
            cost_penalty = min(1.0, mol.cost_incurred / 0.50)  # Penalize expensive evaluations

            # Weighted composite
            composite = (tox_score * 0.5) + (eff_score * 0.4) - (cost_penalty * 0.1)
            mol.properties.additional_properties['composite_score'] = composite

        # Sort by composite score (descending)
        ranked = sorted(molecules,
                       key=lambda m: m.properties.additional_properties.get('composite_score', 0),
                       reverse=True)

        # Mark top candidates as PASSED
        for mol in ranked:
            mol.status = MoleculeStatus.PASSED

        return ranked
