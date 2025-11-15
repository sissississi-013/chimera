/**
 * Market Page - Decentralized marketplace for protein and drug design data
 */
import React from 'react';

const MarketPage: React.FC = () => {
  return (
    <div className="market-page">
      <div className="page-header">
        <h1>Decentralized Market</h1>
        <p>Trade protein design and drug discovery data</p>
      </div>

      <div className="market-content">
        <div className="market-section">
          <h2>Marketplace Coming Soon</h2>
          <p>
            The decentralized marketplace will allow you to:
          </p>
          <ul className="feature-list">
            <li>Browse discovered molecules and protein designs</li>
            <li>Purchase high-quality scientific data</li>
            <li>List your own discoveries for monetization</li>
            <li>Trade data assets using cryptocurrency</li>
            <li>Access verified and validated datasets</li>
            <li>Participate in the decentralized scientific economy</li>
          </ul>
        </div>

        <div className="placeholder-grid">
          <div className="placeholder-card">
            <h3>Featured Listings</h3>
            <p>High-quality molecule discoveries from the Chimera network</p>
            <div className="placeholder-content">
              <div className="placeholder-shimmer" />
            </div>
          </div>

          <div className="placeholder-card">
            <h3>Recent Discoveries</h3>
            <p>Latest uploads to the marketplace</p>
            <div className="placeholder-content">
              <div className="placeholder-shimmer" />
            </div>
          </div>

          <div className="placeholder-card">
            <h3>Your Listings</h3>
            <p>Manage your monetized discoveries</p>
            <div className="placeholder-content">
              <div className="placeholder-shimmer" />
            </div>
          </div>
        </div>

        <div className="status-banner">
          <div className="status-icon">⚙️</div>
          <div className="status-text">
            <strong>Under Development</strong>
            <p>Marketplace infrastructure is being built. Check back soon!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketPage;
