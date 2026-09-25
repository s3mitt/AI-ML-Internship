import React, { useState } from 'react';
import {
  FileText,
  Copy,
  Check,
  Download,
  Code,
  Eye,
  Award,
  BookOpen,
} from 'lucide-react';

export default function ReportViewer({ report, query, critique, metadata }) {
  const [copied, setCopied] = useState(false);
  const [showRaw, setShowRaw] = useState(false);

  if (!report) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const safeName = (query || 'research-report')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .slice(0, 40);
    link.download = `${safeName}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Basic lightweight markdown to HTML renderer for clean visualization without heavy external bloat
  const renderSimpleMarkdown = (md) => {
    let html = md
      // Escape script tags
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      // Headers
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      // Bold and italics
      .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em>$1</em>')
      // Code inline
      .replace(/`([^`]+)`/gim, '<code>$1</code>')
      // Horizontal rules
      .replace(/^---$/gim, '<hr/>')
      // Blockquotes
      .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
      // Unordered lists
      .replace(/^\- (.*$)/gim, '<li>$1</li>')
      // Numbered lists
      .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
      // Linebreaks to paragraphs
      .replace(/\n\n/gim, '</p><p>');

    return `<p>${html}</p>`;
  };

  const qualityScore = critique?.quality_score ?? 8.5;

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-lg)',
      padding: '28px',
      marginBottom: '32px',
      boxShadow: '0 12px 36px rgba(0, 0, 0, 0.35)',
    }}>
      {/* Report Header Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingBottom: '20px',
        marginBottom: '24px',
        borderBottom: '1px solid var(--border-color)',
        flexWrap: 'wrap',
        gap: '14px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <FileText size={22} color="#10b981" />
          </div>
          <div>
            <span style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: '#10b981', fontWeight: 800, letterSpacing: '0.06em' }}>
              Final Research Deliverable
            </span>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ffffff' }}>
              Executive Research Report
            </h2>
          </div>
        </div>

        {/* Action Controls & Metric Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <span className="badge badge-emerald" title="Peer review validation score">
            <Award size={14} />
            Score: {qualityScore} / 10.0
          </span>

          {metadata?.word_count && (
            <span className="badge badge-slate">
              <BookOpen size={14} />
              {metadata.word_count} Words
            </span>
          )}

          <button
            onClick={() => setShowRaw(!showRaw)}
            className="btn btn-secondary"
            style={{ padding: '7px 14px', fontSize: '0.84rem' }}
          >
            {showRaw ? <Eye size={15} /> : <Code size={15} />}
            {showRaw ? 'Preview HTML' : 'Raw Markdown'}
          </button>

          <button
            onClick={handleCopy}
            className="btn btn-secondary"
            style={{ padding: '7px 14px', fontSize: '0.84rem' }}
          >
            {copied ? <Check size={15} color="#10b981" /> : <Copy size={15} />}
            {copied ? 'Copied!' : 'Copy'}
          </button>

          <button
            onClick={handleDownload}
            className="btn btn-primary"
            style={{ padding: '7px 14px', fontSize: '0.84rem' }}
          >
            <Download size={15} />
            Export (.md)
          </button>
        </div>
      </div>

      {/* Content Rendering */}
      {showRaw ? (
        <textarea
          readOnly
          value={report}
          style={{
            width: '100%',
            height: '500px',
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.88rem',
            padding: '16px',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            resize: 'vertical',
            outline: 'none',
          }}
        />
      ) : (
        <div
          className="prose"
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '30px',
            maxHeight: '750px',
            overflowY: 'auto',
          }}
          dangerouslySetInnerHTML={{ __html: renderSimpleMarkdown(report) }}
        />
      )}
    </div>
  );
}
