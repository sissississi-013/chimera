/**
 * Run Page - Drug discovery execution interface
 */
import React, { useState } from 'react';
import chimeraApi from '../services/api';
import type { AgentRequest, DiscoveryResult } from '../types';
import ResultsDashboard from './ResultsDashboard';
import AgentThinking from './AgentThinking';

interface RunPageProps {
  onNavigate: (page: string) => void;
}

const RunPage: React.FC<RunPageProps> = ({ onNavigate }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<DiscoveryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [goal, setGoal] = useState('Find a novel molecule to inhibit EGFR kinase');
  const [target, setTarget] = useState('EGFR');
  const [budget, setBudget] = useState(5.0);
  const [maxToxicity, setMaxToxicity] = useState(0.5);
  const [logs, setLogs] = useState<string[]>([]);
  const [agentThoughts, setAgentThoughts] = useState<any[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const request: AgentRequest = {
      goal,
      target: target || undefined,
      budget,
      constraints: {
        max_toxicity: maxToxicity,
        min_drug_likeness: 0.6,
      },
    };

    try {
      setIsRunning(true);
      setError(null);
      setLogs(['Initializing Chimera agent...']);
      setAgentThoughts([]);

      // Simulate agent thinking process
      simulateAgentThinking();

      // Call API
      const discoveryResult = await chimeraApi.discover(request);

      // Show logs during execution
      if (discoveryResult.response.logs) {
        setLogs(discoveryResult.response.logs);
      }

      setResult(discoveryResult);
      setIsRunning(false);
    } catch (err) {
      setError((err as Error).message);
      setIsRunning(false);
    }
  };

  const simulateAgentThinking = () => {
    const thoughts = [
      { time: 0, phase: 'planning', thought: 'Analyzing goal and creating execution strategy...' },
      { time: 500, phase: 'planning', thought: 'Allocating budget: 60% evaluation, 20% monetization, 10% reserve' },
      { time: 1000, phase: 'generation', thought: 'Selecting molecular scaffolds for generation...' },
      { time: 1500, phase: 'generation', thought: 'Generated 10 candidate molecules' },
      { time: 2000, phase: 'evaluation', thought: 'Applying Lipinski\'s Rule of Five filters...' },
      { time: 2500, phase: 'evaluation', thought: 'Deciding: Call toxicity API? Cost: $0.05. Budget allows. Proceeding...' },
      { time: 3000, phase: 'payment', thought: 'Received HTTP 402 Payment Required. Signing payment payload...' },
      { time: 3500, phase: 'payment', thought: 'Payment authorized via CDP wallet. Retrying API call...' },
      { time: 4000, phase: 'evaluation', thought: 'Toxicity data received. Molecule_1: 0.23 (PASS)' },
      { time: 4500, phase: 'evaluation', thought: 'Evaluating efficacy. Validating dataset reliability...' },
      { time: 5000, phase: 'decision', thought: 'Debating: Use expensive efficacy API? Expected value analysis...' },
      { time: 5500, phase: 'decision', thought: 'Decision: Yes. Potential benefit exceeds cost. Budget: $4.25 remaining' },
      { time: 6000, phase: 'visualization', thought: 'Rendering molecular structures for top 3 candidates...' },
      { time: 6500, phase: 'monetization', thought: 'Preparing data package for marketplace upload...' },
      { time: 7000, phase: 'monetization', thought: 'Marketplace requires $0.20 listing fee. Authorizing payment...' },
      { time: 7500, phase: 'completed', thought: 'Discovery complete. 3 molecules monetized successfully.' },
    ];

    thoughts.forEach((thought) => {
      setTimeout(() => {
        setAgentThoughts((prev) => [...prev, thought]);
      }, thought.time);
    });
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
    setIsRunning(false);
    setLogs([]);
    setAgentThoughts([]);
  };

  if (result) {
    return (
      <div className="run-page">
        <ResultsDashboard result={result} onReset={handleReset} />
      </div>
    );
  }

  return (
    <div className="run-page">
      <div className="run-container">
        <div className="run-header">
          <h1>Discovery Run</h1>
          <p>Configure and execute autonomous drug discovery</p>
        </div>

        <div className="run-content">
          <div className="run-form-container">
            <form onSubmit={handleSubmit} className="run-form">
              <div className="form-group">
                <label>Discovery Goal</label>
                <textarea
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="Describe what you want to discover..."
                  rows={3}
                  required
                  disabled={isRunning}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Target</label>
                  <input
                    type="text"
                    value={target}
                    onChange={(e) => setTarget(e.target.value)}
                    placeholder="e.g., EGFR, VEGFR"
                    disabled={isRunning}
                  />
                </div>

                <div className="form-group">
                  <label>Budget (USD)</label>
                  <input
                    type="number"
                    value={budget}
                    onChange={(e) => setBudget(parseFloat(e.target.value))}
                    min="0.1"
                    max="100"
                    step="0.1"
                    required
                    disabled={isRunning}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Max Toxicity Threshold: {maxToxicity.toFixed(2)}</label>
                <input
                  type="range"
                  value={maxToxicity}
                  onChange={(e) => setMaxToxicity(parseFloat(e.target.value))}
                  min="0"
                  max="1"
                  step="0.05"
                  disabled={isRunning}
                  className="slider"
                />
              </div>

              <button type="submit" className="run-button" disabled={isRunning}>
                {isRunning ? 'Running...' : 'Execute Discovery'}
              </button>
            </form>
          </div>

          {isRunning && (
            <div className="agent-activity">
              <AgentThinking thoughts={agentThoughts} />

              <div className="activity-logs">
                <h3>System Logs</h3>
                <div className="logs-container">
                  {logs.map((log, index) => (
                    <div key={index} className="log-entry">
                      {log}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="error-container">
              <h3>Error</h3>
              <p>{error}</p>
              <button onClick={handleReset} className="reset-button">
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RunPage;
