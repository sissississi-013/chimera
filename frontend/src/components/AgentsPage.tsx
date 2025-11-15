/**
 * Agents Page - Manage crypto accounts and scientific discovery tools
 */
import React, { useState } from 'react';

const AgentsPage: React.FC = () => {
  const [walletConnected, setWalletConnected] = useState(false);

  return (
    <div className="agents-page">
      <div className="page-header">
        <h1>Agents & Transactions</h1>
        <p>Manage your crypto accounts and discovery tools</p>
      </div>

      <div className="agents-content">
        <div className="agents-grid">
          <div className="agent-card">
            <h3>Wallet Management</h3>
            <div className="wallet-section">
              {!walletConnected ? (
                <div className="wallet-connect">
                  <p>Connect your Coinbase CDP wallet to enable autonomous payments</p>
                  <button
                    className="connect-wallet-btn"
                    onClick={() => setWalletConnected(true)}
                  >
                    Connect Wallet
                  </button>
                </div>
              ) : (
                <div className="wallet-info">
                  <div className="wallet-status">
                    <div className="status-indicator connected"></div>
                    <span>Wallet Connected</span>
                  </div>
                  <div className="wallet-details">
                    <p><strong>Address:</strong> 0x742d...4e2a (simulated)</p>
                    <p><strong>Balance:</strong> 100.00 USDC</p>
                    <p><strong>Network:</strong> Base Mainnet</p>
                  </div>
                  <button
                    className="disconnect-wallet-btn"
                    onClick={() => setWalletConnected(false)}
                  >
                    Disconnect
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="agent-card">
            <h3>Transaction History</h3>
            <div className="transactions-list">
              <div className="transaction-item">
                <div className="tx-type">Toxicity API</div>
                <div className="tx-amount">-$0.05</div>
              </div>
              <div className="transaction-item">
                <div className="tx-type">Efficacy Check</div>
                <div className="tx-amount">-$0.10</div>
              </div>
              <div className="transaction-item">
                <div className="tx-type">Marketplace Listing</div>
                <div className="tx-amount">-$0.20</div>
              </div>
            </div>
          </div>

          <div className="agent-card">
            <h3>API Connections</h3>
            <div className="api-list">
              <div className="api-item">
                <div className="api-name">Toxicity Prediction API</div>
                <div className="api-status connected">Connected</div>
              </div>
              <div className="api-item">
                <div className="api-name">Efficacy Scoring API</div>
                <div className="api-status connected">Connected</div>
              </div>
              <div className="api-item">
                <div className="api-name">Data Marketplace API</div>
                <div className="api-status connected">Connected</div>
              </div>
              <div className="api-item">
                <div className="api-name">Anthropic Claude API</div>
                <div className="api-status disconnected">Not Configured</div>
              </div>
            </div>
          </div>

          <div className="agent-card">
            <h3>Discovery Tools</h3>
            <div className="tools-list">
              <div className="tool-item">
                <h4>Molecule Generator</h4>
                <p>Status: Active</p>
                <p>Last Run: 2 minutes ago</p>
              </div>
              <div className="tool-item">
                <h4>Toxicity Evaluator</h4>
                <p>Status: Active</p>
                <p>API Calls Today: 45</p>
              </div>
              <div className="tool-item">
                <h4>Payment Handler</h4>
                <p>Status: Active</p>
                <p>Mode: Simulated</p>
              </div>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h2>Agent Settings</h2>
          <div className="settings-grid">
            <div className="setting-item">
              <label>Default Budget (USD)</label>
              <input type="number" defaultValue="5.00" step="0.1" />
            </div>
            <div className="setting-item">
              <label>Max Cost Per API Call (USD)</label>
              <input type="number" defaultValue="1.00" step="0.1" />
            </div>
            <div className="setting-item">
              <label>Auto-monetize Discoveries</label>
              <select defaultValue="yes">
                <option value="yes">Yes</option>
                <option value="no">No</option>
                <option value="ask">Ask Each Time</option>
              </select>
            </div>
            <div className="setting-item">
              <label>Payment Mode</label>
              <select defaultValue="simulated">
                <option value="simulated">Simulated (Safe Testing)</option>
                <option value="real">Real Transactions</option>
              </select>
            </div>
          </div>
          <button className="save-settings-btn">Save Settings</button>
        </div>
      </div>
    </div>
  );
};

export default AgentsPage;
