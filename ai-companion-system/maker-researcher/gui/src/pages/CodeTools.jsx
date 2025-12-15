import { useState } from 'react';
import {
  Code,
  FileCode,
  Bug,
  Loader2,
  Copy,
  Check,
  AlertTriangle,
  Lightbulb,
  BarChart,
} from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactMarkdown from 'react-markdown';
import { codeApi, debugApi } from '../services/api';

function CodeTools() {
  const [activeTab, setActiveTab] = useState('generate');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const [generateForm, setGenerateForm] = useState({
    description: '',
    language: 'python',
  });
  const [generatedCode, setGeneratedCode] = useState(null);

  const [analyzeForm, setAnalyzeForm] = useState({ filePath: '' });
  const [analysis, setAnalysis] = useState(null);

  const [debugForm, setDebugForm] = useState({ errorText: '', language: 'python' });
  const [debugResult, setDebugResult] = useState(null);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!generateForm.description.trim()) return;

    setLoading(true);
    try {
      const response = await codeApi.generate(
        generateForm.description,
        generateForm.language
      );
      setGeneratedCode(response.data);
    } catch (error) {
      console.error('Generate error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!analyzeForm.filePath.trim()) return;

    setLoading(true);
    try {
      const response = await codeApi.analyze(analyzeForm.filePath);
      setAnalysis(response.data);
    } catch (error) {
      console.error('Analyze error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDebug = async (e) => {
    e.preventDefault();
    if (!debugForm.errorText.trim()) return;

    setLoading(true);
    try {
      const response = await debugApi.analyze(debugForm.errorText, debugForm.language);
      setDebugResult(response.data);
    } catch (error) {
      console.error('Debug error:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyCode = async (code) => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const tabs = [
    { id: 'generate', label: 'Generate', icon: Code },
    { id: 'analyze', label: 'Analyze', icon: FileCode },
    { id: 'debug', label: 'Debug', icon: Bug },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Code Tools</h1>
        <p className="text-surface-400 mt-1">
          Generate, analyze, and debug code with AI assistance
        </p>
      </div>

      <div className="flex gap-2 border-b border-surface-700 pb-2">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === id
                ? 'bg-primary-600 text-white'
                : 'text-surface-400 hover:text-white hover:bg-surface-700'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {activeTab === 'generate' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="card-header">Generate Code</h3>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="block text-sm text-surface-400 mb-2">Description</label>
                <textarea
                  value={generateForm.description}
                  onChange={(e) =>
                    setGenerateForm((prev) => ({ ...prev, description: e.target.value }))
                  }
                  placeholder="Describe what code you need..."
                  className="textarea h-32"
                />
              </div>
              <div>
                <label className="block text-sm text-surface-400 mb-2">Language</label>
                <select
                  value={generateForm.language}
                  onChange={(e) =>
                    setGenerateForm((prev) => ({ ...prev, language: e.target.value }))
                  }
                  className="input"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="rust">Rust</option>
                  <option value="go">Go</option>
                </select>
              </div>
              <button
                type="submit"
                disabled={loading || !generateForm.description.trim()}
                className="btn btn-primary w-full flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Code className="w-4 h-4" />
                    Generate Code
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Generated Code</h3>
              {generatedCode?.code && (
                <button
                  onClick={() => copyCode(generatedCode.code)}
                  className="flex items-center gap-1 text-sm text-surface-400 hover:text-white"
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              )}
            </div>
            {generatedCode ? (
              <div className="space-y-4">
                <div className="rounded-lg overflow-hidden">
                  <SyntaxHighlighter
                    language={generateForm.language}
                    style={oneDark}
                    customStyle={{ margin: 0, borderRadius: '8px' }}
                  >
                    {generatedCode.code}
                  </SyntaxHighlighter>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-surface-400">Confidence:</span>
                  <div className="flex-1 h-2 bg-surface-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500"
                      style={{ width: `${(generatedCode.confidence || 0.8) * 100}%` }}
                    />
                  </div>
                  <span className="text-white">
                    {Math.round((generatedCode.confidence || 0.8) * 100)}%
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-center text-surface-500 py-12">
                <Code className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Generated code will appear here</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'analyze' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="card-header">Analyze File</h3>
            <form onSubmit={handleAnalyze} className="space-y-4">
              <div>
                <label className="block text-sm text-surface-400 mb-2">File Path</label>
                <input
                  type="text"
                  value={analyzeForm.filePath}
                  onChange={(e) => setAnalyzeForm({ filePath: e.target.value })}
                  placeholder="/path/to/your/file.py"
                  className="input"
                />
              </div>
              <button
                type="submit"
                disabled={loading || !analyzeForm.filePath.trim()}
                className="btn btn-primary w-full flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <BarChart className="w-4 h-4" />
                    Analyze
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="card">
            <h3 className="card-header">Analysis Results</h3>
            {analysis ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="stat-card">
                    <p className="stat-label">Lines of Code</p>
                    <p className="stat-value">{analysis.loc}</p>
                  </div>
                  <div className="stat-card">
                    <p className="stat-label">Complexity</p>
                    <p className="stat-value">{analysis.complexity.toFixed(1)}/10</p>
                  </div>
                  <div className="stat-card">
                    <p className="stat-label">Functions</p>
                    <p className="stat-value">{analysis.functions?.length || 0}</p>
                  </div>
                  <div className="stat-card">
                    <p className="stat-label">Classes</p>
                    <p className="stat-value">{analysis.classes?.length || 0}</p>
                  </div>
                </div>

                {analysis.issues?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-surface-300 mb-2 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-500" />
                      Issues ({analysis.issues.length})
                    </h4>
                    <ul className="space-y-2">
                      {analysis.issues.slice(0, 5).map((issue, index) => (
                        <li
                          key={index}
                          className="text-sm p-2 bg-surface-700/50 rounded text-surface-300"
                        >
                          <span
                            className={`badge mr-2 ${
                              issue.severity === 'error' ? 'badge-error' : 'badge-warning'
                            }`}
                          >
                            {issue.severity}
                          </span>
                          {issue.message}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {analysis.suggestions?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-surface-300 mb-2 flex items-center gap-2">
                      <Lightbulb className="w-4 h-4 text-amber-500" />
                      Suggestions
                    </h4>
                    <ul className="space-y-2">
                      {analysis.suggestions.map((suggestion, index) => (
                        <li
                          key={index}
                          className="text-sm p-2 bg-emerald-500/10 rounded text-surface-300 border border-emerald-500/20"
                        >
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center text-surface-500 py-12">
                <FileCode className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Analysis results will appear here</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'debug' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="card-header">Debug Error</h3>
            <form onSubmit={handleDebug} className="space-y-4">
              <div>
                <label className="block text-sm text-surface-400 mb-2">Error Message</label>
                <textarea
                  value={debugForm.errorText}
                  onChange={(e) =>
                    setDebugForm((prev) => ({ ...prev, errorText: e.target.value }))
                  }
                  placeholder="Paste your error message or stack trace here..."
                  className="textarea h-48 font-mono text-sm"
                />
              </div>
              <div>
                <label className="block text-sm text-surface-400 mb-2">Language</label>
                <select
                  value={debugForm.language}
                  onChange={(e) =>
                    setDebugForm((prev) => ({ ...prev, language: e.target.value }))
                  }
                  className="input"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                </select>
              </div>
              <button
                type="submit"
                disabled={loading || !debugForm.errorText.trim()}
                className="btn btn-primary w-full flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Bug className="w-4 h-4" />
                    Debug
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="card">
            <h3 className="card-header">Debug Analysis</h3>
            {debugResult ? (
              <div className="space-y-4">
                <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <p className="text-sm text-red-400 font-medium">
                    {debugResult.error_info?.type}: {debugResult.error_info?.message}
                  </p>
                  {debugResult.error_info?.file && (
                    <p className="text-xs text-surface-400 mt-1">
                      File: {debugResult.error_info.file}, Line: {debugResult.error_info.line}
                    </p>
                  )}
                </div>

                <div>
                  <h4 className="text-sm font-medium text-surface-300 mb-2">Analysis</h4>
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown>{debugResult.analysis}</ReactMarkdown>
                  </div>
                </div>

                {debugResult.suggested_fixes?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-surface-300 mb-2">Suggested Fixes</h4>
                    <div className="space-y-3">
                      {debugResult.suggested_fixes.map((fix, index) => (
                        <div
                          key={index}
                          className="p-3 bg-surface-700/50 rounded-lg border border-surface-600"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-white font-medium">{fix.description}</span>
                            <span
                              className={`badge ${
                                fix.confidence > 0.7
                                  ? 'badge-success'
                                  : fix.confidence > 0.4
                                  ? 'badge-warning'
                                  : 'badge-error'
                              }`}
                            >
                              {Math.round(fix.confidence * 100)}% confidence
                            </span>
                          </div>
                          {fix.code_change && (
                            <SyntaxHighlighter
                              language={debugForm.language}
                              style={oneDark}
                              customStyle={{ margin: 0, borderRadius: '4px', fontSize: '12px' }}
                            >
                              {fix.code_change}
                            </SyntaxHighlighter>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center text-surface-500 py-12">
                <Bug className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Debug analysis will appear here</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default CodeTools;
