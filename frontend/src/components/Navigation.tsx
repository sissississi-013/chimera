/**
 * Navigation Component - Main navigation bar for Chimera
 */
import React from 'react';

interface NavigationProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

const Navigation: React.FC<NavigationProps> = ({ currentPage, onNavigate }) => {
  const navItems = [
    { id: 'home', label: 'Home' },
    { id: 'run', label: 'Run' },
    { id: 'market', label: 'Market' },
    { id: 'agents', label: 'Agents' },
  ];

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-logo">
          <img src="/web_icon.png" alt="Chimera" className="nav-logo-icon" />
        </div>

        <div className="nav-links">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-link ${currentPage === item.id ? 'active' : ''}`}
              onClick={() => onNavigate(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>

        <div className="nav-status">
          <div className="status-indicator"></div>
          <span className="status-text">System Operational</span>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
