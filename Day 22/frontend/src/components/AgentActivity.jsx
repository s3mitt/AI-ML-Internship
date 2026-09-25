import React, { useState } from 'react';
import {
  Activity,
  CheckCircle2,
  Clock,
  ChevronDown,
  ChevronUp,
  FileText,
  Search,
  PieChart,
  ShieldCheck,
  PenTool,
  AlertTriangle,
  BookOpen,
} from 'lucide-react';

const AGENT_ICONS = {
  'Coordinator': Activity,
  'Research Agent': Search,
  'Analyzer': PieChart,
  'Critic': ShieldCheck,
  'Writer': PenTool,
};

export default function AgentActivity({
  agentHistory,
  researchFindings,
  sources,
  analysis,
  critique,
  reportMetadata,
  currentStep,
  workflowStatus,
}) {
  const [expandedAgent, setExpandedAgent] = useState(null);

  const toggleExpand = (agentName) => {
    setExpandedAgent(expandedAgent === agentName ? null : agentName);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <span className="badge badge-emerald"><CheckCircle2 size={12} /> Completed</span>;
      case 'running':
        return <span className="badge badge-blue"><Clock size={12} className="animate-spin" /> Running</span>;
      case 'failed':
        return <span className="badge badge-rose"><AlertTriangle size={12} /> Failed</span>;
      default:
        return <span className="badge badge-slate">Pending</span>;
    }
  };

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-lg)',
      padding: '24px',
      marginBottom: '28px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={20} color="#10b981" />
            Agent Activity & Execution Audit Log
          </h2>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
            Transparent telemetry tracking input/output contracts, duration, and shared state mutations.
          </p>
        </div>
        <span className="badge badge-slate">
          {agentHistory?.length || 0} Events Recorded
        </span>
      </div>

      {(!agentHistory || agentHistory.length === 0) && (
        <div style={{
          textAlign: 'center',
          padding: '40px 20px',
          background: 'var(--bg-card)',
          borderRadius: 'var(--radius-md)',
          color: 'var(--text-muted)',
          fontSize: '0.9rem',
        }}>
          Waiting for workflow execution to start. Submit a research topic above to trigger agents.
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {agentHistory?.map((record, index) => {
          const Icon = AGENT_ICONS[record.agent] || Activity;
          const isExpanded = expandedAgent === `${record.agent}_${index}`;

          return (
            <div
              key={index}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                overflow: 'hidden',
                transition: 'all 0.2s ease',
              }}
            >
              {/* Card Header */}
              <div
                onClick={() => toggleExpand(`${record.agent}_${index}`)}
                style={{
                  padding: '16px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  userSelect: 'none',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '8px',
                    background: 'rgba(59, 130, 246, 0.12)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: '1px solid rgba(59, 130, 246, 0.25)',
                  }}>
                    <Icon size={18} color="#60a5fa" />
                  </div>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.96rem', color: '#ffffff' }}>
                        {record.agent}
                      </span>
                      {record.iteration > 1 && (
                        <span className="badge badge-amber" style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                          Refinement Iteration {record.iteration}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Duration: <strong style={{ color: '#e2e8f0' }}>{record.duration_seconds}s</strong> • End: {new Date(record.end_time).toLocaleTimeString()}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  {getStatusBadge(record.status)}
                  {isExpanded ? <ChevronUp size={18} color="var(--text-muted)" /> : <ChevronDown size={18} color="var(--text-muted)" />}
                </div>
              </div>

              {/* Summary Bar */}
              <div style={{
                padding: '10px 20px 14px',
                borderTop: '1px solid rgba(36, 48, 76, 0.5)',
                fontSize: '0.86rem',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '12px',
                background: 'rgba(10, 13, 20, 0.3)',
              }}>
                <div>
                  <span style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, display: 'block' }}>
                    Input Summary
                  </span>
                  <span style={{ color: 'var(--text-secondary)' }}>{record.input_summary}</span>
                </div>
                <div>
                  <span style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, display: 'block' }}>
                    Output Summary
                  </span>
                  <span style={{ color: '#93c5fd' }}>{record.output_summary}</span>
                </div>
              </div>

              {/* Expanded Detailed Artifacts */}
              {isExpanded && (
                <div style={{
                  padding: '16px 20px',
                  borderTop: '1px solid var(--border-color)',
                  background: 'rgba(17, 23, 38, 0.8)',
                }}>
                  {record.agent === 'Research Agent' && (
                    <div>
                      <h4 style={{ fontSize: '0.86rem', color: '#60a5fa', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Extracted Findings ({researchFindings?.length || 0}) & Sources ({sources?.length || 0})
                      </h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px', marginTop: '10px' }}>
                        {researchFindings?.slice(0, 4).map((fnd, idx) => (
                          <div key={idx} style={{ padding: '10px 12px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', fontSize: '0.82rem' }}>
                            <div style={{ fontWeight: 700, color: '#e2e8f0', marginBottom: '4px' }}>{fnd.title}</div>
                            <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem' }}>{fnd.fact}</div>
                            <div style={{ marginTop: '6px', fontSize: '0.72rem', color: '#38bdf8' }}>Ref: [{fnd.source_id}] • Conf: {(fnd.confidence * 100).toFixed(0)}%</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {record.agent === 'Analyzer' && analysis && (
                    <div>
                      <h4 style={{ fontSize: '0.86rem', color: '#c084fc', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Identified Themes & Empirical Facts
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {analysis.themes?.map((thm, idx) => (
                          <div key={idx} style={{ padding: '8px 12px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', fontSize: '0.82rem' }}>
                            <strong style={{ color: '#f8fafc' }}>{thm.name}</strong>: {thm.summary}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {record.agent === 'Critic' && critique && (
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                        <h4 style={{ fontSize: '0.86rem', color: '#fbbf24', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                          Peer Critique Assessment
                        </h4>
                        <span className="badge badge-amber" style={{ fontSize: '0.82rem' }}>
                          Score: {critique.quality_score} / 10.0
                        </span>
                      </div>
                      <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                        <strong>Overall Verdict:</strong> {critique.overall_assessment}
                      </p>
                      {critique.recommendations?.length > 0 && (
                        <div>
                          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700 }}>Recommendations:</span>
                          <ul style={{ paddingLeft: '20px', fontSize: '0.8rem', color: '#e2e8f0', marginTop: '4px' }}>
                            {critique.recommendations.map((rec, i) => (
                              <li key={i}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {record.agent === 'Writer' && reportMetadata && (
                    <div>
                      <h4 style={{ fontSize: '0.86rem', color: '#34d399', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Report Synthesis Metadata
                      </h4>
                      <div style={{ display: 'flex', gap: '20px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                        <span>Words: <strong style={{ color: '#fff' }}>{reportMetadata.word_count}</strong></span>
                        <span>Characters: <strong style={{ color: '#fff' }}>{reportMetadata.character_count}</strong></span>
                        <span>Sources Cited: <strong style={{ color: '#fff' }}>{reportMetadata.sources_cited}</strong></span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
