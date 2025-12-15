import { useState } from 'react';
import {
  Search,
  Globe,
  GraduationCap,
  Code,
  Newspaper,
  ExternalLink,
  Loader2,
  Star,
  Calendar,
  Users,
  Send,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { researchApi, chatApi } from '../services/api';
import useStore from '../store/useStore';

function ResearchCard({ type, data }) {
  const icons = {
    web: Globe,
    paper: GraduationCap,
    code: Code,
    news: Newspaper,
  };
  const Icon = icons[type] || Globe;

  const colors = {
    web: 'border-primary-500/30 bg-primary-500/5',
    paper: 'border-emerald-500/30 bg-emerald-500/5',
    code: 'border-amber-500/30 bg-amber-500/5',
    news: 'border-purple-500/30 bg-purple-500/5',
  };

  return (
    <div className={`p-4 rounded-lg border ${colors[type]} hover:bg-surface-700/50 transition-colors`}>
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 text-surface-400 flex-shrink-0 mt-1" />
        <div className="flex-1 min-w-0">
          <h4 className="text-white font-medium truncate">{data.title}</h4>
          {data.snippet && (
            <p className="text-sm text-surface-400 mt-1 line-clamp-2">{data.snippet}</p>
          )}
          {data.authors && (
            <div className="flex items-center gap-2 mt-2 text-sm text-surface-500">
              <Users className="w-4 h-4" />
              <span className="truncate">{data.authors.slice(0, 3).join(', ')}</span>
            </div>
          )}
          {data.year && (
            <div className="flex items-center gap-2 mt-1 text-sm text-surface-500">
              <Calendar className="w-4 h-4" />
              <span>{data.year}</span>
              {data.citations !== undefined && (
                <span className="ml-2">| {data.citations} citations</span>
              )}
            </div>
          )}
          {data.stars !== undefined && (
            <div className="flex items-center gap-2 mt-2 text-sm text-surface-500">
              <Star className="w-4 h-4 text-amber-500" />
              <span>{data.stars.toLocaleString()} stars</span>
              {data.language && (
                <span className="ml-2 px-2 py-0.5 bg-surface-700 rounded text-xs">
                  {data.language}
                </span>
              )}
            </div>
          )}
          {data.url && (
            <a
              href={data.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 mt-2 text-sm text-primary-400 hover:text-primary-300"
            >
              <ExternalLink className="w-3 h-3" />
              Open
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

function Research() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [options, setOptions] = useState({
    includePapers: true,
    includeCode: true,
    includeNews: false,
  });

  const { addResearchSession, researchSessions } = useStore();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await researchApi.search(query, options);
      setResults(response.data);
      addResearchSession({
        id: response.data.session_id,
        query,
        timestamp: new Date().toISOString(),
        webResults: response.data.web_results,
        papers: response.data.papers,
        codeExamples: response.data.code_examples,
      });
    } catch (error) {
      console.error('Research error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await chatApi.sendMessage(userMessage);
      setChatMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.data.response, agent: response.data.agent },
      ]);
    } catch (error) {
      setChatMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, an error occurred.', error: true },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Research</h1>
        <p className="text-surface-400 mt-1">
          Search the web, academic papers, and code repositories
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-500" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="What would you like to research?"
                  className="input pl-12"
                />
              </div>

              <div className="flex flex-wrap items-center gap-4">
                <label className="flex items-center gap-2 text-sm text-surface-300">
                  <input
                    type="checkbox"
                    checked={options.includePapers}
                    onChange={(e) =>
                      setOptions((prev) => ({ ...prev, includePapers: e.target.checked }))
                    }
                    className="rounded border-surface-600 bg-surface-700 text-primary-500 focus:ring-primary-500"
                  />
                  Academic Papers
                </label>
                <label className="flex items-center gap-2 text-sm text-surface-300">
                  <input
                    type="checkbox"
                    checked={options.includeCode}
                    onChange={(e) =>
                      setOptions((prev) => ({ ...prev, includeCode: e.target.checked }))
                    }
                    className="rounded border-surface-600 bg-surface-700 text-primary-500 focus:ring-primary-500"
                  />
                  Code Examples
                </label>
                <label className="flex items-center gap-2 text-sm text-surface-300">
                  <input
                    type="checkbox"
                    checked={options.includeNews}
                    onChange={(e) =>
                      setOptions((prev) => ({ ...prev, includeNews: e.target.checked }))
                    }
                    className="rounded border-surface-600 bg-surface-700 text-primary-500 focus:ring-primary-500"
                  />
                  News
                </label>
                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="btn btn-primary ml-auto flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Researching...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      Search
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {results && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 text-sm text-surface-400">
                <span className="badge badge-info">
                  {results.web_results} web results
                </span>
                <span className="badge badge-success">
                  {results.papers} papers
                </span>
                <span className="badge badge-warning">
                  {results.code_examples} code examples
                </span>
              </div>

              {results.formatted && (
                <div className="card">
                  <h3 className="card-header">Research Summary</h3>
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown>{results.formatted.slice(0, 3000)}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="card h-[500px] flex flex-col">
            <h3 className="card-header">Research Assistant</h3>
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {chatMessages.length === 0 ? (
                <div className="text-center text-surface-500 py-8">
                  <Search className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Ask me anything about your research</p>
                </div>
              ) : (
                chatMessages.map((msg, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-primary-600/20 ml-8'
                        : msg.error
                        ? 'bg-red-500/20 mr-8'
                        : 'bg-surface-700 mr-8'
                    }`}
                  >
                    {msg.agent && (
                      <span className="text-xs text-primary-400 uppercase mb-1 block">
                        {msg.agent}
                      </span>
                    )}
                    <div className="prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </div>
                ))
              )}
              {chatLoading && (
                <div className="flex items-center gap-2 text-surface-400 p-3">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Thinking...
                </div>
              )}
            </div>
            <form onSubmit={handleChat} className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask a question..."
                className="input flex-1"
              />
              <button
                type="submit"
                disabled={chatLoading || !chatInput.trim()}
                className="btn btn-primary"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>

          {researchSessions.length > 0 && (
            <div className="card">
              <h3 className="card-header">Recent Sessions</h3>
              <div className="space-y-2">
                {researchSessions.slice(0, 5).map((session) => (
                  <div
                    key={session.id}
                    className="p-3 rounded-lg bg-surface-700/50 hover:bg-surface-700 transition-colors cursor-pointer"
                    onClick={() => setQuery(session.query)}
                  >
                    <p className="text-white truncate">{session.query}</p>
                    <p className="text-xs text-surface-500 mt-1">
                      {new Date(session.timestamp).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Research;
