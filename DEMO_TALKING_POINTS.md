# Chimera Demo - Stripe & Coinbase Payment Integration Talking Points

## Overview
Chimera demonstrates next-generation autonomous AI payments using both traditional (Stripe) and crypto (Coinbase CDP x402) payment rails for drug discovery APIs.

---

## Stripe Integration (Fiat Payments)

### What We Built
- **Complete Payment Flow**: Users can purchase discovered molecules via credit card
- **Webhook Integration**: Real-time payment confirmations and status updates
- **Test Mode**: Fully functional test environment for safe demonstration

### Key Features to Highlight:

**1. Marketplace Monetization**
- "When our agent discovers valuable molecules, we automatically list them on the marketplace"
- "Other researchers can purchase access to molecular data instantly via Stripe"
- "Payment Intent API handles the entire checkout flow - from cart to confirmation"

**2. Stripe Checkout Session**
- "We create checkout sessions programmatically - no manual payment processing needed"
- "Customers get redirected to Stripe's hosted checkout page (PCI compliant out-of-the-box)"
- "Supports multiple payment methods: cards, Apple Pay, Google Pay"

**3. Webhook Events**
```
payment_intent.succeeded → Grant access to molecule data
checkout.session.completed → Send download links
payment_intent.payment_failed → Handle retries gracefully
```

**4. Test Card for Demo**
- Card Number: `4242 4242 4242 4242`
- Expiry: Any future date (e.g., `12/34`)
- CVC: Any 3 digits (e.g., `123`)
- "This lets us demonstrate the full payment flow without real money"

### Demo Flow:
1. Show molecule in marketplace with price tag
2. Click "Purchase" → Creates Stripe Payment Intent
3. Enter test card → Instant payment confirmation
4. Webhook fires → Backend grants data access
5. Show successful purchase in transaction history

---

## Coinbase CDP Integration (Crypto Payments)

### What We Built
- **x402 Protocol**: HTTP 402 Payment Required - API returns payment request, agent pays automatically
- **CDP Wallet**: Coinbase Developer Platform wallet for programmatic crypto transactions
- **USDC on Base**: Fast, low-cost stablecoin payments on Base L2 network

### Key Features to Highlight:

**1. Autonomous AI Payments**
- "Traditional APIs return 402 Payment Required when the agent needs to pay"
- "Our agent automatically signs transactions with its CDP wallet - no human intervention"
- "This is true autonomous commerce - AI agents transacting with other services"

**2. x402 Protocol Flow**
```
1. Agent calls Toxicity API
2. API returns: 402 Payment Required + Payment Address
3. Agent signs USDC transaction via CDP wallet
4. API receives payment confirmation on-chain
5. API returns toxicity data
6. All happens in <2 seconds
```

**3. Why Coinbase CDP?**
- **Programmatic Wallets**: Create wallets via API, no seed phrases
- **MPC Security**: Multi-party computation for secure key management
- **Base Network**: <$0.01 transaction fees, 2-second confirmation
- **USDC Native**: Stablecoin designed for programmatic payments

**4. Cost Tracking**
- "Every API call is tracked with real costs"
- "Budget limits prevent overspending: $10 total, $2 generation, $5 evaluation"
- "Warning system alerts at 75% of any limit"

### Demo Flow:
1. Show agent wallet address and USDC balance
2. Start discovery run → Agent needs toxicity prediction
3. API returns 402 Payment Required ($0.005)
4. Agent automatically sends $0.005 USDC
5. Transaction confirmed on Base Sepolia (testnet)
6. Toxicity data received
7. Show transaction in wallet history

---

## Locus Wallet Integration (Coming Next)

### What We're Adding
- **Spending Controls**: Set hard limits per vendor, per day
- **Real-time Monitoring**: Track agent spending across all services
- **Risk Management**: Automatic freezing if suspicious activity detected
- **Multi-signature**: Require approval for transactions above threshold

### Why Locus?
- "Locus specializes in AI agent spending controls"
- "Think of it as a corporate card for your AI agent"
- "You set the rules, the agent operates within those guardrails"
- "Perfect for production deployments where you need auditability"

### Current Setup
- Wallet Address: `0x3859872d208f9c144adaa56bee126cdcc1e2d71a`
- API Key: Pending (get from paywithlocus.com dashboard)
- Will integrate via their REST API for transaction approval/decline

---

## Combined Value Proposition

### For Researchers:
- **No Payment Friction**: Buy molecules with card or crypto
- **Transparent Costs**: See exactly what each API call costs
- **Instant Access**: No waiting for invoices or wire transfers

### For AI Agents:
- **True Autonomy**: Make purchasing decisions without human approval
- **Budget Awareness**: Optimize API usage based on cost/benefit
- **Multi-modal Payments**: Use whatever payment rail makes sense

### For API Providers:
- **Instant Settlement**: Crypto payments settle in seconds
- **Lower Fees**: 0.5% crypto fees vs 2.9% card fees
- **Global Access**: Accept payments from anywhere, no currency conversion

---

## Technical Architecture

```
┌─────────────────┐
│  Chimera Agent  │
│   (Planning +   │
│   Decision)     │
└────────┬────────┘
         │
         ├─── Need Fiat Payment? ──→ Stripe API
         │         │
         │         ↓
         │    [Create Payment Intent]
         │         │
         │         ↓
         │    [Customer pays via card]
         │         │
         │         ↓
         │    [Webhook: payment_succeeded]
         │
         ├─── Need Crypto Payment? ──→ x402 Protocol
         │         │
         │         ↓
         │    [API returns 402 + address]
         │         │
         │         ↓
         │    [CDP Wallet signs tx]
         │         │
         │         ↓
         │    [Base network confirms]
         │         │
         │         ↓
         │    [API returns data]
         │
         └─── Budget Tracking ──→ Cost Manager
                   │
                   ↓
              [Log every cost]
                   │
                   ↓
              [Enforce limits]
                   │
                   ↓
              [Warn at 75%]
```

---

## Questions to Anticipate

**Q: Why not just use Stripe for everything?**
A: Crypto is better for AI-to-AI payments. No human approval needed, instant settlement, programmable money. Stripe is great for human checkouts.

**Q: Isn't crypto too volatile for payments?**
A: We use USDC - a stablecoin pegged 1:1 to USD. Zero volatility risk.

**Q: What about gas fees on Ethereum?**
A: We use Base (Ethereum L2) - fees are <$0.01 per transaction vs $5-50 on mainnet.

**Q: How do you prevent the agent from spending unlimited money?**
A: Hard budget caps enforced in code. Agent literally cannot spend more than the limit. Plus Locus provides additional guardrails.

**Q: What if an API goes down mid-payment?**
A: Stripe handles payment failures automatically with retries. For crypto, transactions are atomic - either full completion or full refund.

**Q: Can agents buy from each other?**
A: Yes! That's the vision. Agent A discovers a molecule, lists it. Agent B buys it via x402. Pure machine-to-machine commerce.

---

## Key Metrics for Demo

- **Payment Speed**: <2 seconds for crypto, ~3 seconds for Stripe
- **Transaction Costs**: $0.01 crypto fees vs 2.9% + $0.30 Stripe fees
- **Budget Enforcement**: 100% - agent cannot exceed limits
- **API Cost Range**: $0.005 (toxicity) to $0.10 (AlphaFold2 structure)
- **Networks Supported**: Base Sepolia (testnet), Base Mainnet (production)

---

## Future Enhancements

1. **Multi-Agent Marketplace**: Agents buying/selling data to each other
2. **Dynamic Pricing**: API costs adjust based on demand
3. **Payment Streaming**: Pay-as-you-go for long-running computations
4. **Lightning Network**: Even faster/cheaper micropayments
5. **Smart Contract Escrow**: Hold payments until quality verified

---

## Closing Statement

"Chimera shows the future of autonomous AI commerce. Agents that can discover drugs, evaluate their safety, and transact for services - all without human intervention. We've combined the best of traditional payments (Stripe for human UX) with the best of crypto (x402 for autonomous agent payments). This is how AI agents will operate in the real economy."
