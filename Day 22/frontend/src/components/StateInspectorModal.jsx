import React, { useState } from 'react';
import { X, Copy, Check, Database, Code, Activity, AlertCircle } from 'lucide-react';

export default function StateInspectorModal({ isOpen, onClose, stateData }) {
  const [activeTab, setActiveTab] = useState('full');
  const [copied, setCopied] = useState(false);

  if (!isOpen || !stateData) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(stateData, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(5, 8, 15, 0.85)',
      backdropFilter: 'blur(6px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px',
    }}>
      <div style={{
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-xl)',
        width: '100%',
        maxWidth: '920px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.7)',
        overflow: 'hidden',
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '18px 24px',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Database size={20} color="#38bdf8" />
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#ffffff' }}>
                Explicit Shared State Inspector
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Workflow ID: <code style={{ color: '#38bdf8' }}>{stateData.workflow_id}</code>
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button onClick={handleCopy} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
              {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
              {copied ? 'Copied' : 'Copy JSON'}
            </button>
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '6px',
                borderRadius: '6px',
              }}
              onMouseEnter={(e) => e.target.style.color = '#fff'}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div style={{
          display: 'flex',
          gap: '8px',
          padding: '10px 24px',
          borderBottom: '1px solid var(--border-color)',
          background: 'var(--bg-card)',
        }}>
          {[
            { id: 'full', label: 'Full State JSON', icon: Code },
            { id: 'history', label: `Agent History (${stateData.agent_history?.length || 0})`, icon: Activity },
            { id: 'errors', label: `Errors (${stateData.errors?.length || 0})`, icon: AlertCircle },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: activeTab === tab.id ? 'var(--bg-secondary)' : 'transparent',
                color: activeTab === tab.id ? '#ffffff' : 'var(--text-secondary)',
                border: `1px solid ${activeTab === tab.id ? 'var(--border-color)' : 'transparent'}`,
                borderRadius: 'var(--radius-sm)',
                padding: '6px 12px',
                fontSize: '0.82rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontWeight: activeTab === tab.id ? 600 : 400,
              }}
            >
              <tab.icon size={14} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Modal Body */}
        <div style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
          {activeTab === 'full' && (
            <pre style={{
              background: 'var(--bg-primary)',
              padding: '16px',
              borderRadius: 'var(--radius-md)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.82rem',
              color: '#93c5fd',
              overflowX: 'auto',
              border: '1px solid var(--border-color)',
            }}>
              {JSON.stringify(stateData, null, 2)}
            </pre>
          )}

          {activeTab === 'history' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {stateData.agent_history?.map((h, i) => (
                <div key={i} style={{ padding: '12px', background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', fontSize: '0.84rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <strong style={{ color: '#fff' }}>{h.agent}</strong>
                    <span style={{ color: '#34d399' }}>{h.duration_seconds}s</span>
                  </div>
                  <div style={{ color: 'var(--text-secondary)', marginBottom: '4px' }}><strong>Input:</strong> {h.input_summary}</div>
                  <div style={{ color: '#93c5fd' }}><strong>Output:</strong> {h.output_summary}</div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'errors' && (
            <div>
              {(!stateData.errors || stateData.errors.length === 0) ? (
                <p style={{ color: '#34d399', fontSize: '0.9rem' }}>No errors recorded during workflow execution. All stages executed cleanly.</p>
              ) : (
                stateData.errors.map((err, i) => (
                  <div key={i} style={{ padding: '12px', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-sm)', marginBottom: '8px' }}>
                    <strong style={{ color: '#fb7185' }}>{err.agent} ({err.error_type}):</strong>
                    <div style={{ color: '#fda4af', fontSize: '0.84rem', marginTop: '4px' }}>{err.message}</div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
