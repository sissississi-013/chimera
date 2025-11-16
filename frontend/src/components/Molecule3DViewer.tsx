/**
 * 3D Molecule Viewer - Interactive 3D visualization using 3Dmol.js
 */
import React, { useEffect, useRef, useState } from 'react';

interface Molecule3DViewerProps {
  smiles: string;
  name: string;
  onClose: () => void;
}

const Molecule3DViewer: React.FC<Molecule3DViewerProps> = ({ smiles, name, onClose }) => {
  const viewerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load3DView = async () => {
      try {
        // Dynamically load 3Dmol.js
        if (!window.$3Dmol) {
          const script = document.createElement('script');
          script.src = 'https://3Dmol.csb.pitt.edu/build/3Dmol-min.js';
          script.async = true;
          document.body.appendChild(script);

          await new Promise((resolve, reject) => {
            script.onload = resolve;
            script.onerror = reject;
          });
        }

        if (viewerRef.current) {
          // Clear previous viewer
          viewerRef.current.innerHTML = '';

          // Create new viewer
          const viewer = window.$3Dmol.createViewer(viewerRef.current, {
            backgroundColor: 'black',
          });

          // Fetch 3D structure from PubChem using SMILES
          const pubchemUrl = `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/${encodeURIComponent(smiles)}/SDF`;

          const response = await fetch(pubchemUrl);

          if (!response.ok) {
            throw new Error('Could not fetch 3D structure from PubChem');
          }

          const sdfData = await response.text();

          // Add molecule to viewer
          viewer.addModel(sdfData, 'sdf');

          // Set style - stick representation
          viewer.setStyle({}, {
            stick: {
              colorscheme: 'Jmol',
              radius: 0.2
            }
          });

          // Add surface (semi-transparent)
          viewer.addSurface(window.$3Dmol.SurfaceType.VDW, {
            opacity: 0.7,
            colorscheme: 'Jmol'
          });

          // Center and zoom
          viewer.zoomTo();
          viewer.render();

          // Enable rotation
          viewer.spin(true);

          setLoading(false);
        }
      } catch (err) {
        console.error('3D visualization error:', err);
        setError('Unable to load 3D structure. The molecule may not be available in PubChem.');
        setLoading(false);
      }
    };

    load3DView();
  }, [smiles]);

  return (
    <div className="molecule-3d-modal">
      <div className="modal-overlay" onClick={onClose} />
      <div className="modal-content">
        <div className="modal-header">
          <h2>3D Structure: {name}</h2>
          <button onClick={onClose} className="close-button">×</button>
        </div>

        <div className="viewer-container">
          {loading && (
            <div className="loading-overlay">
              <div className="spinner"></div>
              <p>Loading 3D structure from PubChem...</p>
            </div>
          )}
          {error && (
            <div className="error-overlay">
              <div className="error-icon">⚠</div>
              <p>{error}</p>
              <button onClick={onClose} className="btn-close">Close</button>
            </div>
          )}
          <div
            ref={viewerRef}
            className="viewer-3d"
            style={{
              width: '100%',
              height: '600px',
              position: 'relative',
            }}
          />
        </div>

        <div className="viewer-controls">
          <div className="smiles-display">
            <strong>SMILES:</strong> <code>{smiles}</code>
          </div>
          <div className="control-info">
            <span>🖱️ Drag to rotate</span>
            <span>🔍 Scroll to zoom</span>
            <span>⚡ Auto-rotating</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        .molecule-3d-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 9999;
          display: flex;
          align-items: center;
          justify-content: center;
          animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .modal-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.85);
          backdrop-filter: blur(10px);
        }

        .modal-content {
          position: relative;
          width: 90%;
          max-width: 1000px;
          background: linear-gradient(135deg, rgba(30, 30, 40, 0.95) 0%, rgba(20, 20, 30, 0.95) 100%);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 16px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
          animation: slideUp 0.4s ease-out;
        }

        @keyframes slideUp {
          from {
            transform: translateY(50px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 24px 32px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .modal-header h2 {
          margin: 0;
          color: rgba(255, 255, 255, 0.95);
          font-size: 24px;
          font-weight: 600;
        }

        .close-button {
          background: rgba(255, 255, 255, 0.1);
          border: none;
          color: rgba(255, 255, 255, 0.9);
          font-size: 32px;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .close-button:hover {
          background: rgba(255, 255, 255, 0.2);
          transform: scale(1.1);
        }

        .viewer-container {
          position: relative;
          padding: 32px;
        }

        .loading-overlay,
        .error-overlay {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
          z-index: 10;
        }

        .spinner {
          width: 50px;
          height: 50px;
          border: 4px solid rgba(255, 255, 255, 0.1);
          border-top-color: #667eea;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 16px;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        .loading-overlay p,
        .error-overlay p {
          color: rgba(255, 255, 255, 0.7);
          font-size: 14px;
        }

        .error-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }

        .btn-close {
          margin-top: 16px;
          padding: 10px 24px;
          background: #667eea;
          border: none;
          border-radius: 8px;
          color: white;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-close:hover {
          background: #5568d3;
          transform: translateY(-2px);
        }

        .viewer-3d {
          border-radius: 12px;
          overflow: hidden;
        }

        .viewer-controls {
          padding: 24px 32px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .smiles-display {
          margin-bottom: 16px;
          color: rgba(255, 255, 255, 0.9);
        }

        .smiles-display strong {
          color: rgba(255, 255, 255, 0.6);
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .smiles-display code {
          background: rgba(255, 255, 255, 0.05);
          padding: 4px 8px;
          border-radius: 4px;
          font-family: 'Courier New', monospace;
          font-size: 13px;
          color: rgba(255, 255, 255, 0.8);
          margin-left: 8px;
        }

        .control-info {
          display: flex;
          gap: 24px;
          justify-content: center;
        }

        .control-info span {
          color: rgba(255, 255, 255, 0.5);
          font-size: 13px;
        }
      `}</style>
    </div>
  );
};

export default Molecule3DViewer;
