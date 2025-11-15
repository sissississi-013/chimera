/**
 * Agent Thinking - Visualizes agent's decision-making process
 */
import React from 'react';

interface Thought {
  time: number;
  phase: string;
  thought: string;
}

interface AgentThinkingProps {
  thoughts: Thought[];
}

const AgentThinking: React.FC<AgentThinkingProps> = ({ thoughts }) => {
  const getPhaseColor = (phase: string) => {
    const colors: Record<string, string> = {
      planning: '#3B5BA5',
      generation: '#A855F7',
      evaluation: '#E85D75',
      payment: '#4CAF50',
      decision: '#FF9800',
      visualization: '#2196F3',
      monetization: '#9C27B0',
      completed: '#4CAF50',
    };
    return colors[phase] || '#666';
  };

  return (
    <div className="agent-thinking">
      <h3>Agent Thinking Process</h3>
      <div className="thinking-timeline">
        {thoughts.map((thought, index) => (
          <div key={index} className="thought-item">
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
        {thoughts.length > 0 && (
          <div className="thought-pulse">
            <div className="pulse-dot" />
            <span>Processing...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentThinking;
