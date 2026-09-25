import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import TopicInput from './components/TopicInput';
import WorkflowProgress from './components/WorkflowProgress';
import AgentActivity from './components/AgentActivity';
import ReportViewer from './components/ReportViewer';
import StateInspectorModal from './components/StateInspectorModal';
import { fetchSystemInfo, startResearch } from './services/api';
import { AlertCircle, Terminal, HelpCircle } from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('Impact of generative AI on software development');
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [systemInfo, setSystemInfo] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);
  const [workflowStatus, setWorkflowStatus] = useState('idle');
  const [stateData, setStateData] = useState(null);
  const [inspectorOpen, setInspectorOpen] = useState(false);

  useEffect(() => {
    fetchSystemInfo()
      .then((data) => setSystemInfo(data))
      .catch((err) => {
        console.warn('System info fetch error:', err);
        setSystemInfo({ is_mock_mode: true, llm_provider: 'mock' });
      });
  }, []);

  const handleStartResearch = async (searchQuery) => {
    setIsRunning(true);
    setError(null);
    setWorkflowStatus('running');
    setStateData(null);

    // Provide progressive UI feedback simulating active multi-agent handoffs
    const stepSequence = ['coordinator', 'research', 'analyze', 'criticize', 'write'];
    let stepIndex = 0;
    setCurrentStep(stepSequence[stepIndex]);

    const stepInterval = setInterval(() => {
      stepIndex++;
      if (stepIndex < stepSequence.length) {
        setCurrentStep(stepSequence[stepIndex]);
      }
    }, 450);

    try {
      const response = await startResearch(searchQuery);
      clearInterval(stepInterval);
      setCurrentStep(null);
      setWorkflowStatus(response.status || 'completed');
      setStateData(response);
    } catch (err) {
      clearInterval(stepInterval);
      setCurrentStep(null);
      setWorkflowStatus('failed');
      setError(err.message || 'An unexpected error occurred during workflow execution.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSelectPreset = (preset) => {
    setQuery(preset);
  };

  return (
    <div className="container">
      <Header
        systemInfo={systemInfo}
        onOpenInspector={() => setInspectorOpen(true)}
        hasActiveWorkflow={Boolean(stateData)}
      />

      {error && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '16px 20px',
          background: 'rgba(244, 63, 94, 0.12)',
          border: '1px solid rgba(244, 63, 94, 0.4)',
          borderRadius: 'var(--radius-md)',
          color: '#fb7185',
          marginBottom: '24px',
        }}>
          <AlertCircle size={20} />
          <div>
            <strong>Workflow Error:</strong> {error}
          </div>
        </div>
      )}

      <TopicInput
        query={query}
        setQuery={setQuery}
        onStart={handleStartResearch}
        isRunning={isRunning}
        onSelectPreset={handleSelectPreset}
      />

      <WorkflowProgress
        currentStep={currentStep}
        workflowStatus={workflowStatus}
        agentHistory={stateData?.agent_history || []}
        critique={stateData?.critique}
      />

      <AgentActivity
        agentHistory={stateData?.agent_history || []}
        researchFindings={stateData?.research_findings || []}
        sources={stateData?.sources || []}
        analysis={stateData?.analysis || {}}
        critique={stateData?.critique || {}}
        reportMetadata={stateData?.metadata || {}}
        currentStep={currentStep}
        workflowStatus={workflowStatus}
      />

      <ReportViewer
        report={stateData?.final_report}
        query={stateData?.query || query}
        critique={stateData?.critique}
        metadata={stateData?.metadata}
      />

      <StateInspectorModal
        isOpen={inspectorOpen}
        onClose={() => setInspectorOpen(false)}
        stateData={stateData}
      />
    </div>
  );
}
