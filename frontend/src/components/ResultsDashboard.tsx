/**
 * Results Dashboard Component - Display discovery results
 */
import React from 'react';
import type { DiscoveryResult, Molecule } from '../types';
import MoleculeCard from './MoleculeCard';

interface ResultsDashboardProps {
  result: DiscoveryResult;
  onReset: () => void;
}

const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ result, onReset }) => {
  const { response, final_report, molecules } = result;
  const passedMolecules = molecules?.filter(m => m.status === 'passed' || m.status === 'monetized') || [];

  const budgetSpent = final_report?.budget_summary?.spent || 0;
  const budgetTotal = final_report?.budget_summary?.total_budget || response.budget_remaining;
  const budgetPercent = (budgetSpent / budgetTotal) * 100;

  return (
    <div className="results-dashboard">
      {/* Header */}
      <div className="results-header">
        <div className="results-title-section">
          <h2>Discovery Results</h2>
          <div className="status-badge" data-status={response.status}>
            {response.status === 'success' ? '✓' : '✗'} {response.status.toUpperCase()}
          </div>
        </div>
        <button onClick={onReset} className="btn-new-run">
          New Discovery Run
        </button>
      </div>

      {/* Status Message */}
      {response.message && (
        <div className="status-message-card">
          <p>{response.message}</p>
        </div>
      )}

      {/* Summary Grid */}
      <div className="summary-grid">
        <div className="summary-card">
          <div className="summary-label">Molecules Generated</div>
          <div className="summary-value">{response.molecules_generated}</div>
          <div className="summary-bar">
            <div className="summary-bar-fill" style={{ width: '100%', background: 'var(--primary)' }}></div>
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Passed Evaluation</div>
          <div className="summary-value">{response.molecules_passed}</div>
          <div className="summary-bar">
            <div
              className="summary-bar-fill"
              style={{
                width: `${(response.molecules_passed / response.molecules_generated) * 100}%`,
                background: 'var(--success)'
              }}
            ></div>
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Budget Spent</div>
          <div className="summary-value">${budgetSpent.toFixed(2)}</div>
          <div className="summary-bar">
            <div
              className="summary-bar-fill"
              style={{
                width: `${budgetPercent}%`,
                background: 'var(--pink)'
              }}
            ></div>
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Iterations</div>
          <div className="summary-value">{final_report?.execution_summary?.iterations || 1}</div>
          <div className="summary-bar">
            <div className="summary-bar-fill" style={{ width: '100%', background: 'var(--accent)' }}></div>
          </div>
        </div>
      </div>

      {/* Budget Bar */}
      <div className="budget-section">
        <h3>Budget Utilization</h3>
        <div className="budget-bar-container">
          <div className="budget-bar">
            <div
              className="budget-bar-fill"
              style={{ width: `${budgetPercent}%` }}
            ></div>
          </div>
          <div className="budget-labels">
            <span>${budgetSpent.toFixed(2)} spent</span>
            <span>${(budgetTotal - budgetSpent).toFixed(2)} remaining</span>
          </div>
        </div>
      </div>

      {/* Transactions */}
      {final_report?.transactions && final_report.transactions.length > 0 && (
        <div className="transactions-section">
          <h3>Payment Transactions</h3>
          <div className="transactions-list">
            {final_report.transactions.map((tx: any) => (
              <div key={tx.id} className="transaction-item">
                <div className="tx-info">
                  <span className="tx-service">{tx.service}</span>
                  <span className="tx-method">{tx.method}</span>
                </div>
                <div className="tx-amount">${tx.amount.toFixed(2)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Molecules */}
      {passedMolecules.length > 0 && (
        <div className="molecules-section">
          <h3>Top Molecules</h3>
          <div className="molecules-grid">
            {passedMolecules.map((molecule) => (
              <MoleculeCard key={molecule.id} molecule={molecule} />
            ))}
          </div>
        </div>
      )}

      {/* Monetization Results */}
      {final_report?.monetization && (
        <div className="monetization-section">
          <h3>Monetization</h3>
          <div className="monetization-card">
            <p>
              Successfully uploaded {final_report.monetization.successful} of{' '}
              {final_report.monetization.attempted} molecules to marketplace
            </p>
            {final_report.monetization.results?.map((r: any, idx: number) => (
              r.success && (
                <div key={idx} className="listing-item">
                  <span>Listing ID: {r.listing_id}</span>
                  {r.listing_url && (
                    <a href={r.listing_url} target="_blank" rel="noopener noreferrer">
                      View →
                    </a>
                  )}
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Logs */}
      {response.logs && response.logs.length > 0 && (
        <div className="logs-section">
          <h3>Execution Logs</h3>
          <div className="logs-box">
            {response.logs.map((log, index) => (
              <div key={index} className="log-entry">
                {log}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsDashboard;
