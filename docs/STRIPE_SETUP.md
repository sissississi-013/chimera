# Stripe Integration Setup for Chimera

## Overview
Chimera uses Stripe to enable monetization of discovered molecules. Users can purchase molecules from the marketplace using credit cards or other payment methods supported by Stripe.

## Installation Complete ✓

Stripe CLI is installed and configured with your test API key.

## Configuration

Your `.env` file has been created with:
- `STRIPE_SECRET_KEY`: Your test mode secret key (starts with `sk_test_`)
- `STRIPE_PUBLISHABLE_KEY`: (needs to be added)
- `STRIPE_WEBHOOK_SECRET`: (will be generated when setting up webhooks)

## Quick Start

### 1. Test Your Connection
```bash
stripe balance retrieve
```

### 2. Use the Helper Script
Run the interactive Stripe helper:
```bash
./scripts/stripe_helpers.sh
```

This provides a menu-driven interface for common operations:
- Check balance
- Create products (molecule listings)
- Create prices
- Manage customers
- Test payments
- Listen to webhooks

### 3. Manual Commands

**List Products:**
```bash
stripe products list --limit 10
```

**Create a Molecule Product:**
```bash
stripe products create \
  --name "EGFR_inhibitor_001" \
  --description "Novel EGFR kinase inhibitor with high binding affinity" \
  --metadata[type]="molecule" \
  --metadata[smiles]="CC(=O)Oc1ccccc1C(=O)O" \
  --metadata[molecular_weight]="180.16" \
  --metadata[toxicity_score]="0.23"
```

**Create a Price for a Product:**
```bash
stripe prices create \
  --product prod_XXXXXXXX \
  --unit-amount 50000 \
  --currency usd
```
(Amount is in cents, so 50000 = $500.00)

**Create a Test Customer:**
```bash
stripe customers create \
  --email "researcher@university.edu" \
  --name "Dr. Jane Smith" \
  --description "Research lab customer"
```

**Create a Payment Intent:**
```bash
stripe payment_intents create \
  --amount 50000 \
  --currency usd \
  --payment-method-types card \
  --description "Molecule purchase: EGFR_inhibitor_001"
```

## Webhook Setup for Local Development

### 1. Start Webhook Listener
```bash
stripe listen --forward-to localhost:8000/api/webhook/stripe
```

This will output a webhook signing secret that looks like:
```
whsec_xxxxxxxxxxxxxxxxxxxxx
```

### 2. Add Webhook Secret to .env
Copy the signing secret and add it to your `.env` file:
```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx
```

### 3. Restart Your Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000
```

## Testing Payments

Stripe provides test card numbers for different scenarios:

**Successful Payment:**
- Card: `4242 4242 4242 4242`
- Expiry: Any future date (e.g., 12/34)
- CVC: Any 3 digits (e.g., 123)
- ZIP: Any 5 digits (e.g., 12345)

**Failed Payment:**
- Card: `4000 0000 0000 0002`

**Requires Authentication (3D Secure):**
- Card: `4000 0025 0000 3155`

## Integration with Chimera

### Marketplace Flow

1. **Molecule Discovery** → Agent generates and evaluates molecules
2. **Save to Library** → User saves promising molecules
3. **List on Market** → User selects molecules to sell
4. **Create Stripe Products** → Each molecule becomes a Stripe product
5. **Set Prices** → Assign USD prices to molecules
6. **Customer Purchase** → Buyers pay via Stripe Checkout
7. **Webhook Notification** → Backend processes successful payments
8. **Data Transfer** → Buyer receives molecule data

### API Endpoints (To Be Implemented)

**Create Marketplace Listing:**
```
POST /api/marketplace/listings
{
  "molecule_id": "mol_123",
  "price_usd": 500.00,
  "title": "Novel EGFR Inhibitor",
  "description": "High binding affinity..."
}
```

**Purchase Molecule:**
```
POST /api/marketplace/purchase
{
  "listing_id": "listing_456",
  "payment_method": "stripe"
}
```

## Useful Commands

**View Logs in Real-Time:**
```bash
stripe logs tail
```

**List All Webhooks:**
```bash
stripe webhook-endpoints list
```

**Trigger Test Webhook:**
```bash
stripe trigger payment_intent.succeeded
```

**Refund a Payment:**
```bash
stripe refunds create --payment-intent pi_XXXXXXXX
```

## Resources

- [Stripe Dashboard](https://dashboard.stripe.com/)
- [Stripe API Docs](https://stripe.com/docs/api)
- [Stripe CLI Docs](https://stripe.com/docs/stripe-cli)
- [Test Cards](https://stripe.com/docs/testing)

## Next Steps

1. Get your **Publishable Key** from [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
2. Add it to `.env` as `STRIPE_PUBLISHABLE_KEY`
3. Implement Stripe Checkout in the frontend
4. Create webhook handler in backend
5. Test end-to-end payment flow

## Support

For issues:
- Stripe Support: https://support.stripe.com/
- Chimera Issues: https://github.com/sissississi-013/chimera/issues
