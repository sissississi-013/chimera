# Chimera 🧬

**Autonomous Drug Discovery & Monetization Agent**

Chimera is an autonomous AI agent that discovers novel drug candidates, evaluates them for safety and efficacy, and monetizes the results through data sharing. It demonstrates the integration of AI, chemistry, blockchain micropayments (x402), and autonomous decision-making.

![Chimera Logo](./logo.png)

## Features

- **🧬 Autonomous Molecule Generation**: AI-driven generation of drug-like molecules using scaffold-based methods
- **🔬 Safety & Efficacy Evaluation**: Toxicity prediction, drug-likeness filters (Lipinski's Rule of Five), and efficacy scoring
- **💰 Autonomous Payment Handling**:
  - x402 protocol micropayments via Coinbase CDP wallets
  - Stripe integration for fiat transactions
  - Budget management and cost-benefit analysis
- **📊 Real-time Visualization**: 2D/3D molecular structure rendering
- **🌐 Data Monetization**: Automatic upload to paywalled marketplaces
- **🎯 Decision-Making**: Intelligent iteration, budget allocation, and strategy adjustment

## Architecture

Chimera uses a **modular architecture** with clear separation of concerns:

### Backend (Python + FastAPI)
- **Planning Module**: Creates execution strategy and budget allocation
- **Generation Module**: Generates candidate molecules
- **Evaluation Module**: Assesses safety and efficacy (with API calls)
- **Payment Module**: Handles x402 and Stripe payments autonomously
- **Visualization Module**: Renders molecular structures
- **Data Sharing Module**: Uploads results to marketplaces
- **Orchestrator**: Coordinates all modules and manages workflow

### Frontend (React + TypeScript)
- Interactive form to start discovery runs
- Real-time progress monitoring
- Results visualization with molecule cards
- Budget tracking and transaction history

## Tech Stack

**Backend:**
- Python 3.9+
- FastAPI (REST API)
- RDKit (chemistry/molecule handling)
- Pydantic (data validation)
- asyncio (async execution)

**Frontend:**
- React 18
- TypeScript
- Vite (build tool)
- Axios (API client)

**Payments (Currently Mocked):**
- Coinbase CDP x402 protocol
- Stripe API

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 18+ and npm
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   cd Chimera
   ```

2. **Set up the backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up the frontend:**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

#### Option 1: Run Both Services Manually

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open http://localhost:3000 in your browser.

#### Option 2: Using the Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This will install dependencies and start both services.

## Usage

1. **Start a Discovery Run:**
   - Enter your goal (e.g., "Find a novel EGFR kinase inhibitor")
   - Specify target protein (optional)
   - Set budget (USD)
   - Adjust toxicity threshold
   - Click "Start Discovery"

2. **Monitor Progress:**
   - Watch real-time logs as the agent works
   - See budget utilization
   - View payment transactions as they occur

3. **Review Results:**
   - Examine top molecule candidates
   - View 2D structure visualizations
   - Check safety and efficacy scores
   - See Lipinski's Rule of Five compliance
   - Review monetization results

## API Endpoints

### POST `/api/v1/discover/sync`
Start a synchronous discovery run (waits for completion)

**Request:**
```json
{
  "goal": "Find a novel molecule to inhibit EGFR kinase",
  "target": "EGFR",
  "budget": 5.0,
  "constraints": {
    "max_toxicity": 0.5,
    "min_drug_likeness": 0.6
  }
}
```

**Response:**
```json
{
  "response": {
    "run_id": "run_abc123",
    "status": "success",
    "phase": "completed",
    "molecules_generated": 10,
    "molecules_passed": 3,
    "budget_remaining": 3.25
  },
  "final_report": { ... },
  "molecules": [ ... ]
}
```

### GET `/api/v1/runs`
List all discovery runs

### GET `/api/v1/runs/{run_id}`
Get status of a specific run

### POST `/api/v1/config`
Update agent configuration

## Module Details

### Planning Module
- Analyzes goals and creates execution strategy
- Allocates budget across tasks (generation, evaluation, visualization, monetization)
- Sets evaluation criteria and thresholds
- Plans iteration strategy

### Generation Module
- Scaffold-based molecule generation
- Random functional group addition
- Basic validation and deduplication
- **Future**: Integration with AI generative models

### Evaluation Module
- **Basic Filters**: Lipinski's Rule of Five, molecular weight, LogP, H-bond donors/acceptors
- **Toxicity Prediction**: Calls API (simulated, returns 402 Payment Required)
- **Efficacy Prediction**: Estimates biological activity
- **Decision Logic**: Filters molecules based on criteria, ranks by composite score

### Payment Module
- **x402 Protocol**: Handles HTTP 402 Payment Required challenges
- **CDP Wallet**: Signs payment payloads (simulated)
- **Stripe**: Processes fiat payments (simulated)
- **Budget Management**: Tracks spending, enforces limits
- **Cost-Benefit Analysis**: Decides whether to pay for optional services

### Visualization Module
- Generates 2D molecular structure diagrams
- Creates SVG/PNG images (currently placeholders, production would use RDKit rendering)
- Optional 3D conformer generation

### Data Sharing Module
- Prepares molecule data packages
- Uploads to paywalled marketplace
- Handles listing fees via x402 payment
- Returns listing IDs and URLs

## Configuration

The agent can be configured via the `/api/v1/config` endpoint:

```json
{
  "mock_mode": true,
  "mock_api_mode": true,
  "wallet_balance": 100.0,
  "generate_3d": false
}
```

- `mock_mode`: Use simulated payments (default: true)
- `mock_api_mode`: Use simulated API responses (default: true)
- `wallet_balance`: Initial wallet balance for x402 payments
- `generate_3d`: Enable 3D structure generation

## Development Roadmap

### Phase 1: Core Functionality ✅
- [x] Modular architecture with all core modules
- [x] Mock payment integration (x402 and Stripe)
- [x] Basic molecule generation and evaluation
- [x] FastAPI backend
- [x] React frontend with real-time monitoring

### Phase 2: Real Integrations (In Progress)
- [ ] Integrate real Coinbase CDP wallet for x402 payments
- [ ] Integrate real Stripe API for fiat payments
- [ ] Connect to real toxicity prediction APIs
- [ ] Integrate RDKit for proper molecule rendering
- [ ] Add real AI generative models for molecule generation

### Phase 3: Advanced Features
- [ ] Multi-target optimization
- [ ] QSAR model integration
- [ ] Docking simulations
- [ ] Patent search and novelty checking
- [ ] Collaboration with wet-lab validation
- [ ] NFT minting for molecule IP

### Phase 4: Production Readiness
- [ ] Database persistence (PostgreSQL)
- [ ] Redis for state management
- [ ] WebSocket for real-time updates
- [ ] Authentication and user accounts
- [ ] Rate limiting and security hardening
- [ ] Docker containerization
- [ ] Kubernetes deployment

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests (when added)
cd frontend
npm test
```

## Security Considerations

⚠️ **Important**: The current implementation uses **mock payments** for demonstration. Before deploying with real payments:

1. Secure API keys and wallet credentials (use environment variables, not hardcoded)
2. Implement proper authentication and authorization
3. Add rate limiting to prevent abuse
4. Validate all inputs rigorously
5. Use HTTPS in production
6. Implement proper error handling for payment failures
7. Add transaction logging and monitoring
8. Comply with financial regulations for automated payments

## Contributing

Contributions are welcome! Areas for contribution:
- AI model integration for better molecule generation
- Real API integrations (Coinbase CDP, Stripe, toxicity APIs)
- RDKit integration for chemistry operations
- Additional evaluation metrics
- UI/UX improvements
- Documentation and tutorials

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Inspired by Coinbase's x402 protocol for micropayments
- Built for autonomous AI agent development
- Chemistry operations planned to use RDKit
- UI inspired by modern data science dashboards

## Contact

For questions, issues, or collaboration opportunities, please open an issue on GitHub.

---

**Built with ❤️ for the future of autonomous AI agents in drug discovery**
