# Chimera Architecture Documentation

## Overview

Chimera is built as a **modular, autonomous agent system** with clear separation between planning, execution, payment handling, and user interface layers.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────────┐  │
│  │Discovery │  │Results   │  │  Molecule Cards     │  │
│  │  Form    │  │Dashboard │  │  & Visualization    │  │
│  └──────────┘  └──────────┘  └─────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│              Backend FastAPI Server                      │
│  ┌───────────────────────────────────────────────────┐ │
│  │            Agent Orchestrator                     │ │
│  │  (Coordinates all modules, manages workflow)     │ │
│  └───────────────────────────────────────────────────┘ │
│         │         │         │         │         │       │
│    ┌────▼────┐ ┌─▼──────┐ ┌▼────────┐ ┌───▼────┐      │
│    │Planning │ │Generate│ │Evaluate │ │Payment │      │
│    │ Module  │ │ Module │ │ Module  │ │ Module │      │
│    └─────────┘ └────────┘ └─────────┘ └────────┘      │
│         │                     │                          │
│    ┌────▼───────┐      ┌─────▼──────────┐              │
│    │Visualize   │      │  Data Sharing  │              │
│    │  Module    │      │     Module     │              │
│    └────────────┘      └────────────────┘              │
└─────────────────────────────────────────────────────────┘
                     │              │
        ┌────────────▼─────┐  ┌────▼──────────┐
        │ Mock x402 APIs   │  │ Mock Stripe   │
        │ (Toxicity, etc.) │  │   Payments    │
        └──────────────────┘  └───────────────┘
```

## Backend Architecture

### Core Components

#### 1. Agent Orchestrator (`orchestrator.py`)
**Responsibility**: Main controller that coordinates all modules

**Key Functions**:
- Initialize and execute modules in correct order
- Manage agent state throughout execution
- Handle iteration logic (retry if no candidates found)
- Adjust strategy based on results
- Generate final reports

**Flow**:
```
Planning → Generation → Evaluation → Visualization → Monetization
   ↑                                                        │
   └─────────────── (if needed, iterate) ─────────────────┘
```

#### 2. Planning Module (`modules/planning.py`)
**Responsibility**: Create execution strategy and allocate resources

**Inputs**:
- User goal
- Target protein/disease
- Budget
- Constraints

**Outputs**:
- Execution plan with ordered steps
- Budget allocation across tasks
- Evaluation criteria and thresholds
- Success criteria

**Budget Allocation Strategy**:
- 5% generation
- 60% evaluation (most expensive)
- 5% visualization
- 20% monetization
- 10% reserve

#### 3. Generation Module (`modules/generation.py`)
**Responsibility**: Create candidate drug molecules

**Methods**:
- **Scaffold-based**: Start with known drug scaffolds (benzene, quinoline, etc.)
- **Functional group addition**: Add drug-like groups (amide, hydroxyl, etc.)
- **Validation**: Basic SMILES validation and deduplication

**Output**: List of Molecule objects with SMILES notation

**Future Enhancements**:
- AI generative models (Transformer-based, VAE, GAN)
- Reinforcement learning for optimization
- Fragment-based design

#### 4. Evaluation Module (`modules/evaluation.py`)
**Responsibility**: Assess molecules for safety and efficacy

**Evaluation Pipeline**:

1. **Basic Filters** (free, local):
   - Lipinski's Rule of Five
   - Molecular weight ≤ 500 Da
   - LogP ≤ 5
   - H-bond donors ≤