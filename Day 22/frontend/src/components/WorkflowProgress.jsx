import React from 'react';
import {
  CheckCircle2,
  Clock,
  ArrowRight,
  RotateCcw,
  AlertCircle,
  Cpu,
  Layers,
} from 'lucide-react';

const STAGES = [
  { id: 'coordinator', name: 'Coordinator', role: 'Workflow Planning & State Initialization' },
  { id: 'research', name: 'Research Agent', role: 'Fact Extraction & Source Cataloging' },
  { id: 'analyze', name: 'Analyzer', role: 'Thematic Breakdown & Pattern Detection' },
  { id: 'criticize', name: 'Critic', role: 'Peer Review, Consistency & Quality Scoring' },
  { id: 'write', name: 'Writer', role: 'Executive Synthesis & Critic Integration' },
];

export default function WorkflowProgress({ currentStep, workflowStatus, agentHistory, critique }) {
  // Map completed agents from history
  const completedAgentNames = new Set(
    (agentHistory || [])
      .filter((h) => h.status === 'completed')
      .map((h) => h.agent.toLowerCase())
  );

  const isWorkflowDone = workflowStatus === 'completed';
  const hasRefinement = (critique && critique.needs_refinement) || (agentHistory || []).some(h => h.iteration > 1);

  const getStageStatus = (stage) => {
    if (isWorkflowDone) return 'completed';

    // Coordinator is considered completed as soon as workflow starts running
    if (stage.id === 'coordinator') {
      return 'completed';
    }

    if (currentStep === stage.id) {
      return 'running';
    }

    if (completedAgentNames.has(stage.name.toLowerCase())) {
      return 'completed';
    }

    return 'pending';
  };

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-lg)',
      padding: '24px',
      marginBottom: '28px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={20} color="#3b82f6" />
            Workflow Execution Pipeline
          </h2>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
            Sequential stage progression governed by the Coordinator with feedback refinement checks.
          </p>
        </div>

        {hasRefinement && (
          <span className="badge badge-amber" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <RotateCcw size={13} />
            Refinement Loop Triggered
          </span>
        )}
      </div>

      {/* Pipeline Visual Stepper */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '12px',
      }}>
        {STAGES.map((stage, idx) => {
          const status = getStageStatus(stage);
          const isCurrent = status === 'running';
          const isDone = status === 'completed';

          return (
            <div
              key={stage.id}
              style={{
                background: isCurrent
                  ? 'rgba(59, 130, 246, 0.12)'
                  : isDone
                  ? 'rgba(16, 185, 129, 0.08)'
                  : 'var(--bg-card)',
                border: `1px solid ${
                  isCurrent
                    ? 'rgba(59, 130, 246, 0.5)'
                    : isDone
                    ? 'rgba(16, 185, 129, 0.35)'
                    : 'var(--border-color)'
                }`,
                borderRadius: 'var(--radius-md)',
                padding: '14px 16px',
                position: 'relative',
                transition: 'all 0.3s ease',
                boxShadow: isCurrent ? '0 0 16px rgba(59, 130, 246, 0.25)' : 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  color: isCurrent ? '#60a5fa' : isDone ? '#34d399' : 'var(--text-muted)',
                  textTransform: 'uppercase',
                }}>
                  Step {idx + 1}
                </span>

                {isDone ? (
                  <CheckCircle2 size={18} color="#10b981" />
                ) : isCurrent ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <div className="animate-spin" style={{ width: '14px', height: '14px', border: '2px solid #3b82f6', borderTopColor: 'transparent', borderRadius: '50%' }} />
                    <span style={{ fontSize: '0.72rem', color: '#60a5fa', fontWeight: 600 }}>Active</span>
                  </div>
                ) : (
                  <Clock size={16} color="var(--text-muted)" />
                )}
              </div>

              <div style={{ fontWeight: 700, fontSize: '0.98rem', color: isDone || isCurrent ? '#ffffff' : 'var(--text-secondary)', marginBottom: '4px' }}>
                {isDone ? '✓ ' : isCurrent ? '→ ' : ''}{stage.name}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.3' }}>
                {stage.role}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
