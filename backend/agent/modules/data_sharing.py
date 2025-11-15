"""
Data Sharing/Monetization Module - Uploads molecules to marketplace
"""
from typing import List, Dict, Any, Optional
import uuid
import asyncio
from .base import BaseModule
from .payment import PaymentModule
from ..models.agent_state import AgentState, AgentPhase
from ..models.molecule import Molecule, MoleculeStatus


class DataSharingModule(BaseModule):
    """
    The Data Sharing Module handles monetization:
    1. Prepare molecule data for sharing/sale
    2. Upload to paywalled marketplace (may require listing fee)
    3. Handle x402 payment if required
    4. Confirm listing and capture receipt

    In production, this could integrate with:
    - Data marketplaces (Ocean Protocol, etc.)
    - NFT platforms (for IP as NFT)
    - Custom data APIs
    - On-chain storage with payment
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.payment_module = PaymentModule(config)
        self.mock_mode = config.get('mock_mode', True) if config else True
        self.marketplace_url = config.get('marketplace_url', 'https://api.datamarket.example.com') if config else 'https://api.datamarket.example.com'

    async def execute(self, state: AgentState) -> AgentState:
        """
        Upload successful molecules to marketplace

        Args:
            state: Agent state with evaluated molecules

        Returns:
            State with monetization results
        """
        self.log(state, "Starting data monetization")
        state.phase = AgentPhase.MONETIZING

        # Get top molecules to monetize
        passed_molecules = [m for m in state.molecules if m.status == MoleculeStatus.PASSED]

        if not passed_molecules:
            self.log(state, "No molecules to monetize")
            return state

        # Monetize top candidates (default: top 3)
        molecules_to_share = passed_molecules[:3]
        self.log(state, f"Uploading {len(molecules_to_share)} molecules to marketplace")

        results = []
        for mol in molecules_to_share:
            result = await self._upload_molecule(mol, state)
            results.append(result)

            if result['success']:
                mol.status = MoleculeStatus.MONETIZED
                mol.properties.additional_properties['listing_id'] = result.get('listing_id')
                mol.properties.additional_properties['listing_url'] = result.get('listing_url')
                self.log(state, f"✓ {mol.name} monetized successfully (Listing ID: {result.get('listing_id')})")
            else:
                self.log(state, f"✗ Failed to monetize {mol.name}: {result.get('error')}")

        # Store results in state
        if not state.final_results:
            state.final_results = {}

        state.final_results['monetization'] = {
            'attempted': len(molecules_to_share),
            'successful': len([r for r in results if r['success']]),
            'results': results
        }

        return state

    async def _upload_molecule(self, mol: Molecule, state: AgentState) -> Dict[str, Any]:
        """
        Upload a single molecule to the marketplace

        Args:
            mol: Molecule to upload
            state: Agent state

        Returns:
            Upload result dictionary
        """
        self.log(state, f"Uploading {mol.name} to marketplace...")

        # Prepare data package
        data_package = self._prepare_data_package(mol)

        # Attempt upload
        upload_result = await self._call_marketplace_api(data_package, state)

        if upload_result['requires_payment']:
            # Handle 402 payment challenge
            self.log(state, f"Marketplace requires payment: ${upload_result['payment_info']['price']:.2f}")

            payment_result = await self.payment_module.handle_402_challenge(
                state=state,
                response_data=upload_result['payment_info'],
                original_request=data_package
            )

            if not payment_result['success']:
                self.log(state, f"Failed to pay listing fee: {payment_result.get('error')}")
                return {
                    'success': False,
                    'error': f"Payment failed: {payment_result.get('error')}",
                    'molecule_id': mol.id
                }

            # Retry with payment token
            upload_result = await self._call_marketplace_api(
                data_package,
                state,
                payment_token=payment_result['payment_token']
            )

        if upload_result['success']:
            return {
                'success': True,
                'molecule_id': mol.id,
                'listing_id': upload_result['listing_id'],
                'listing_url': upload_result['listing_url'],
                'cost': upload_result.get('cost', 0.0)
            }
        else:
            return {
                'success': False,
                'error': upload_result.get('error', 'Unknown error'),
                'molecule_id': mol.id
            }

    def _prepare_data_package(self, mol: Molecule) -> Dict[str, Any]:
        """
        Prepare molecule data for upload/sale

        Args:
            mol: Molecule to package

        Returns:
            Data package dictionary
        """
        return {
            'molecule': {
                'id': mol.id,
                'name': mol.name,
                'smiles': mol.smiles,
                'structure': mol.smiles,  # Could include other formats (InChI, mol file, etc.)
            },
            'properties': {
                'toxicity_score': mol.properties.toxicity_score,
                'efficacy_score': mol.properties.efficacy_score,
                'molecular_weight': mol.properties.molecular_weight,
                'logp': mol.properties.logp,
                'drug_likeness': mol.properties.drug_likeness,
                'predicted_activity': mol.properties.predicted_activity,
            },
            'metadata': {
                'generation_method': mol.generation_method,
                'evaluation_history': mol.evaluation_history,
                'generated_by': 'Chimera Autonomous Agent',
                'agent_version': '0.1.0'
            },
            'visualization': mol.visualization_url,
            'pricing': {
                'suggested_price': 10.0,  # Could be calculated based on properties
                'currency': 'USD'
            }
        }

    async def _call_marketplace_api(self, data_package: Dict[str, Any],
                                   state: AgentState,
                                   payment_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Call marketplace API to upload molecule data

        In production:
        async with httpx.AsyncClient() as client:
            headers = {'X-PAYMENT': payment_token} if payment_token else {}
            response = await client.post(
                f'{self.marketplace_url}/molecules',
                json=data_package,
                headers=headers
            )

            if response.status_code == 402:
                return {'requires_payment': True, 'payment_info': response.json()}

            return response.json()

        For now, simulate the API call
        """
        await asyncio.sleep(0.2)  # Simulate network delay

        if self.mock_mode:
            # First call without payment - return 402
            if payment_token is None:
                return {
                    'requires_payment': True,
                    'payment_info': {
                        'price': 0.20,
                        'currency': 'USD',
                        'pay_to': 'data_marketplace_listing_fee',
                        'nonce': f'listing_{data_package["molecule"]["id"]}'
                    }
                }

            # Second call with payment - success
            listing_id = f'listing_{uuid.uuid4().hex[:12]}'
            listing_url = f'{self.marketplace_url}/listings/{listing_id}'

            return {
                'success': True,
                'requires_payment': False,
                'listing_id': listing_id,
                'listing_url': listing_url,
                'cost': 0.20,
                'message': 'Molecule data successfully uploaded to marketplace'
            }

        return {
            'success': False,
            'error': 'Real API mode not implemented yet'
        }

    async def can_execute(self, state: AgentState) -> bool:
        """Check if we can monetize"""
        return (state.phase == AgentPhase.VISUALIZING and
                len([m for m in state.molecules if m.status == MoleculeStatus.PASSED]) > 0)

    def get_required_budget(self, state: AgentState) -> float:
        """Estimate monetization cost"""
        if state.plan:
            return state.plan.budget_allocation.monetization_budget
        return 0.0
