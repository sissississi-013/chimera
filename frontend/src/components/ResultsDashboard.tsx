/**
 * Results Dashboard Component - Display discovery results with export functionality
 */
import React, { useState } from 'react';
import type { DiscoveryResult, Molecule } from '../types';

interface ResultsDashboardProps {
  result: DiscoveryResult;
  onReset: () => void;
  onSaveToLibrary: (molecules: any[]) => void;
}

const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ result, onReset, onSaveToLibrary }) => {
  const [selectedMolecule, setSelectedMolecule] = useState<Molecule | null>(null);
  const [showExportMenu, setShowExportMenu] = useState(false);

  const { response, final_report, molecules } = result;
  const passedMolecules = molecules?.filter(m => m.status === 'passed' || m.status === 'monetized') || [];

  const budgetSpent = final_report?.budget_summary?.spent || 0;
  const budgetTotal = final_report?.budget_summary?.total_budget || response.budget_remaining;
  const budgetPercent = (budgetSpent / budgetTotal) * 100;

  const handleMoleculeClick = (molecule: Molecule) => {
    setSelectedMolecule(molecule);
  };

  const handleCloseDetail = () => {
    setSelectedMolecule(null);
  };

  const handleExport = (format: 'sdf' | 'mol2' | 'smiles' | 'json') => {
    if (!selectedMolecule) return;

    let content = '';
    let filename = '';
    let mimeType = '';

    switch (format) {
      case 'sdf':
        content = generateSDFFormat(selectedMolecule);
        filename = `${selectedMolecule.id}.sdf`;
        mimeType = 'chemical/x-mdl-sdfile';
        break;
      case 'mol2':
        content = generateMOL2Format(selectedMolecule);
        filename = `${selectedMolecule.id}.mol2`;
        mimeType = 'chemical/x-mol2';
        break;
      case 'smiles':
        content = selectedMolecule.smiles || '';
        filename = `${selectedMolecule.id}.smi`;
        mimeType = 'text/plain';
        break;
      case 'json':
        content = JSON.stringify(selectedMolecule, null, 2);
        filename = `${selectedMolecule.id}.json`;
        mimeType = 'application/json';
        break;
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setShowExportMenu(false);
  };

  const handleSaveAll = () => {
    onSaveToLibrary(passedMolecules);
    alert(`Saved ${passedMolecules.length} molecules to library!`);
  };

  return (
    <div className="results-dashboard">
      {/* Header */}
      <div className="results-header">
        <div>
          <h1>Discovery Results</h1>
          <p className="results-subtitle">
            {passedMolecules.length} molecules passed evaluation
          </p>
        </div>
        <div className="results-header-actions">
          <button onClick={handleSaveAll} className="btn-solid-blue">
            Save All to Library
          </button>
          <button onClick={onReset} className="btn-solid-red">
            New Discovery
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="results-summary">
        <div className="summary-card-new blue">
          <div className="summary-icon">🧬</div>
          <div className="summary-content">
            <div className="summary-number">{response.molecules_generated}</div>
            <div className="summary-text">Generated</div>
          </div>
        </div>

        <div className="summary-card-new red">
          <div className="summary-icon">✓</div>
          <div className="summary-content">
            <div className="summary-number">{response.molecules_passed}</div>
            <div className="summary-text">Passed</div>
          </div>
        </div>

        <div className="summary-card-new blue">
          <div className="summary-icon">💰</div>
          <div className="summary-content">
            <div className="summary-number">${budgetSpent.toFixed(2)}</div>
            <div className="summary-text">Spent</div>
          </div>
        </div>

        <div className="summary-card-new red">
          <div className="summary-icon">📊</div>
          <div className="summary-content">
            <div className="summary-number">{final_report?.execution_summary?.iterations || 1}</div>
            <div className="summary-text">Iterations</div>
          </div>
        </div>
      </div>

      {/* Budget Progress */}
      <div className="budget-progress-section">
        <div className="budget-progress-header">
          <span>Budget Utilization</span>
          <span>{budgetPercent.toFixed(0)}%</span>
        </div>
        <div className="budget-progress-bar">
          <div
            className="budget-progress-fill"
            style={{ width: `${budgetPercent}%` }}
          ></div>
        </div>
        <div className="budget-progress-labels">
          <span>${budgetSpent.toFixed(2)} spent</span>
          <span>${(budgetTotal - budgetSpent).toFixed(2)} remaining</span>
        </div>
      </div>

      {/* Molecules Grid */}
      {passedMolecules.length > 0 && (
        <div className="molecules-section-new">
          <h2>Discovered Molecules</h2>
          <div className="molecules-grid-new">
            {passedMolecules.map((molecule) => (
              <div
                key={molecule.id}
                className="molecule-card-new"
                onClick={() => handleMoleculeClick(molecule)}
              >
                <div className="molecule-card-header">
                  <span className="molecule-id">{molecule.id}</span>
                  <span className={`molecule-status ${molecule.status}`}>
                    {molecule.status}
                  </span>
                </div>

                <div className="molecule-structure">
                  {molecule.svg_2d ? (
                    <div dangerouslySetInnerHTML={{ __html: molecule.svg_2d }} />
                  ) : (
                    <div className="molecule-placeholder">
                      <div className="molecule-placeholder-icon">⬡</div>
                    </div>
                  )}
                </div>

                <div className="molecule-properties">
                  {molecule.properties?.molecular_weight && (
                    <div className="property-item">
                      <span className="property-label">MW</span>
                      <span className="property-value">
                        {molecule.properties.molecular_weight.toFixed(2)}
                      </span>
                    </div>
                  )}
                  {molecule.properties?.logp !== undefined && (
                    <div className="property-item">
                      <span className="property-label">LogP</span>
                      <span className="property-value">
                        {molecule.properties.logp.toFixed(2)}
                      </span>
                    </div>
                  )}
                  {molecule.evaluation?.toxicity_score !== undefined && (
                    <div className="property-item">
                      <span className="property-label">Toxicity</span>
                      <span className="property-value">
                        {molecule.evaluation.toxicity_score.toFixed(2)}
                      </span>
                    </div>
                  )}
                </div>

                <div className="molecule-card-footer">
                  <button className="btn-view-details">
                    View Details →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Transactions */}
      {final_report?.transactions && final_report.transactions.length > 0 && (
        <div className="transactions-section-new">
          <h2>Payment Transactions</h2>
          <div className="transactions-table">
            {final_report.transactions.map((tx: any) => (
              <div key={tx.id} className="transaction-row">
                <div className="tx-col">
                  <span className="tx-label">Service</span>
                  <span className="tx-value">{tx.service}</span>
                </div>
                <div className="tx-col">
                  <span className="tx-label">Method</span>
                  <span className="tx-value">{tx.method}</span>
                </div>
                <div className="tx-col">
                  <span className="tx-label">Amount</span>
                  <span className="tx-amount">${tx.amount.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Molecule Detail Modal */}
      {selectedMolecule && (
        <div className="modal-overlay" onClick={handleCloseDetail}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedMolecule.id}</h2>
              <button className="modal-close" onClick={handleCloseDetail}>×</button>
            </div>

            <div className="modal-body">
              <div className="modal-structure">
                {selectedMolecule.svg_2d ? (
                  <div dangerouslySetInnerHTML={{ __html: selectedMolecule.svg_2d }} />
                ) : (
                  <div className="molecule-placeholder-large">⬡</div>
                )}
              </div>

              <div className="modal-info">
                <div className="info-section">
                  <h3>SMILES</h3>
                  <code className="smiles-code">{selectedMolecule.smiles}</code>
                </div>

                <div className="info-section">
                  <h3>Properties</h3>
                  <div className="properties-grid">
                    {selectedMolecule.properties && Object.entries(selectedMolecule.properties).map(([key, value]) => (
                      <div key={key} className="property-row">
                        <span className="prop-key">{key.replace(/_/g, ' ')}</span>
                        <span className="prop-value">
                          {typeof value === 'number' ? value.toFixed(2) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {selectedMolecule.evaluation && (
                  <div className="info-section">
                    <h3>Evaluation</h3>
                    <div className="properties-grid">
                      {Object.entries(selectedMolecule.evaluation).map(([key, value]) => (
                        <div key={key} className="property-row">
                          <span className="prop-key">{key.replace(/_/g, ' ')}</span>
                          <span className="prop-value">
                            {typeof value === 'number' ? value.toFixed(2) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="modal-footer">
              <div className="export-section">
                {!showExportMenu ? (
                  <button
                    className="btn-solid-blue"
                    onClick={() => setShowExportMenu(true)}
                  >
                    Export Molecule
                  </button>
                ) : (
                  <div className="export-menu">
                    <button onClick={() => handleExport('sdf')} className="export-btn">
                      SDF Format
                    </button>
                    <button onClick={() => handleExport('mol2')} className="export-btn">
                      MOL2 Format
                    </button>
                    <button onClick={() => handleExport('smiles')} className="export-btn">
                      SMILES
                    </button>
                    <button onClick={() => handleExport('json')} className="export-btn">
                      JSON Data
                    </button>
                    <button
                      onClick={() => setShowExportMenu(false)}
                      className="export-btn cancel"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper functions to generate export formats
function generateSDFFormat(molecule: Molecule): string {
  return `
  ${molecule.id}


  0  0  0  0  0  0  0  0  0  0999 V2000
M  END
> <ID>
${molecule.id}

> <SMILES>
${molecule.smiles}

> <MOLECULAR_WEIGHT>
${molecule.properties?.molecular_weight || 'N/A'}

> <LOGP>
${molecule.properties?.logp || 'N/A'}

> <TOXICITY_SCORE>
${molecule.evaluation?.toxicity_score || 'N/A'}

$$$$
`;
}

function generateMOL2Format(molecule: Molecule): string {
  return `@<TRIPOS>MOLECULE
${molecule.id}
0 0 0 0 0
SMALL
USER_CHARGES

@<TRIPOS>ATOM

@<TRIPOS>BOND

@<TRIPOS>SUBSTRUCTURE

# SMILES: ${molecule.smiles}
# Molecular Weight: ${molecule.properties?.molecular_weight || 'N/A'}
# LogP: ${molecule.properties?.logp || 'N/A'}
# Toxicity Score: ${molecule.evaluation?.toxicity_score || 'N/A'}
`;
}

export default ResultsDashboard;
