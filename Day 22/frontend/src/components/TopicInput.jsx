import React from 'react';
import { Search, Sparkles, Loader2, Compass } from 'lucide-react';

const PRESET_TOPICS = [
  "Impact of generative AI on software development",
  "Autonomous Multi-Agent Systems in Supply Chain Optimization",
  "Post-Quantum Cryptography: Lattice-based vs Hash-based Standards",
  "Evaluating Hallucination Mitigation Techniques in Foundation Models"
];

export default function TopicInput({ query, setQuery, onStart, isRunning, onSelectPreset }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() || isRunning) return;
    onStart(query);
  };

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-lg)',
      padding: '24px',
      marginBottom: '28px',
      boxShadow: '0 8px 30px rgba(0, 0, 0, 0.25)'
    }}>
      <form onSubmit={handleSubmit}>
        <label style={{
          display: 'block',
          fontSize: '0.88rem',
          fontWeight: 700,
          color: 'var(--text-secondary)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: '10px'
        }}>
          Research Topic / Investigation Question
        </label>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: '280px' }}>
            <Search
              size={18}
              style={{
                position: 'absolute',
                left: '16px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)'
              }}
            />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Impact of generative AI on software development"
              disabled={isRunning}
              style={{
                width: '100%',
                padding: '14px 16px 14px 44px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '1rem',
                fontFamily: 'inherit',
                outline: 'none',
                transition: 'border-color 0.2s ease',
              }}
              onFocus={(e) => e.target.style.borderColor = 'var(--border-focus)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={!query.trim() || isRunning}
            style={{ minWidth: '170px' }}
          >
            {isRunning ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Orchestrating...
              </>
            ) : (
              <>
                <Sparkles size={18} />
                Start Research
              </>
            )}
          </button>
        </div>
      </form>

      {/* Preset Topics */}
      <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Compass size={13} />
          Sample Queries:
        </span>
        {PRESET_TOPICS.map((preset, idx) => (
          <button
            key={idx}
            type="button"
            disabled={isRunning}
            onClick={() => onSelectPreset(preset)}
            style={{
              background: 'rgba(36, 48, 76, 0.4)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-secondary)',
              fontSize: '0.78rem',
              padding: '4px 10px',
              cursor: isRunning ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => {
              if (!isRunning) {
                e.target.style.background = 'rgba(59, 130, 246, 0.15)';
                e.target.style.color = '#93c5fd';
                e.target.style.borderColor = 'rgba(59, 130, 246, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isRunning) {
                e.target.style.background = 'rgba(36, 48, 76, 0.4)';
                e.target.style.color = 'var(--text-secondary)';
                e.target.style.borderColor = 'var(--border-color)';
              }
            }}
          >
            {preset}
          </button>
        ))}
      </div>
    </div>
  );
}
