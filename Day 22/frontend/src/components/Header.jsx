import React from 'react';
import { Bot, Cpu, Sparkles, Database, Layers, CheckCircle2 } from 'lucide-react';

export default function Header({ systemInfo, onOpenInspector, hasActiveWorkflow }) {
  const isMock = systemInfo?.is_mock_mode ?? true;
  const provider = systemInfo?.llm_provider || 'mock';

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingBottom: '20px',
      marginBottom: '28px',
      borderBottom: '1px solid var(--border-color)',
      flexWrap: 'wrap',
      gap: '16px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '46px',
          height: '46px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 16px rgba(59, 130, 246, 0.4)'
        }}>
          <Bot size={26} color="#ffffff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.45rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#ffffff' }}>
            MULTI-AGENT RESEARCH ASSISTANT
          </h1>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)' }}>
            Autonomous Multi-Agent Pipeline: Coordinator • Research Agent • Analyzer • Critic • Writer
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
        <span className={`badge ${isMock ? 'badge-amber' : 'badge-emerald'}`} title={`Provider: ${provider}`}>
          <Cpu size={14} />
          {isMock ? 'Deterministic Mock Engine' : `LLM: ${provider.toUpperCase()}`}
        </span>

        <span className="badge badge-blue">
          <Layers size={14} />
          5 Specialized Agents
        </span>

        {hasActiveWorkflow && (
          <button
            onClick={onOpenInspector}
            className="btn btn-secondary"
            style={{ padding: '6px 12px', fontSize: '0.82rem' }}
            title="Inspect raw Shared State object"
          >
            <Database size={15} color="#38bdf8" />
            Shared State Inspector
          </button>
        )}
      </div>
    </header>
  );
}
