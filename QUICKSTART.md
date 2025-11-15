# Chimera Quick Start Guide 🚀

Get Chimera up and running in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed
- Terminal/command line access

## Step 1: Installation

Run the setup script:

```bash
./setup.sh
```

This will:
- Install Python dependencies (FastAPI, Pydantic, etc.)
- Install Node dependencies (React, TypeScript, Vite)
- Set up virtual environments

## Step 2: Start the Application

Run both backend and frontend:

```bash
./run.sh
```

Or start them manually in separate terminals:

**Terminal 1 (Backend):**
```bash
cd backend
python -m uvicorn api.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

## Step 3: Access the Application

Open your browser and navigate to:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Step 4: Run Your First Discovery

1. In the web interface, you'll see a form
2. Enter a goal like: "Find a novel EGFR kinase inhibitor"
3. Set a budget (e.g., $5.00)
4. Click "Start Discovery"
5. Watch the agent work in real-time!

## Example Discovery Request

Try this goal:

**Goal:** "Find a novel molecule to inhibit EGFR kinase with low toxicity"

**Target:** EGFR

**Budget:** $5.00

**Max Toxicity:** 0.5

The agent will:
1. ✅ Create an execution plan
2. ✅ Generate 10 candidate molecules
3. ✅ Filter by drug-likeness (Lipinski's rules)
4. ✅ Predict toxicity (with mock payment)
5. ✅ Predict efficacy (with mock payment)
6. ✅ Visualize top candidates
7. ✅ Upload to marketplace (with mock payment)
8. ✅ Return results with budget breakdown

## What to Expect

You should see:
- **Real-time logs** showing agent progress
- **Payment transactions** for API calls (mocked)
- **Molecule visualizations** (2D structures)
- **Safety scores** (toxicity < 0.5 = safe)
- **Budget tracking** (spent vs. remaining)
- **Monetization confirmation** (listing IDs)

## Understanding the Results

### Molecule Card

Each passing molecule shows:
- **Name** and **SMILES** notation
- **2D structure** visualization
- **Toxicity score** (0-1, lower is better)
- **Efficacy score** (0-1, higher is better)
- **Molecular weight**, **LogP**, etc.
- **Lipinski's Rule of Five** compliance

### Budget Breakdown

The agent allocates budget:
- **5%** for generation (mostly free)
- **60%** for evaluation (API calls)
- **5%** for visualization (mostly free)
- **20%** for monetization (listing fees)
- **10%** reserve (for retries)

### Transactions

You'll see simulated payments for:
- **Toxicity checks** ($0.05 each)
- **Efficacy predictions** ($0.10 each)
- **Marketplace listing** ($0.20 each)

## Troubleshooting

### Backend won't start

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend won't start

```bash
cd frontend
npm install
npm run dev
```

### Port already in use

Change the port in the run script or:

```bash
# Backend on different port
uvicorn api.main:app --port 8001

# Frontend will proxy to backend automatically
```

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Try different goals**: Experiment with different targets
3. **Adjust budgets**: See how it affects results
4. **Read the docs**: Check out README.md for architecture details

## Need Help?

- Check the logs in the web interface
- Look at terminal output for errors
- Open an issue on GitHub
- Read the full README.md

## Example curl Request

Test the API directly:

```bash
curl -X POST http://localhost:8000/api/v1/discover/sync \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Find a novel EGFR inhibitor",
    "target": "EGFR",
    "budget": 5.0,
    "constraints": {
      "max_toxicity": 0.5
    }
  }'
```

---

**You're all set! Happy drug discovering! 🧬💊**
