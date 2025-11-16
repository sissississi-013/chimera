# Locus Integration Setup Guide for Chimera

## Overview
This guide will help you integrate Locus for REAL crypto payments during molecule generation. We'll configure Locus to handle payments for the **Neurosnap Toxicity API** - every toxicity check will require actual USDC payment approval from your Locus wallet.

## What You'll Need
- 10-15 minutes
- USDC on Base Network (for payments)
- Your Locus wallet address (already configured): `0x3859872d208f9c144adaa56bee126cdcc1e2d71a`

---

## Step 1: Sign Up for Locus

1. Go to **https://app.paywithlocus.com**
2. Click "Sign Up" or "Create Account"
3. Complete registration with your email

---

## Step 2: Create Your Wallet

1. Navigate to **https://app.paywithlocus.com/dashboard/wallets**
2. Click "Create New Wallet" or "Add Wallet"
3. Configure:
   - **Chain**: Base Mainnet (for production) or Base Sepolia (for testing)
   - **Wallet Name**: "Chimera Drug Discovery Wallet"
4. **IMPORTANT**: Download the private key JSON file (you'll never see it again!)
5. Click "Deploy Wallet"

**Result**: You'll see your wallet address and $0.00 balance

---

## Step 3: Fund Your Wallet

### Option A: Using Coinbase OnRamp (Recommended)
1. In your wallet dashboard, click "Add Funds"
2. Follow Coinbase OnRamp instructions
3. Purchase **USDC on Base Network**
4. Start with $10-20 USDC for testing

### Option B: Transfer Existing USDC
If you already have USDC on Base:
1. Send USDC to your wallet address: `0x3859872d208f9c144adaa56bee126cdcc1e2d71a`
2. Use Base Network (NOT Ethereum mainnet)
3. Wait 1-2 minutes for confirmation

**Verify**: Refresh your wallet dashboard - balance should show your USDC amount

---

## Step 4: Create a Policy Group

This controls how your AI agent can spend money.

1. Go to **https://app.paywithlocus.com/dashboard/agents**
2. Click "Create Policy Group" or "New Policy"
3. Configure:
   - **Name**: "Chimera Discovery Policy"
   - **Associated Wallet**: Select your wallet from dropdown
   - **Monthly Budget**: $100 (or your preferred limit)
   - **Agent Permissions**: Enable all three options:
     - ✅ Allow agents to send funds to email addresses
     - ✅ Allow agents to send funds to wallet addresses
     - ✅ Allow agents to send funds to contacts

4. **Whitelist Contacts** (Optional):
   - Navigate to "Contacts" tab or https://app.paywithlocus.com/dashboard/contacts
   - Add trusted vendor addresses (e.g., Neurosnap payment address)

5. Click "Create Policy Group"

**Result**: Your policy group is now active

---

## Step 5: Get Your API Credentials

You have two options:

### Option A: API Key (Simple - Recommended for Chimera)
1. Go to **https://app.paywithlocus.com/dashboard/agents**
2. Click "Create Agent"
3. Enter:
   - **Name**: "Chimera Drug Discovery Agent"
   - **Memo**: "Autonomous agent for molecule toxicity payments"
4. **Enable**: "Generate API Key"
5. Click "Create Agent"
6. **COPY THIS IMMEDIATELY**:
   - **API Key**: `locus_...` (starts with locus_)

### Option B: OAuth (More Secure - For Production)
Same steps but copy:
- **Client ID**: `client_...`
- **Client Secret**: `secret_...`

**IMPORTANT**: Save these to a secure location - you can't retrieve them later!

---

## Step 6: Update Your Chimera .env File

Open `/Users/sissi/Chimera/.env` and update:

```bash
# ----- LOCUS (Spending Controls) -----
LOCUS_WALLET_ADDRESS=0x3859872d208f9c144adaa56bee126cdcc1e2d71a
LOCUS_API_KEY=locus_your_api_key_here  # Replace with your actual API key
LOCUS_API_URL=https://api.paywithlocus.com/v1

# Or if using OAuth:
LOCUS_CLIENT_ID=client_your_id_here
LOCUS_CLIENT_SECRET=secret_your_secret_here
```

Save the file and restart your backend:
```bash
cd /Users/sissi/Chimera/backend
# Kill existing backend (Ctrl+C)
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000
```

---

## Step 7: Test Your Integration

1. **Check Wallet Status**:
   ```bash
   curl -X GET http://localhost:8000/api/v1/wallet/status
   ```

   Should return your wallet balance and spending limits.

2. **Run a Discovery** (with real payment):
   - Open http://localhost:3000
   - Navigate to "Run" page
   - Chat with Chimera to plan a discovery
   - Click "Start Discovery Run"

3. **Watch for Payment**:
   - When Neurosnap toxicity check is called (~$0.005 per molecule)
   - Locus will be queried for approval
   - USDC payment will be executed on Base Network
   - Check your Locus dashboard to see the transaction

---

## How It Works in Chimera

### Payment Flow:
```
1. Agent needs toxicity prediction
   ↓
2. Call Locus API: request_payment_approval()
   - Amount: $0.005 per molecule
   - Vendor: "neurosnap"
   - Description: "Toxicity prediction for molecule XYZ"
   ↓
3. Locus checks:
   - Sufficient balance?
   - Within policy limits?
   - Approved vendor?
   ↓
4. If approved:
   - Execute USDC payment on Base
   - Return transaction ID
   ↓
5. Call Neurosnap API with payment proof
   ↓
6. Agent receives toxicity data
```

### Cost Estimates:
- **Neurosnap Toxicity**: $0.005 per molecule
- **10 molecules**: $0.05 total
- **50 molecules**: $0.25 total
- **100 molecules**: $0.50 total

---

## Monitoring Your Spending

### View Transaction History:
1. Go to https://app.paywithlocus.com/dashboard/transactions
2. See all payments made by your agent
3. Export to CSV for accounting

### Set Up Alerts:
1. Configure email notifications for:
   - Large transactions (>$1.00)
   - Budget warnings (75% threshold)
   - Policy violations

---

## Troubleshooting

### "LOCUS_API_KEY is PENDING"
- You haven't created an agent in the Locus dashboard yet
- Follow Step 5 to generate credentials

### "Insufficient balance"
- Fund your wallet with more USDC (Step 3)
- Check balance at https://app.paywithlocus.com/dashboard/wallets

### "Payment rejected by policy"
- Check your policy group limits
- Verify the vendor is whitelisted (if using whitelist)
- Ensure you haven't exceeded daily/monthly budget

### "Wallet not found"
- Double-check wallet address in .env matches Locus dashboard
- Verify you've deployed the wallet (not just created it)

---

## Production Checklist

Before going live:
- [ ] Switch from Base Sepolia Testnet to Base Mainnet
- [ ] Fund wallet with sufficient USDC
- [ ] Set conservative spending limits in policy group
- [ ] Use OAuth credentials (not API Key) for better security
- [ ] Enable webhook notifications for payment events
- [ ] Set up email alerts for budget thresholds
- [ ] Whitelist only trusted vendor addresses
- [ ] Test with small amounts first ($1-5)

---

## Next Steps

Once configured:
1. The agent will automatically use Locus for ALL Neurosnap toxicity checks
2. Every API call will require real USDC payment
3. You can track spending in real-time on your Locus dashboard
4. Budget limits will prevent overspending

## Questions?
- Locus Docs: https://docs.paywithlocus.com
- Locus Support: support@paywithlocus.com
- Locus Discord: https://discord.gg/locus
