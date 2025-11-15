/**
 * Library Page - Manage and export discovered molecules
 */
import React, { useState } from 'react';

interface LibraryPageProps {
  molecules: any[];
  onNavigate: (page: string) => void;
}

const LibraryPage: React.FC<LibraryPageProps> = ({ molecules, onNavigate }) => {
  const [selectedMolecules, setSelectedMolecules] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const handleSelectMolecule = (id: string) => {
    const newSelected = new Set(selectedMolecules);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedMolecules(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedMolecules.size === molecules.length) {
      setSelectedMolecules(new Set());
    } else {
      setSelectedMolecules(new Set(molecules.map(m => m.id)));
    }
  };

  const handleExportSelected = () => {
    const selected = molecules.filter(m => selectedMolecules.has(m.id));
    const content = JSON.stringify(selected, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `chimera_molecules_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExportToMarket = () => {
    if (selectedMolecules.size === 0) {
      alert('Please select molecules to export to marketplace');
      return;
    }
    alert(`Exporting ${selectedMolecules.size} molecules to marketplace...`);
    // Here you would integrate with the marketplace API
  };

  return (
    <div className="library-page">
      <div className="library-header">
        <div>
          <h1>Molecule Library</h1>
          <p className="library-subtitle">
            {molecules.length} molecules saved
          </p>
        </div>
        <div className="library-actions">
          <button
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            className="btn-view-mode"
          >
            {viewMode === 'grid' ? '☰ List' : '⊞ Grid'}
          </button>
          {molecules.length > 0 && (
            <>
              <button onClick={handleSelectAll} className="btn-solid-blue">
                {selectedMolecules.size === molecules.length ? 'Deselect All' : 'Select All'}
              </button>
              {selectedMolecules.size > 0 && (
                <>
                  <button onClick={handleExportSelected} className="btn-solid-blue">
                    Export ({selectedMolecules.size})
                  </button>
                  <button onClick={handleExportToMarket} className="btn-solid-red">
                    Sell on Market ({selectedMolecules.size})
                  </button>
                </>
              )}
            </>
          )}
        </div>
      </div>

      {molecules.length === 0 ? (
        <div className="library-empty">
          <div className="empty-icon">📚</div>
          <h2>No Molecules in Library</h2>
          <p>Discover and save molecules to build your library</p>
          <button onClick={() => onNavigate('run')} className="btn-solid-blue">
            Start Discovery
          </button>
        </div>
      ) : (
        <div className={`library-${viewMode}`}>
          {molecules.map((molecule) => (
            <div
              key={molecule.id}
              className={`library-molecule-card ${selectedMolecules.has(molecule.id) ? 'selected' : ''}`}
            >
              <div className="molecule-select">
                <input
                  type="checkbox"
                  checked={selectedMolecules.has(molecule.id)}
                  onChange={() => handleSelectMolecule(molecule.id)}
                  onClick={(e) => e.stopPropagation()}
                />
              </div>

              <div className="molecule-card-content">
                <div className="molecule-header">
                  <span className="molecule-id">{molecule.id}</span>
                  <span className={`molecule-status ${molecule.status}`}>
                    {molecule.status}
                  </span>
                </div>

                <div className="molecule-structure-preview">
                  {molecule.svg_2d ? (
                    <div dangerouslySetInnerHTML={{ __html: molecule.svg_2d }} />
                  ) : (
                    <div className="molecule-placeholder">⬡</div>
                  )}
                </div>

                <div className="molecule-info">
                  <div className="info-row">
                    <span className="info-label">MW:</span>
                    <span className="info-value">
                      {molecule.properties?.molecular_weight?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">LogP:</span>
                    <span className="info-value">
                      {molecule.properties?.logp?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Toxicity:</span>
                    <span className="info-value">
                      {molecule.evaluation?.toxicity_score?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LibraryPage;
