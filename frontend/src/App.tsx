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
import ResultsDashboard from './components/ResultsDashboard';
import LibraryPage from './components/LibraryPage';
import type { DiscoveryResult } from './types';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [currentResult, setCurrentResult] = useState<DiscoveryResult | null>(null);
  const [savedMolecules, setSavedMolecules] = useState<any[]>([]);

  const handleNavigate = (page: string, data?: any) => {
    if (page === 'results' && data) {
      setCurrentResult(data);
    }
    setCurrentPage(page);
  };

  const handleSaveMolecules = (molecules: any[]) => {
    setSavedMolecules(prev => [...prev, ...molecules]);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage onNavigate={handleNavigate} />;
      case 'run':
        return <RunPage onNavigate={handleNavigate} onResultsReady={setCurrentResult} />;
      case 'results':
        return currentResult ? (
          <ResultsDashboard
            result={currentResult}
            onReset={() => handleNavigate('run')}
            onSaveToLibrary={handleSaveMolecules}
          />
        ) : (
          <div className="no-results">No results available. Run a discovery first.</div>
        );
      case 'library':
        return <LibraryPage molecules={savedMolecules} onNavigate={handleNavigate} />;
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
