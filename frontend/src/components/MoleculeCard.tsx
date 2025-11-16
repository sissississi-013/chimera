/**
 * Molecule Card Component - Display individual molecule details with 3D visualization
 */
import React, { useState } from 'react';
import type { Molecule } from '../types';
import Molecule3DViewer from './Molecule3DViewer';

interface MoleculeCardProps {
  molecule: Molecule;
}

const MoleculeCard: React.FC<MoleculeCardProps> = ({ molecule }) => {
  const { name, smiles, properties, visualization_url, status } = molecule;
  const [show3D, setShow3D] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return '#4CAF50';
      case 'monetized':
        return '#2196F3';
      case 'rejected':
        return '#f44336';
      default:
        return '#9E9E9E';
    }
  };

  return (
    <div className="molecule-card">
      <div className="molecule-header">
        <h4>{name}</h4>
        <span
          className="molecule-status"
          style={{ backgroundColor: getStatusColor(status) }}
        >
          {status}
        </span>
      </div>

      {/* Visualization */}
      {visualization_url && (
        <div className="molecule-viz" onClick={() => setShow3D(true)} style={{ cursor: 'pointer' }}>
          <img src={visualization_url} alt={`Structure of ${name}`} />
          <div className="view-3d-overlay">
            <span className="view-3d-button">🔍 Click to view in 3D</span>
          </div>
        </div>
      )}

      {/* SMILES */}
      <div className="molecule-smiles">
        <code>{smiles}</code>
      </div>

      {/* Properties */}
      <div className="molecule-properties">
        {properties.toxicity_score !== undefined && (
          <div className="property-item">
            <span className="property-label">Toxicity:</span>
            <span className="property-value">
              {properties.toxicity_score.toFixed(3)}
            </span>
            <div
              className="property-bar"
              style={{
                width: '100%',
                height: '4px',
                background: '#e0e0e0',
                marginTop: '4px',
              }}
            >
              <div
                style={{
                  width: `${properties.toxicity_score * 100}%`,
                  height: '100%',
                  background:
                    properties.toxicity_score > 0.5 ? '#f44336' : '#4CAF50',
                }}
              ></div>
            </div>
          </div>
        )}

        {properties.efficacy_score !== undefined && (
          <div className="property-item">
            <span className="property-label">Efficacy:</span>
            <span className="property-value">
              {properties.efficacy_score.toFixed(3)}
            </span>
            <div
              className="property-bar"
              style={{
                width: '100%',
                height: '4px',
                background: '#e0e0e0',
                marginTop: '4px',
              }}
            >
              <div
                style={{
                  width: `${properties.efficacy_score * 100}%`,
                  height: '100%',
                  background: '#2196F3',
                }}
              ></div>
            </div>
          </div>
        )}

        {properties.molecular_weight && (
          <div className="property-item">
            <span className="property-label">MW:</span>
            <span className="property-value">
              {properties.molecular_weight.toFixed(1)} Da
            </span>
          </div>
        )}

        {properties.logp !== undefined && (
          <div className="property-item">
            <span className="property-label">LogP:</span>
            <span className="property-value">{properties.logp.toFixed(2)}</span>
          </div>
        )}

        {properties.drug_likeness !== undefined && (
          <div className="property-item">
            <span className="property-label">Drug-likeness:</span>
            <span className="property-value">
              {properties.drug_likeness.toFixed(2)}
            </span>
          </div>
        )}

        {properties.predicted_activity && (
          <div className="property-item">
            <span className="property-label">Activity:</span>
            <span className="property-value">{properties.predicted_activity}</span>
          </div>
        )}

        {properties.additional_properties?.composite_score !== undefined && (
          <div className="property-item">
            <span className="property-label">Composite Score:</span>
            <span className="property-value">
              {properties.additional_properties.composite_score.toFixed(3)}
            </span>
          </div>
        )}
      </div>

      {/* Lipinski's Rule of Five Compliance */}
      <div className="lipinski-section">
        <div className="lipinski-title">Lipinski's Rule of Five:</div>
        <div className="lipinski-checks">
          <span className={properties.molecular_weight && properties.molecular_weight <= 500 ? 'check-pass' : 'check-fail'}>
            {properties.molecular_weight && properties.molecular_weight <= 500 ? '✓' : '✗'} MW ≤ 500
          </span>
          <span className={properties.logp && properties.logp <= 5 ? 'check-pass' : 'check-fail'}>
            {properties.logp && properties.logp <= 5 ? '✓' : '✗'} LogP ≤ 5
          </span>
          <span className={properties.h_bond_donors && properties.h_bond_donors <= 5 ? 'check-pass' : 'check-fail'}>
            {properties.h_bond_donors && properties.h_bond_donors <= 5 ? '✓' : '✗'} HBD ≤ 5
          </span>
          <span className={properties.h_bond_acceptors && properties.h_bond_acceptors <= 10 ? 'check-pass' : 'check-fail'}>
            {properties.h_bond_acceptors && properties.h_bond_acceptors <= 10 ? '✓' : '✗'} HBA ≤ 10
          </span>
        </div>
      </div>

      {/* 3D Viewer Modal */}
      {show3D && (
        <Molecule3DViewer
          smiles={smiles}
          name={name}
          onClose={() => setShow3D(false)}
        />
      )}

      <style jsx>{`
        .molecule-viz {
          position: relative;
          transition: transform 0.2s;
        }

        .molecule-viz:hover {
          transform: scale(1.02);
        }

        .view-3d-overlay {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
          padding: 8px;
          opacity: 0;
          transition: opacity 0.2s;
        }

        .molecule-viz:hover .view-3d-overlay {
          opacity: 1;
        }

        .view-3d-button {
          color: white;
          font-size: 12px;
          font-weight: 600;
          display: block;
          text-align: center;
        }
      `}</style>
    </div>
  );
};

export default MoleculeCard;
