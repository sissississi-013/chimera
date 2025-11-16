"""
NeuroSnap API Integration for Toxicity & Synthesizability Prediction
"""
import os
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class NeuroSnapError(Exception):
    """Base exception for NeuroSnap API errors"""
    pass


class NeuroSnapClient:
    """Client for NeuroSnap - Toxicity and Synthesizability Prediction"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('NEUROSNAP_API_KEY')
        self.base_url = os.getenv('NEUROSNAP_API_URL', 'https://api.neurosnap.ai/v1')

        if not self.api_key:
            raise NeuroSnapError("NEUROSNAP_API_KEY not found in environment")

    def predict_toxicity(self, smiles: str) -> Dict[str, Any]:
        """
        Predict toxicity profile for a molecule

        Args:
            smiles: SMILES string of molecule

        Returns:
            Dict with toxicity predictions across multiple endpoints
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'smiles': smiles,
            'endpoints': [
                'acute_toxicity',
                'carcinogenicity',
                'mutagenicity',
                'hERG',
                'hepatotoxicity'
            ]
        }

        logger.info(f"🧪 NeuroSnap: Predicting toxicity for {smiles[:30]}...")

        try:
            response = requests.post(
                f'{self.base_url}/toxicity/predict',
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ NeuroSnap: Toxicity prediction complete")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ NeuroSnap toxicity API error: {str(e)}")
            # Return mock data for fallback
            return self._get_mock_toxicity()

    def predict_synthesizability(self, smiles: str) -> Dict[str, Any]:
        """
        Predict synthesizability score (Synthetic Accessibility Score)

        Args:
            smiles: SMILES string of molecule

        Returns:
            Dict with SAS score and synthetic feasibility
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'smiles': smiles
        }

        logger.info(f"🧪 NeuroSnap: Predicting synthesizability for {smiles[:30]}...")

        try:
            response = requests.post(
                f'{self.base_url}/synthesizability/predict',
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ NeuroSnap: Synthesizability prediction complete")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ NeuroSnap synthesizability API error: {str(e)}")
            # Return mock data for fallback
            return self._get_mock_synthesizability()

    def predict_admet(self, smiles: str) -> Dict[str, Any]:
        """
        Predict ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) properties

        Args:
            smiles: SMILES string of molecule

        Returns:
            Dict with ADMET predictions
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'smiles': smiles,
            'properties': [
                'bioavailability',
                'blood_brain_barrier',
                'caco2_permeability',
                'cyp450_inhibition',
                'plasma_protein_binding'
            ]
        }

        logger.info(f"🧪 NeuroSnap: Predicting ADMET for {smiles[:30]}...")

        try:
            response = requests.post(
                f'{self.base_url}/admet/predict',
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ NeuroSnap: ADMET prediction complete")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ NeuroSnap ADMET API error: {str(e)}")
            # Return mock data for fallback
            return self._get_mock_admet()

    def comprehensive_evaluation(self, smiles: str) -> Dict[str, Any]:
        """
        Run comprehensive evaluation: toxicity, synthesizability, and ADMET

        Args:
            smiles: SMILES string of molecule

        Returns:
            Dict with all predictions combined
        """
        logger.info(f"🔬 Running comprehensive evaluation for {smiles[:30]}...")

        toxicity = self.predict_toxicity(smiles)
        synthesizability = self.predict_synthesizability(smiles)
        admet = self.predict_admet(smiles)

        return {
            'smiles': smiles,
            'toxicity': toxicity,
            'synthesizability': synthesizability,
            'admet': admet,
            'overall_score': self._calculate_overall_score(toxicity, synthesizability, admet)
        }

    def _calculate_overall_score(
        self,
        toxicity: Dict,
        synthesizability: Dict,
        admet: Dict
    ) -> float:
        """Calculate overall drug-likeness score"""
        # Simple scoring: lower toxicity, higher synthesizability, better ADMET = higher score
        # This is a simplified version - real scoring would be more sophisticated
        score = 0.0

        # Toxicity (lower is better) - scale 0-1
        tox_score = toxicity.get('score', 0.5)
        score += (1.0 - tox_score) * 0.4  # 40% weight

        # Synthesizability (higher is better) - scale 0-1
        syn_score = synthesizability.get('score', 0.5)
        score += syn_score * 0.3  # 30% weight

        # ADMET (higher is better) - scale 0-1
        admet_score = admet.get('score', 0.5)
        score += admet_score * 0.3  # 30% weight

        return round(score, 3)

    def _get_mock_toxicity(self) -> Dict[str, Any]:
        """Return mock toxicity data as fallback"""
        return {
            'score': 0.25,
            'prediction': 'low_risk',
            'endpoints': {
                'acute_toxicity': 'low',
                'carcinogenicity': 'low',
                'mutagenicity': 'low',
                'hERG': 'low_risk',
                'hepatotoxicity': 'low'
            },
            'confidence': 0.85,
            'note': 'Mock data - API unavailable'
        }

    def _get_mock_synthesizability(self) -> Dict[str, Any]:
        """Return mock synthesizability data as fallback"""
        return {
            'score': 0.72,
            'sas_score': 2.8,
            'prediction': 'synthetically_accessible',
            'complexity': 'moderate',
            'confidence': 0.88,
            'note': 'Mock data - API unavailable'
        }

    def _get_mock_admet(self) -> Dict[str, Any]:
        """Return mock ADMET data as fallback"""
        return {
            'score': 0.68,
            'properties': {
                'bioavailability': 'high',
                'blood_brain_barrier': 'permeable',
                'caco2_permeability': 'high',
                'cyp450_inhibition': 'non_inhibitor',
                'plasma_protein_binding': 'moderate'
            },
            'confidence': 0.82,
            'note': 'Mock data - API unavailable'
        }
