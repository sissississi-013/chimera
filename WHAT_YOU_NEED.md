# 🎯 WHAT YOU NEED TO PROVIDE - Quick Reference

## TL;DR - Get These API Keys

Copy this checklist and fill it in as you go:

```
CRITICAL (Must Have):
[ ] Stripe Secret Key: sk_test_________________________
[ ] Stripe Publishable Key: pk_test_________________________
[ ] Stripe Webhook Secret: whsec_________________________
[ ] Coinbase CDP API Key ID: ________________________
[ ] Coinbase CDP API Secret: ________________________
[ ] Agent Wallet Address: 0x________________________

IMPORTANT (For Drug Discovery):
[ ] NVIDIA API Key: ________________________
   OR
[ ] Hugging Face Token: hf_________________________

OPTIONAL (Nice to Have):
[ ] Locus API Key: ________________________
[ ] NeuroSnap API Key: ________________________
```

---

## Step-by-Step: What to Do Right Now

### 1. Stripe (5 minutes)
**Go to:** https://dashboard.stripe.com/test/apikeys

**Get:**
- Secret key (starts with `sk_test_`)
- Publishable key (starts with `pk_test_`)

**Then go to:** https://dashboard.stripe.com/test/webhooks
- Click "Add endpoint"
- URL: `https://YOUR_NGROK_URL/api/stripe/webhook` (we'll set up ngrok later)
- Select events: `checkout.session.completed`, `payment_intent.succeeded`
- Get: Webhook secret (starts with `whsec_`)

### 2. Coinbase (10 minutes)
**Go to:** https://portal.cdp.coinbase.com/

**Do:**
1. Create account
2. Create new project
3. Generate API key
4. Download the JSON file - it has your:
   - API Key ID
   - API Key Secret
   - Wallet Secret

5. **Create wallet** (I'll give you a script for this)
6. **Fund wallet:** Go to https://faucet.quicknode.com/base/sepolia
   - Enter your wallet address
   - Get free test USDC

### 3. NVIDIA BioNeMo (5-15 minutes)
**Go to:** https://ngc.nvidia.com/setup/api-key

**Do:**
1. Sign up/log in
2. Click "Generate API Key"
3. Copy the key

**Optional:** Request BioNeMo access at https://www.nvidia.com/en-us/gpu-cloud/bionemo/
- May take a few hours to approve
- In the meantime, we can use Hugging Face as fallback

### 4. Hugging Face (Fallback - 2 minutes)
**Go to:** https://huggingface.co/settings/tokens

**Do:**
1. Create account
2. New token → "Read" access
3. Copy token (starts with `hf_`)

---

## What I'll Do With These Keys

Once you provide the keys, I will:

1. ✅ Create `.env` file with all your credentials
2. ✅ Set up payment webhooks
3. ✅ Configure the agent's crypto wallet
4. ✅ Integrate drug discovery APIs
5. ✅ Test everything works
6. ✅ Get the demo running

---

## Fast Track (If You're in a Hurry)

**Minimum to get started:**
1. Stripe keys (3 total) - 5 mins
2. Coinbase keys (3 values) - 10 mins
3. ONE AI key (NVIDIA or Hugging Face) - 5 mins

**Total: 20 minutes** and we can start!

---

## How to Give Me the Keys

**Option 1: Paste here** (I'll create the .env file)
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
...etc
```

**Option 2: Tell me which ones you have**
"I got Stripe and Coinbase set up, here are my keys..."

**Option 3: Follow SETUP_GUIDE.md yourself**
Then just tell me "Done! .env file is ready"

---

## I Don't Have Time for All This!

**No problem!** Set this in `.env`:
```
DEMO_MODE=true
MOCK_PAYMENTS=true
USE_LOCAL_MODELS=true
```

This will:
- Simulate payments (no real Stripe/Coinbase needed)
- Use free local models (no NVIDIA needed)
- Still show the full UI and workflow
- Perfect for initial development/testing

**You can add real APIs later when you have them!**

---

## What's Next?

After you get the keys:

1. **I'll create your `.env` file**
2. **We'll install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up ngrok for webhooks:**
   ```bash
   brew install ngrok  # or download from ngrok.com
   ngrok http 8000
   ```

4. **Start everything up!**

---

## Questions?

**Q: Do I need ALL of these?**
A: No! Start with Stripe + Coinbase + one AI service. Add more later.

**Q: What if an API doesn't approve me in time?**
A: Use fallbacks! Set `ENABLE_FALLBACKS=true` and we'll use local models.

**Q: This is overwhelming!**
A: Start with `DEMO_MODE=true` - get the app running first, add real APIs later!

**Q: How much will this cost?**
A: $0 for testing! Everything has a free tier or test mode.

---

**Ready? Let's get those API keys! 🚀**

Just paste what you have, and I'll take it from there.
