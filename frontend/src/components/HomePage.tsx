/**
 * Home Page - Landing page for Chimera
 */
import React from 'react';

interface HomePageProps {
  onNavigate: (page: string) => void;
}

const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  return (
    <div className="home-page">
      <div className="home-hero">
        <img src="/logo.png" alt="Chimera" className="home-logo-large" />
        <p className="home-subtitle">
          AI That <em>Designs</em> Molecules, <em>Pays</em> to Play,<br />
          and <em>Gets Paid</em> to <em>Share</em>.
        </p>

        <button className="home-cta" onClick={() => onNavigate('run')}>
          Start Discovery
        </button>
      </div>

      <div className="home-features">
        <div className="feature-section">
          <h2>What is Chimera?</h2>
          <p>
            Chimera is an autonomous AI-powered platform that revolutionizes drug discovery
            through intelligent automation, blockchain micropayments, and decentralized data markets.
            Our system combines cutting-edge AI with economic intelligence to discover novel
            molecular candidates, evaluate them for safety and efficacy, and monetize the results.
          </p>
        </div>

        <div className="feature-grid">
          <div className="feature-card">
            <h3>Autonomous Discovery</h3>
            <p>
              AI agents autonomously generate novel molecular structures using scaffold-based
              generation and advanced algorithms. The system intelligently explores chemical
              space to identify promising drug candidates.
            </p>
          </div>

          <div className="feature-card">
            <h3>Intelligent Evaluation</h3>
            <p>
              Multi-stage evaluation pipeline includes Lipinski's Rule of Five filtering,
              toxicity prediction via external APIs, efficacy scoring, and composite ranking.
              Every decision is made with cost-benefit analysis.
            </p>
          </div>

          <div className="feature-card">
            <h3>Economic Intelligence</h3>
            <p>
              Built-in budget management with x402 micropayments and Stripe integration.
              The agent autonomously decides when to spend resources, handling HTTP 402
              payment challenges seamlessly using Coinbase CDP wallets.
            </p>
          </div>

          <div className="feature-card">
            <h3>Decentralized Market</h3>
            <p>
              Discovered molecules are automatically uploaded to paywalled marketplaces,
              enabling true data monetization. Your discoveries become tradeable assets
              on the decentralized scientific data market.
            </p>
          </div>

          <div className="feature-card">
            <h3>Real-Time Monitoring</h3>
            <p>
              Watch your agent work in real-time with detailed logs, transaction tracking,
              and budget visualization. See every decision, every payment, and every
              discovery as it happens.
            </p>
          </div>

          <div className="feature-card">
            <h3>Modular Architecture</h3>
            <p>
              Six specialized modules work in harmony: Planning, Generation, Evaluation,
              Payment, Visualization, and Data Sharing. Each module is independently
              scalable and can integrate with external services.
            </p>
          </div>
        </div>

        <div className="feature-section">
          <h2>How It Works</h2>
          <div className="process-steps">
            <div className="process-step">
              <div className="step-number">01</div>
              <div className="step-content">
                <h4>Planning</h4>
                <p>Agent analyzes your goal and creates an execution strategy with budget allocation</p>
              </div>
            </div>

            <div className="process-step">
              <div className="step-number">02</div>
              <div className="step-content">
                <h4>Generation</h4>
                <p>Generates novel molecular candidates using AI and algorithmic methods</p>
              </div>
            </div>

            <div className="process-step">
              <div className="step-number">03</div>
              <div className="step-content">
                <h4>Evaluation</h4>
                <p>Filters candidates through drug-likeness checks and toxicity prediction</p>
              </div>
            </div>

            <div className="process-step">
              <div className="step-number">04</div>
              <div className="step-content">
                <h4>Visualization</h4>
                <p>Renders 2D/3D structures of top candidates with property analysis</p>
              </div>
            </div>

            <div className="process-step">
              <div className="step-number">05</div>
              <div className="step-content">
                <h4>Monetization</h4>
                <p>Uploads discoveries to marketplace with automatic payment handling</p>
              </div>
            </div>
          </div>
        </div>

        <div className="feature-section cta-section">
          <h2>Ready to Discover?</h2>
          <p>Start your autonomous drug discovery journey now</p>
          <button className="home-cta-large" onClick={() => onNavigate('run')}>
            Launch Chimera Agent
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
