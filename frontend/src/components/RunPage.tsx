/**
 * Run Page - Drug discovery execution interface with conversational AI
 */
import React, { useState, useEffect } from 'react';
import chimeraApi from '../services/api';
import type { AgentRequest, DiscoveryResult } from '../types';
import ResultsDashboard from './ResultsDashboard';
import ChatInterface from './ChatInterface';

interface RunPageProps {
  onNavigate: (page: string, data?: any) => void;
  onResultsReady: (result: DiscoveryResult) => void;
}

const RunPage: React.FC<RunPageProps> = ({ onNavigate, onResultsReady }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<DiscoveryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [agentThoughts, setAgentThoughts] = useState<any[]>([]);
  const [currentPhase, setCurrentPhase] = useState<string>('idle');
  const [showChat, setShowChat] = useState(true);

  const handleStartDiscovery = async (params: any) => {
    // Convert chat params to AgentRequest
    const request: AgentRequest = {
      goal: params.goal,
      target: params.target || undefined,
      budget: params.budget || 5.0,
      constraints: {
        max_toxicity: params.constraints?.max_toxicity || 0.5,
        min_drug_likeness: params.constraints?.min_drug_likeness || 0.6,
      },
    };

    try {
      setIsRunning(true);
      setShowChat(false);
      setError(null);
      setLogs(['Initializing Chimera agent...']);
      setAgentThoughts([]);

      // Start streaming real-time logs and thoughts
      startRealtimeStreaming();

      // Call API
      const discoveryResult = await chimeraApi.discover(request);

      // Show final logs
      if (discoveryResult.response.logs) {
        setLogs(discoveryResult.response.logs);
      }

      setResult(discoveryResult);
      onResultsReady(discoveryResult);
      setIsRunning(false);
    } catch (err) {
      setError((err as Error).message);
      setIsRunning(false);
    }
  };

  const startRealtimeStreaming = () => {
    // Connect to backend event stream for real-time agent thinking
    const eventSource = new EventSource('http://localhost:8000/api/v1/discover/stream');

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'log') {
          setLogs(prev => [...prev, data.message]);
        } else if (data.type === 'thought') {
          setAgentThoughts(prev => [...prev, {
            time: Date.now(),
            phase: data.phase,
            thought: data.content
          }]);
          setCurrentPhase(data.phase);
        } else if (data.type === 'phase_change') {
          setCurrentPhase(data.phase);
          setLogs(prev => [...prev, `=== Phase: ${data.phase.toUpperCase()} ===`]);
        } else if (data.type === 'complete') {
          eventSource.close();
        }
      } catch (e) {
        console.error('Error parsing stream data:', e);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
    setIsRunning(false);
    setLogs([]);
    setAgentThoughts([]);
    setCurrentPhase('idle');
    setShowChat(true);
  };

  const handleViewResults = () => {
    onNavigate('results');
  };

  const getPhaseColor = (phase: string) => {
    const colors: Record<string, string> = {
      planning: '#3B5BA5',
      generating: '#A855F7',
      evaluating: '#E85D75',
      payment: '#4CAF50',
      decision: '#FF9800',
      visualizing: '#2196F3',
      monetizing: '#9C27B0',
      completed: '#4CAF50',
    };
    return colors[phase] || '#666';
  };

  return (
    <div className="run-page">
      <div className="run-container">
        <div className="run-header">
          <h1>Discovery Run</h1>
          <p>Chat with Chimera to plan your drug discovery campaign</p>
        </div>

        {showChat && !isRunning && !result ? (
          <div className="chat-mode">
            <ChatInterface onStartDiscovery={handleStartDiscovery} />
          </div>
        ) : (
          <div className="agent-activity-fullscreen">
            <div className="activity-header">
              <div className="activity-status">
                <div className="status-pulse"></div>
                <span>Agent Running... </span>
                <span className="current-phase" style={{ color: getPhaseColor(currentPhase) }}>
                  {currentPhase.toUpperCase()}
                </span>
              </div>
            </div>

            <div className="activity-grid">
              {/* Real-time Agent Thinking */}
              <div className="agent-thinking-live">
                <h3>Agent Reasoning</h3>
                <div className="thinking-timeline">
                  {agentThoughts.map((thought, index) => (
                    <div key={index} className="thought-item animate-in">
                      <div
                        className="thought-indicator"
                        style={{ backgroundColor: getPhaseColor(thought.phase) }}
                      />
                      <div className="thought-content">
                        <div className="thought-phase">{thought.phase.toUpperCase()}</div>
                        <div className="thought-text">{thought.thought}</div>
                      </div>
                    </div>
                  ))}
                  {agentThoughts.length > 0 && (
                    <div className="thought-pulse">
                      <div className="pulse-dot" />
                      <span>Thinking...</span>
                    </div>
                  )}
                </div>
              </div>

              {/* System Logs */}
              <div className="activity-logs">
                <h3>System Logs</h3>
                <div className="logs-container">
                  {logs.length === 0 ? (
                    <div className="log-entry log-placeholder">Waiting for logs...</div>
                  ) : (
                    logs.map((log, index) => (
                      <div key={index} className="log-entry animate-in">
                        <span className="log-time">[{new Date().toLocaleTimeString()}]</span>
                        <span className="log-text">{log}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Completion Actions - Show when run is complete */}
            {result && !isRunning && (
              <div className="completion-actions-bar">
                <div className="completion-summary">
                  <div className="completion-icon-small">✓</div>
                  <div className="completion-text">
                    <strong>Discovery Complete!</strong>
                    <span>{result.response.molecules_generated} molecules generated, {result.response.molecules_passed} passed evaluation</span>
                  </div>
                </div>
                <div className="completion-buttons">
                  <button onClick={handleViewResults} className="btn-view-results-primary">
                    View Detailed Results →
                  </button>
                  <button onClick={handleReset} className="btn-new-run-outline">
                    Start New Discovery
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="error-container">
            <div className="error-icon">!</div>
            <div className="error-content">
              <h3>Error Occurred</h3>
              <p>{error}</p>
              <button onClick={handleReset} className="reset-button">
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .chat-mode {
          height: 600px;
          margin-top: 24px;
        }

        .animate-in {
          animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .current-phase {
          font-weight: 600;
          margin-left: 8px;
        }

        .agent-thinking-live {
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 20px;
          overflow-y: auto;
        }

        .agent-thinking-live h3 {
          margin: 0 0 16px 0;
          color: rgba(255, 255, 255, 0.9);
          font-size: 16px;
        }

        .thinking-timeline {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .thought-item {
          display: flex;
          gap: 12px;
          padding: 12px;
          background: rgba(255, 255, 255, 0.03);
          border-radius: 8px;
          border-left: 3px solid;
        }

        .thought-indicator {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-top: 6px;
          flex-shrink: 0;
        }

        .thought-content {
          flex: 1;
        }

        .thought-phase {
          font-size: 11px;
          font-weight: 600;
          color: rgba(255, 255, 255, 0.5);
          margin-bottom: 4px;
          letter-spacing: 0.5px;
        }

        .thought-text {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.8);
          line-height: 1.5;
        }

        .thought-pulse {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px;
          color: rgba(255, 255, 255, 0.6);
          font-size: 13px;
        }

        .pulse-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.6);
          animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 0.4;
            transform: scale(1);
          }
          50% {
            opacity: 1;
            transform: scale(1.2);
          }
        }

        .completion-actions-bar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 24px;
          margin: 24px;
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
          border: 2px solid rgba(102, 126, 234, 0.3);
          border-radius: 12px;
          animation: slideIn 0.5s ease-out;
        }

        .completion-summary {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .completion-icon-small {
          width: 40px;
          height: 40px;
          background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          color: white;
        }

        .completion-text {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .completion-text strong {
          color: rgba(255, 255, 255, 0.95);
          font-size: 16px;
        }

        .completion-text span {
          color: rgba(255, 255, 255, 0.7);
          font-size: 14px;
        }

        .completion-buttons {
          display: flex;
          gap: 12px;
        }

        .btn-view-results-primary {
          padding: 12px 28px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          border-radius: 8px;
          color: white;
          font-weight: 600;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-view-results-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }

        .btn-new-run-outline {
          padding: 12px 28px;
          background: transparent;
          border: 2px solid rgba(255, 255, 255, 0.2);
          border-radius: 8px;
          color: rgba(255, 255, 255, 0.9);
          font-weight: 600;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-new-run-outline:hover {
          background: rgba(255, 255, 255, 0.05);
          border-color: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </div>
  );
};

export default RunPage;
