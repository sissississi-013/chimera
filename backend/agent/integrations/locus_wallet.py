"""
Locus Wallet Integration - AI Agent spending controls and monitoring
"""
import os
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LocusWalletClient:
    """
    Client for Locus - AI Agent spending controls

    Features:
    - Set spending limits per vendor
    - Real-time transaction monitoring
    - Automatic spending freezes
    - Multi-signature approvals for large transactions
    """

    def __init__(self):
        self.api_key = os.getenv('LOCUS_API_KEY', 'PENDING')
        self.api_url = os.getenv('LOCUS_API_URL', 'https://api.paywithlocus.com/v1')
        self.wallet_address = os.getenv('LOCUS_WALLET_ADDRESS')

        if not self.wallet_address:
            raise Exception("LOCUS_WALLET_ADDRESS not found in environment")

        if self.api_key == 'PENDING':
            logger.warning("⚠️  Locus API key not configured. Get it from paywithlocus.com dashboard")

        logger.info(f"✅ Locus Wallet initialized: {self.wallet_address}")

    def request_payment_approval(
        self,
        amount: float,
        vendor: str,
        description: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Request approval for a payment from Locus

        Args:
            amount: Payment amount in USD
            vendor: Vendor identifier (e.g., 'neurosnap', 'nvidia_molmim')
            description: Human-readable description
            metadata: Additional context

        Returns:
            Approval response with transaction ID and status
        """
        if self.api_key == 'PENDING':
            logger.warning("⚠️  Locus API not configured, simulating approval")
            return {
                'approved': True,
                'transaction_id': f'locus_sim_{vendor}_{int(amount * 1000)}',
                'wallet_address': self.wallet_address,
                'amount': amount,
                'vendor': vendor,
                'message': 'Simulated approval - configure Locus API for production'
            }

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'wallet_address': self.wallet_address,
                'amount_usd': amount,
                'vendor': vendor,
                'description': description,
                'metadata': metadata or {}
            }

            response = requests.post(
                f'{self.api_url}/transactions/request-approval',
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            logger.info(f"💳 Locus approval: ${amount:.3f} to {vendor} - {data.get('status')}")

            return data

        except Exception as e:
            logger.error(f"❌ Locus error: {str(e)}")
            raise Exception(f"Locus payment approval failed: {str(e)}")

    def check_spending_limit(
        self,
        amount: float,
        vendor: str
    ) -> Dict[str, Any]:
        """
        Check if payment is within spending limits

        Args:
            amount: Payment amount
            vendor: Vendor identifier

        Returns:
            Limit check result with remaining budget
        """
        if self.api_key == 'PENDING':
            return {
                'within_limit': True,
                'remaining': 100.0,
                'limit': 100.0,
                'vendor_limit': 10.0
            }

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            params = {
                'wallet_address': self.wallet_address,
                'amount': amount,
                'vendor': vendor
            }

            response = requests.get(
                f'{self.api_url}/limits/check',
                headers=headers,
                params=params,
                timeout=10
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"❌ Locus limit check error: {str(e)}")
            return {
                'within_limit': False,
                'error': str(e)
            }

    def get_transaction_history(
        self,
        limit: int = 20
    ) -> list[Dict[str, Any]]:
        """
        Get recent transaction history

        Args:
            limit: Number of transactions to fetch

        Returns:
            List of transactions
        """
        if self.api_key == 'PENDING':
            return [
                {
                    'transaction_id': 'sim_001',
                    'amount': 0.005,
                    'vendor': 'neurosnap',
                    'status': 'approved',
                    'timestamp': '2025-01-15T10:30:00Z'
                }
            ]

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            params = {
                'wallet_address': self.wallet_address,
                'limit': limit
            }

            response = requests.get(
                f'{self.api_url}/transactions',
                headers=headers,
                params=params,
                timeout=10
            )

            response.raise_for_status()
            return response.json().get('transactions', [])

        except Exception as e:
            logger.error(f"❌ Locus history error: {str(e)}")
            return []

    def set_vendor_limit(
        self,
        vendor: str,
        daily_limit: float
    ) -> Dict[str, Any]:
        """
        Set daily spending limit for a specific vendor

        Args:
            vendor: Vendor identifier
            daily_limit: Maximum daily spend in USD

        Returns:
            Updated limit configuration
        """
        if self.api_key == 'PENDING':
            logger.info(f"Would set {vendor} limit to ${daily_limit}/day")
            return {'vendor': vendor, 'daily_limit': daily_limit, 'status': 'simulated'}

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'wallet_address': self.wallet_address,
                'vendor': vendor,
                'daily_limit_usd': daily_limit
            }

            response = requests.post(
                f'{self.api_url}/limits/vendor',
                headers=headers,
                json=payload,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            logger.info(f"✅ Set {vendor} limit: ${daily_limit}/day")

            return data

        except Exception as e:
            logger.error(f"❌ Locus set limit error: {str(e)}")
            raise Exception(f"Failed to set vendor limit: {str(e)}")

    def get_wallet_status(self) -> Dict[str, Any]:
        """
        Get current wallet status and limits

        Returns:
            Wallet status including balance, limits, and spending
        """
        if self.api_key == 'PENDING':
            return {
                'wallet_address': self.wallet_address,
                'total_limit': 100.0,
                'spent_today': 0.15,
                'remaining': 99.85,
                'vendor_limits': {
                    'neurosnap': {'limit': 10.0, 'spent': 0.05},
                    'nvidia_molmim': {'limit': 20.0, 'spent': 0.10}
                },
                'status': 'active',
                'configured': False
            }

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            params = {
                'wallet_address': self.wallet_address
            }

            response = requests.get(
                f'{self.api_url}/wallet/status',
                headers=headers,
                params=params,
                timeout=10
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"❌ Locus wallet status error: {str(e)}")
            return {'error': str(e), 'configured': False}


# Cost limits per vendor for Locus
VENDOR_LIMITS = {
    'neurosnap': 10.0,  # $10/day
    'nvidia_molmim': 20.0,  # $20/day
    'nvidia_genmol': 15.0,  # $15/day
    'nvidia_alphafold2': 50.0,  # $50/day
    'nvidia_diffdock': 30.0,  # $30/day
}
