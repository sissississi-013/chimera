"""
Payment Module - Handles x402 micropayments and Stripe transactions
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import asyncio
from .base import BaseModule
from ..models.agent_state import AgentState, PaymentTransaction


class PaymentModule(BaseModule):
    """
    The Payment Module manages all economic transactions:
    1. x402 micropayments via Coinbase CDP wallet (for API calls)
    2. Stripe payments for fiat transactions
    3. Budget tracking and authorization
    4. Payment retry logic

    For initial development, this uses mock/simulated payments.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.mock_mode = config.get('mock_mode', True) if config else True
        self.wallet_balance = config.get('wallet_balance', 100.0) if config else 100.0

    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute is not typically called directly for Payment Module.
        Instead, other modules call handle_payment_challenge() or make_payment()
        """
        self.log(state, "Payment module initialized")
        return state

    async def handle_402_challenge(self, state: AgentState, response_data: Dict[str, Any],
                                   original_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle HTTP 402 Payment Required challenge

        Args:
            state: Agent state
            response_data: The 402 response data including payment requirements
            original_request: The original API request that triggered 402

        Returns:
            Dict containing payment token and instructions for retry
        """
        self.log(state, "Received 402 Payment Required challenge")

        # Parse payment requirements from 402 response
        price = response_data.get('price', 0.0)
        currency = response_data.get('currency', 'USD')
        pay_to = response_data.get('pay_to', 'unknown_service')
        nonce = response_data.get('nonce', str(uuid.uuid4()))

        self.log(state, f"Payment required: {price} {currency} to {pay_to}")

        # Check if we can afford it
        if not self._can_afford(state, price):
            self.log(state, f"ERROR: Insufficient budget. Required: ${price:.2f}, "
                           f"Remaining: ${state.plan.budget_allocation.remaining:.2f}")
            return {
                "success": False,
                "error": "Insufficient budget",
                "required": price,
                "available": state.plan.budget_allocation.remaining
            }

        # Perform cost-benefit analysis
        if not self._is_worth_paying(state, price, pay_to):
            self.log(state, f"Decision: Not worth paying ${price:.2f} for {pay_to}")
            return {
                "success": False,
                "error": "Cost exceeds benefit threshold",
                "required": price
            }

        # Create payment
        payment_result = await self._make_x402_payment(
            state=state,
            amount=price,
            currency=currency,
            service=pay_to,
            nonce=nonce
        )

        return payment_result

    async def _make_x402_payment(self, state: AgentState, amount: float,
                                currency: str, service: str, nonce: str) -> Dict[str, Any]:
        """
        Make an x402 micropayment using CDP wallet

        In production, this would:
        1. Use Coinbase CDP SDK to access wallet
        2. Sign payment payload with private key
        3. Submit transaction on-chain or via facilitator
        4. Return signed payment token

        For now, we simulate this process.
        """
        self.log(state, f"Processing x402 payment: ${amount:.2f} to {service}")

        if self.mock_mode:
            # Simulate payment processing delay
            await asyncio.sleep(0.1)

            # Create mock signed payment payload
            payment_token = self._create_mock_payment_token(amount, currency, service, nonce)

            # Record transaction
            transaction = PaymentTransaction(
                transaction_id=f"x402_{uuid.uuid4().hex[:12]}",
                amount=amount,
                currency=currency,
                payment_method="x402_mock",
                service=service,
                status="completed",
                details={
                    "nonce": nonce,
                    "payment_token": payment_token,
                    "wallet_balance": self.wallet_balance
                }
            )

            state.add_transaction(transaction)
            self.log(state, f"Payment successful. TX ID: {transaction.transaction_id}")

            return {
                "success": True,
                "payment_token": payment_token,
                "transaction_id": transaction.transaction_id,
                "X-PAYMENT": payment_token  # Header to attach to retry request
            }
        else:
            # Real CDP wallet integration would go here
            # from coinbase.wallet import Client
            # client = Client(api_key, api_secret)
            # ...
            pass

    async def make_stripe_payment(self, state: AgentState, amount: float,
                                 description: str) -> Dict[str, Any]:
        """
        Make a Stripe payment (for fiat services)

        Args:
            state: Agent state
            amount: Amount in USD
            description: What the payment is for

        Returns:
            Payment result dictionary
        """
        self.log(state, f"Processing Stripe payment: ${amount:.2f} for {description}")

        if not self._can_afford(state, amount):
            self.log(state, "ERROR: Insufficient budget for Stripe payment")
            return {"success": False, "error": "Insufficient budget"}

        if self.mock_mode:
            # Simulate payment processing
            await asyncio.sleep(0.2)

            transaction = PaymentTransaction(
                transaction_id=f"stripe_{uuid.uuid4().hex[:12]}",
                amount=amount,
                currency="USD",
                payment_method="stripe_mock",
                service=description,
                status="completed",
                details={
                    "card_last4": "4242",
                    "description": description
                }
            )

            state.add_transaction(transaction)
            self.log(state, f"Stripe payment successful. TX ID: {transaction.transaction_id}")

            return {
                "success": True,
                "transaction_id": transaction.transaction_id,
                "amount": amount
            }
        else:
            # Real Stripe integration would go here
            # import stripe
            # stripe.api_key = self.config.get('stripe_api_key')
            # ...
            pass

    def _can_afford(self, state: AgentState, amount: float) -> bool:
        """
        Check if we have sufficient budget

        Args:
            state: Agent state
            amount: Amount to check

        Returns:
            True if affordable, False otherwise
        """
        if not state.plan:
            return False

        return state.plan.budget_allocation.can_spend(amount)

    def _is_worth_paying(self, state: AgentState, amount: float, service: str) -> bool:
        """
        Cost-benefit analysis: Is this payment worth it?

        Decision rules:
        1. Essential services (toxicity checks): Pay if within budget
        2. Optional services (secondary checks): Only if we have >30% budget remaining
        3. Never exceed max_cost_per_molecule if evaluating a molecule
        4. Prioritize critical path items

        Args:
            state: Agent state
            amount: Payment amount
            service: What service we're paying for

        Returns:
            True if worth paying, False otherwise
        """
        if not state.plan:
            return False

        budget = state.plan.budget_allocation

        # Check max cost per molecule if applicable
        if "toxicity" in service.lower() or "efficacy" in service.lower():
            max_per_mol = state.plan.evaluation_criteria.get('max_cost_per_molecule', 1.0)
            if amount > max_per_mol:
                self.log(state, f"Payment ${amount:.2f} exceeds max per molecule ${max_per_mol:.2f}")
                return False

        # Essential services - pay if we can afford it
        essential_services = ["toxicity", "drug_likeness", "safety"]
        if any(term in service.lower() for term in essential_services):
            return self._can_afford(state, amount)

        # Optional services - only if we have comfortable budget remaining
        remaining_pct = (budget.remaining / budget.total_budget) * 100
        if remaining_pct < 30:
            self.log(state, f"Skipping optional service {service} - only {remaining_pct:.1f}% budget remaining")
            return False

        return self._can_afford(state, amount)

    def _create_mock_payment_token(self, amount: float, currency: str,
                                   service: str, nonce: str) -> str:
        """
        Create a mock payment token simulating x402 signed payload

        In production, this would be:
        - A cryptographically signed payload
        - Including wallet address, amount, nonce, signature
        - Verifiable by the service provider
        """
        # Mock token structure (base64-like)
        token_data = f"{amount}:{currency}:{service}:{nonce}:{uuid.uuid4().hex}"
        # In real implementation: sign with private key
        mock_signature = uuid.uuid4().hex[:32]

        return f"x402.{token_data}.{mock_signature}"

    def get_budget_status(self, state: AgentState) -> Dict[str, Any]:
        """
        Get current budget status

        Args:
            state: Agent state

        Returns:
            Budget status dictionary
        """
        if not state.plan:
            return {"error": "No plan available"}

        budget = state.plan.budget_allocation

        return {
            "total_budget": budget.total_budget,
            "spent": budget.spent,
            "remaining": budget.remaining,
            "remaining_pct": (budget.remaining / budget.total_budget) * 100,
            "transactions": len(state.transactions),
            "allocation": {
                "generation": budget.generation_budget,
                "evaluation": budget.evaluation_budget,
                "visualization": budget.visualization_budget,
                "monetization": budget.monetization_budget,
                "reserve": budget.reserve_budget
            }
        }
