/**
 * ChatInterface - Conversational AI interface for drug discovery planning
 */
import React, { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  onStartDiscovery: (params: any) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onStartDiscovery }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I'm Chimera, your autonomous drug discovery assistant. I can help you plan and execute molecule discovery campaigns using NVIDIA NIMs and advanced AI models.\n\nWhat would you like to discover today? For example:\n- \"Find molecules that inhibit EGFR kinase with low toxicity\"\n- \"Discover anti-cancer compounds targeting BCR-ABL\"\n- \"Generate drug candidates for Alzheimer's disease\""
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call Claude API
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          conversation_history: messages,
          stream: false
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response from Claude');
      }

      const data = await response.json();
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.content
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExtractAndStart = async () => {
    setIsExtracting(true);

    try {
      // Extract parameters from conversation
      const response = await fetch('http://localhost:8000/api/v1/chat/extract-params', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_history: messages
        })
      });

      if (!response.ok) {
        throw new Error('Failed to extract parameters');
      }

      const params = await response.json();

      // Add confirmation message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Perfect! I've extracted your discovery parameters:\n\n**Goal:** ${params.goal}\n**Target:** ${params.target || 'Not specified'}\n**Budget:** $${params.budget}\n**Max Toxicity:** ${params.constraints?.max_toxicity || 0.5}\n\nStarting your discovery run now...`
      }]);

      // Start discovery with extracted params
      setTimeout(() => {
        onStartDiscovery(params);
      }, 1500);

    } catch (error) {
      console.error('Extract error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I had trouble extracting the parameters. Could you clarify your discovery goal?'
      }]);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickPrompts = [
    "Find EGFR inhibitors with high drug-likeness",
    "Discover anti-inflammatory compounds",
    "Generate kinase inhibitors under $10 budget"
  ];

  return (
    <div className="chat-interface">
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.role}`}>
              <div className="message-avatar">
                <img
                  src={msg.role === 'assistant' ? '/assets/chimera.png' : '/assets/user.png'}
                  alt={msg.role === 'assistant' ? 'Chimera' : 'User'}
                  className="avatar-image"
                />
              </div>
              <div className="message-content">
                <div className="message-role">
                  {msg.role === 'assistant' ? 'Chimera' : 'You'}
                </div>
                <div className="message-text">
                  {msg.content.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="chat-message assistant">
              <div className="message-avatar">
                <img
                  src="/assets/chimera.png"
                  alt="Chimera"
                  className="avatar-image"
                />
              </div>
              <div className="message-content">
                <div className="message-role">Chimera</div>
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {messages.length > 2 && (
          <div className="chat-actions">
            <button
              onClick={handleExtractAndStart}
              disabled={isExtracting || isLoading}
              className="btn-start-discovery"
            >
              {isExtracting ? 'Extracting Parameters...' : 'Start Discovery Run'}
            </button>
          </div>
        )}

        <div className="chat-input-container">
          {messages.length === 1 && (
            <div className="quick-prompts">
              {quickPrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setInput(prompt)}
                  className="quick-prompt-btn"
                >
                  {prompt}
                </button>
              ))}
            </div>
          )}

          <div className="chat-input-wrapper">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe what you want to discover..."
              rows={3}
              disabled={isLoading}
              className="chat-input"
            />
            <button
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
              className="btn-send"
            >
              {isLoading ? '...' : '→'}
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        .chat-interface {
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .chat-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 16px;
          overflow: hidden;
          backdrop-filter: blur(20px);
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .chat-message {
          display: flex;
          gap: 12px;
          max-width: 80%;
        }

        .chat-message.user {
          align-self: flex-end;
          flex-direction: row-reverse;
        }

        .chat-message.assistant {
          align-self: flex-start;
        }

        .message-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          overflow: hidden;
        }

        .avatar-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .message-content {
          flex: 1;
        }

        .message-role {
          font-size: 12px;
          font-weight: 600;
          color: rgba(255, 255, 255, 0.6);
          margin-bottom: 4px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .message-text {
          background: rgba(255, 255, 255, 0.05);
          padding: 12px 16px;
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: rgba(255, 255, 255, 0.9);
          line-height: 1.6;
        }

        .message-text p {
          margin: 0;
          margin-bottom: 8px;
        }

        .message-text p:last-child {
          margin-bottom: 0;
        }

        .chat-message.user .message-text {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-color: rgba(255, 255, 255, 0.2);
        }

        .typing-indicator {
          display: flex;
          gap: 4px;
          padding: 12px 16px;
        }

        .typing-indicator span {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.6);
          animation: typing 1.4s infinite;
        }

        .typing-indicator span:nth-child(2) {
          animation-delay: 0.2s;
        }

        .typing-indicator span:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.6;
          }
          30% {
            transform: translateY(-10px);
            opacity: 1;
          }
        }

        .chat-actions {
          padding: 16px 24px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          display: flex;
          justify-content: center;
        }

        .btn-start-discovery {
          padding: 12px 32px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          border-radius: 8px;
          color: white;
          font-weight: 600;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-start-discovery:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }

        .btn-start-discovery:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .chat-input-container {
          padding: 16px 24px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .quick-prompts {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 12px;
        }

        .quick-prompt-btn {
          padding: 8px 16px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 20px;
          color: rgba(255, 255, 255, 0.8);
          font-size: 13px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .quick-prompt-btn:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }

        .chat-input-wrapper {
          display: flex;
          gap: 12px;
          align-items: flex-end;
        }

        .chat-input {
          flex: 1;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 12px 16px;
          color: white;
          font-size: 14px;
          resize: none;
          font-family: inherit;
        }

        .chat-input:focus {
          outline: none;
          border-color: rgba(102, 126, 234, 0.5);
          background: rgba(255, 255, 255, 0.08);
        }

        .chat-input::placeholder {
          color: rgba(255, 255, 255, 0.4);
        }

        .btn-send {
          width: 48px;
          height: 48px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          border-radius: 12px;
          color: white;
          font-size: 20px;
          cursor: pointer;
          transition: all 0.2s;
          flex-shrink: 0;
        }

        .btn-send:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .btn-send:disabled {
          opacity: 0.3;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default ChatInterface;
