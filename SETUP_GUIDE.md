# Chimera Autonomous Agent - Complete Setup Guide

## Overview
This guide will walk you through setting up all the necessary accounts, API keys, and integrations for the Chimera autonomous drug discovery agent with payment capabilities.

---

## 🔑 Part 1: Account Setup & API Key Collection

### 1. Stripe (Fiat Payments) ⚡
**Purpose:** Handle traditional credit card payments for funding the agent

**Steps:**
1. Go to [stripe.com](https://stripe.com) and create an account
2. Activate **Test Mode** (toggle in top-right of dashboard)
3. Navigate to **Developers → API Keys**
4. Copy these values to your `.env` file:
   - `STRIPE_SECRET_KEY` (starts with `sk_test_...`)
   - `STRIPE_PUBLISHABLE_KEY` (starts with `pk_test_...`)

5. **Set up Webhooks:**
   - Go to **Developers → Webhooks**
   - Click **Add endpoint**
   - Enter your webhook URL: `https://YOUR_DOMAIN/api/stripe/webhook`
     - For local dev, use **ngrok**: `ngrok http 8000` and use the https URL
   - Select these events:
     - `checkout.session.completed`
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
   - Copy the **Signing secret** (starts with `whsec_...`) → `STRIPE_WEBHOOK_SECRET`

6. **Test with Stripe CLI** (optional but recommended):
   ```bash
   # Install Stripe CLI: https://stripe.com/docs/stripe-cli
   stripe listen --forward-to localhost:8000/api/stripe/webhook
   stripe trigger payment_intent.succeeded
   ```

---

### 2. Coinbase Developer Platform (CDP) 💰
**Purpose:** Create crypto wallet for agent, enable x402 micropayments

**Steps:**
1. Go to [Coinbase Developer Platform](https://portal.cdp.coinbase.com/)
2. Sign up / Log in
3. Create a new **Project**
4. Navigate to **API Keys** section
5. Create a new API key and download the JSON file
6. Copy these values to `.env`:
   - `CDP_API_KEY_ID`
   - `CDP_API_KEY_SECRET`
   - `CDP_WALLET_SECRET`

7. **Create Agent Wallet:**
   ```bash
   # Install Coinbase SDK
   npm install @coinbase/coinbase-sdk
   # Or for Python:
   pip install coinbase-advanced-py
   ```

   Use the SDK to create a wallet:
   ```python
   from coinbase.wallet.client import Wallet

   # This will generate a new wallet
   wallet = Wallet(api_key, api_secret)
   account = wallet.create_account(name='Chimera Agent Wallet')

   # Copy the address → AGENT_WALLET_ADDRESS
   print(account.address)
   ```

8. **Fund Test Wallet:**
   - Go to [Base Sepolia Faucet](https://faucet.quicknode.com/base/sepolia)
   - Enter your `AGENT_WALLET_ADDRESS`
   - Request test ETH (for gas) and test USDC
   - Verify funds: Check on [Base Sepolia Explorer](https://sepolia.basescan.org/)

9. **x402 Configuration:**
   - Base Sepolia USDC contract: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
   - Network: `base-sepolia`
   - Add to `.env`

---

### 3. Locus (Programmable Spending) 🔒
**Purpose:** Set spending limits and policies for autonomous agent

**Steps:**
1. Sign up at [paywithlocus.com](https://paywithlocus.com)
2. Wait for beta approval (usually quick for hackathon participants)
3. Once approved, go to **Dashboard**
4. Create a new **Agent Identity**:
   - Name: "Chimera Discovery Agent"
   - Link your Base wallet address from step 2
5. Copy `LOCUS_API_KEY` from API section
6. Copy your `LOCUS_AGENT_ID`

7. **Set Spending Policies:**
   - Max per transaction: $0.50
   - Max per day: $10.00
   - Allowed services: Whitelist the APIs you'll call
   - This ensures the agent can't overspend!

---

### 4. NVIDIA BioNeMo (AI Drug Discovery) 🧬
**Purpose:** Molecule generation, protein folding

**Steps:**
1. Go to [NVIDIA NGC](https://ngc.nvidia.com/)
2. Create account / Sign in
3. Navigate to **Setup → Generate API Key**
4. Copy the API key → `NVIDIA_API_KEY`
5. Request access to **BioNeMo Cloud Service**:
   - Go to [BioNeMo](https://www.nvidia.com/en-us/gpu-cloud/bionemo/)
   - Click "Request Access" or "Get Started"
   - May need to fill out a form stating use case (mention hackathon)
6. Once approved, you'll get access to endpoints like:
   - `https://health.api.nvidia.com/v1/biology/nvidia/molmim/generate`
   - `https://health.api.nvidia.com/v1/biology/meta/esmfold`

**Test the API:**
```bash
curl -X POST "https://health.api.nvidia.com/v1/biology/meta/esmfold" \
  -H "Authorization: Bearer YOUR_NVIDIA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sequence": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNL"}'
```

---

### 5. Hugging Face (Optional - Open Source Models) 🤗
**Purpose:** Fallback models if NVIDIA unavailable

**Steps:**
1. Go to [huggingface.co](https://huggingface.co)
2. Sign up / Log in
3. Go to **Settings → Access Tokens**
4. Create new token with "Read" permissions
5. Copy to `.env` → `HUGGINGFACE_API_TOKEN`

**Useful models:**
- `ncfrey/ChemGPT-1.2B` (molecule generation)
- `facebook/esm2_t33_650M_UR50D` (protein embeddings)

---

### 6. NeuroSnap (Toxicity Prediction) ☠️
**Purpose:** Predict molecule toxicity and synthesizability

**Steps:**
1. Go to [neurosnap.ai](https://neurosnap.ai)
2. Sign up for an account
3. Navigate to **API Access**
4. Generate API key
5. Copy to `.env` → `NEUROSNAP_API_KEY`

**Alternative (Free):** Use local RDKit for basic toxicity checks
- No API key needed
- Included in requirements.txt
- Less accurate but instant

---

## 📦 Part 2: Installation

### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp ../.env.example ../.env

# Edit .env with your API keys
nano ../.env  # or use any text editor
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Should be ready to go!
```

---

## ⚙️ Part 3: Configuration

### Edit your `.env` file

Copy the `.env.example` to `.env` and fill in all the values you collected:

```bash
cp .env.example .env
```

**Required for Basic Operation:**
- `STRIPE_SECRET_KEY` ✅
- `CDP_API_KEY_ID` ✅
- `CDP_API_KEY_SECRET` ✅
- `AGENT_WALLET_ADDRESS` ✅

**Required for Drug Discovery:**
- `NVIDIA_API_KEY` ✅ (or `HUGGINGFACE_API_TOKEN` as fallback)

**Optional but Recommended:**
- `LOCUS_API_KEY` (for spending controls)
- `NEUROSNAP_API_KEY` (for toxicity)

**Development Settings:**
- Set `PAYMENT_MODE=test` for testing
- Set `DEMO_MODE=true` to bypass payments during development
- Set `ENABLE_FALLBACKS=true` to use local models if APIs fail

---

## 🧪 Part 4: Testing Setup

### 1. Test Stripe
```bash
# In terminal, start webhook forwarding
stripe listen --forward-to localhost:8000/api/stripe/webhook

# In another terminal, start backend
cd backend && source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000

# Trigger test payment
stripe trigger checkout.session.completed
```

### 2. Test Coinbase Wallet
```python
# Quick wallet test
python backend/test_wallet.py
# Should show: Wallet address: 0x... Balance: X USDC
```

### 3. Test NVIDIA API
```bash
curl -X POST "http://localhost:8000/api/test/nvidia" \
  -H "Content-Type: application/json"
# Should return: {"status": "ok", "service": "nvidia_bionemo"}
```

---

## 🚀 Part 5: Running the Application

### Start Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🎯 Part 6: For Demo/Hackathon

### Quick Start with Mock Data
If you don't have all APIs set up yet:

1. Set in `.env`:
   ```
   DEMO_MODE=true
   MOCK_PAYMENTS=true
   USE_LOCAL_MODELS=true
   ```

2. This will:
   - Bypass real payments
   - Use cached/mock results
   - Run local RDKit for basic checks
   - Still show the full UI flow

### Making it Public (for Demo)
```bash
# Install ngrok
brew install ngrok  # or download from ngrok.com

# Expose backend
ngrok http 8000

# Copy the https URL (e.g., https://abc123.ngrok.io)
# Update WEBHOOK_BASE_URL in .env
```

---

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt --upgrade
```

### Stripe webhook not receiving events
- Make sure `stripe listen` is running
- Check that STRIPE_WEBHOOK_SECRET matches
- Verify ngrok URL is correct in Stripe dashboard

### Wallet has no funds
- Use Base Sepolia faucet again
- Check block explorer to verify transaction
- May need to wait a few seconds for confirmation

### API rate limits
- NVIDIA: Free tier has limits, wait or upgrade
- Hugging Face: Rate limited to X requests/hour on free tier
- Use `ENABLE_FALLBACKS=true` to switch to local models

---

## 📚 Additional Resources

- [Stripe API Docs](https://stripe.com/docs/api)
- [Coinbase x402 Protocol](https://docs.cdp.coinbase.com/x402/docs)
- [NVIDIA BioNeMo Docs](https://docs.nvidia.com/bionemo/)
- [RDKit Documentation](https://www.rdkit.org/docs/)
- [Base Sepolia Testnet](https://docs.base.org/network-information/)

---

## ✅ Checklist

Before running Chimera, ensure you have:

- [ ] Stripe test keys configured
- [ ] Coinbase CDP wallet created and funded
- [ ] Agent wallet has test USDC and ETH
- [ ] NVIDIA API key (or Hugging Face token)
- [ ] .env file completely filled out
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Webhook endpoint accessible (ngrok if local)
- [ ] Tested at least one payment flow
- [ ] Tested at least one API call

---

**You're ready to run Chimera! 🎉**

For questions or issues, check the main README.md or open an issue on GitHub.
