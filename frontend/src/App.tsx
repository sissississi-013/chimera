/**
 * Main Chimera App with Navigation
 */
import React, { useState } from 'react';
import './App.css';
import Navigation from './components/Navigation';
import HomePage from './components/HomePage';
import RunPage from './components/RunPage';
import MarketPage from './components/MarketPage';
import AgentsPage from './components/AgentsPage';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const handleNavigate = (page: string) => {
    setCurrentPage(page);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage onNavigate={handleNavigate} />;
      case 'run':
        return <RunPage onNavigate={handleNavigate} />;
      case 'market':
        return <MarketPage />;
      case 'agents':
        return <AgentsPage />;
      default:
        return <HomePage onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="app">
      <Navigation currentPage={currentPage} onNavigate={handleNavigate} />
      <main className="app-main">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
