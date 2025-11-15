/**
 * Discovery Form Component - Start new drug discovery runs
 */
import React, { useState } from 'react';
import chimeraApi from '../services/api';
import type { AgentRequest, DiscoveryResult } from '../types';

interface DiscoveryFormProps {
  onStart: () => void;
  onComplete: (result: DiscoveryResult) => void;
  onError: (error: Error) => void;
  isRunning: boolean;
}

const DiscoveryForm: React.FC<DiscoveryFormProps> = ({
  onStart,
  onComplete,
  onError,
  isRunning,
}) => {
  const [goal, setGoal] = useState('Find a novel molecule to inhibit EGFR kinase');
  const [target, setTarget] = useState('EGFR');
  const [budget, setBudget] = useState(5.0);
  const [maxToxicity, setMaxToxicity] = useState(0.5);
  const [logs, setLogs] = useState<string[]>([]);

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
      onStart();
      setLogs(['Starting drug discovery...']);

      // Call API
      const result = await chimeraApi.discover(request);

      // Show logs during execution
      if (result.response.logs) {
        setLogs(result.response.logs);
      }

      onComplete(result);
    } catch (err) {
      onError(err as Error);
    }
  };

  return (
    <div className="discovery-form-container">
      <div className="discovery-card">
        <h2>Start New Discovery Run</h2>

        <form onSubmit={handleSubmit} className="discovery-form">
          <div className="form-group">
            <label htmlFor="goal">Discovery Goal</label>
            <textarea
              id="goal"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="What drug candidate are you looking for?"
              rows={3}
              required
              disabled={isRunning}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="target">Target (Optional)</label>
              <input
                type="text"
                id="target"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="e.g., EGFR, VEGFR"
                disabled={isRunning}
              />
            </div>

            <div className="form-group">
              <label htmlFor="budget">Budget (USD)</label>
              <input
                type="number"
                id="budget"
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
            <label htmlFor="maxToxicity">Maximum Toxicity Threshold</label>
            <input
              type="range"
              id="maxToxicity"
              value={maxToxicity}
              onChange={(e) => setMaxToxicity(parseFloat(e.target.value))}
              min="0"
              max="1"
              step="0.05"
              disabled={isRunning}
            />
            <span className="range-value">{maxToxicity.toFixed(2)}</span>
          </div>

          <button
            type="submit"
            className="btn-primary btn-large"
            disabled={isRunning}
          >
            {isRunning ? 'Running...' : 'Start Discovery'}
          </button>
        </form>

        {/* Live Logs */}
        {isRunning && logs.length > 0 && (
          <div className="logs-container">
            <h3>Agent Logs</h3>
            <div className="logs-box">
              {logs.map((log, index) => (
                <div key={index} className="log-entry">
                  {log}
                </div>
              ))}
            </div>
            <div className="spinner">
              <div className="spinner-circle"></div>
              <p>Agent is working...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiscoveryForm;
