import { useState, useEffect } from 'react';
import {
  Zap,
  Cpu,
  MemoryStick,
  HardDrive,
  AlertTriangle,
  CheckCircle,
  Lightbulb,
  Loader2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { optimizeApi } from '../services/api';
import useStore from '../store/useStore';

function OptimizationCategory({ category }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between"
      >
        <h3 className="text-lg font-semibold text-white">{category.category}</h3>
        {expanded ? (
          <ChevronUp className="w-5 h-5 text-surface-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-surface-400" />
        )}
      </button>

      {expanded && (
        <ul className="mt-4 space-y-2">
          {category.recommendations.map((rec, index) => (
            <li key={index} className="flex items-start gap-3 p-3 bg-surface-700/50 rounded-lg">
              <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
              <span className="text-surface-300">{rec}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function SuggestionCard({ suggestion }) {
  const priorityColors = {
    1: 'bg-red-500/20 text-red-400 border-red-500/30',
    2: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    3: 'bg-primary-500/20 text-primary-400 border-primary-500/30',
    4: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  };

  const effortColors = {
    low: 'badge-success',
    medium: 'badge-warning',
    high: 'badge-error',
  };

  return (
    <div
      className={`p-4 rounded-lg border ${priorityColors[suggestion.priority] || priorityColors[3]}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <h4 className="font-medium text-white">{suggestion.title}</h4>
          <p className="text-sm text-surface-400 mt-1">{suggestion.description}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`badge ${effortColors[suggestion.effort] || 'badge-info'}`}>
            {suggestion.effort} effort
          </span>
        </div>
      </div>
      <div className="mt-3 p-2 bg-surface-800 rounded text-sm text-emerald-400">
        {suggestion.benefit}
      </div>
    </div>
  );
}

function Optimize() {
  const { optimizations, loading, fetchOptimizations, systemMetrics } = useStore();
  const [profile, setProfile] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchOptimizations();
  }, [fetchOptimizations]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const response = await optimizeApi.analyze();
      setProfile(response.data.profile);
      setSuggestions(response.data.suggestions);
    } catch (error) {
      console.error('Analyze error:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Optimize</h1>
          <p className="text-surface-400 mt-1">
            Performance analysis and optimization for RTX 4060
          </p>
        </div>
        <button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="btn btn-primary flex items-center gap-2"
        >
          {analyzing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Zap className="w-4 h-4" />
              Run Analysis
            </>
          )}
        </button>
      </div>

      {profile && (
        <div className="space-y-4">
          {profile.bottlenecks?.length > 0 && (
            <div className="card border-amber-500/50">
              <h3 className="card-header flex items-center gap-2 text-amber-400">
                <AlertTriangle className="w-5 h-5" />
                Bottlenecks Detected
              </h3>
              <ul className="space-y-2">
                {profile.bottlenecks.map((bottleneck, index) => (
                  <li key={index} className="flex items-center gap-2 text-surface-300">
                    <span className="w-2 h-2 rounded-full bg-amber-500" />
                    {bottleneck}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {profile.recommendations?.length > 0 && (
            <div className="card">
              <h3 className="card-header flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-amber-500" />
                Recommendations
              </h3>
              <ul className="space-y-2">
                {profile.recommendations.map((rec, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-3 p-3 bg-surface-700/50 rounded-lg"
                  >
                    <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                    <span className="text-surface-300">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {suggestions.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-4">
            Optimization Suggestions
          </h3>
          <div className="space-y-3">
            {suggestions.map((suggestion) => (
              <SuggestionCard key={suggestion.id} suggestion={suggestion} />
            ))}
          </div>
        </div>
      )}

      <div>
        <h3 className="text-lg font-semibold text-white mb-4">
          RTX 4060 Optimization Guide
        </h3>
        {loading.optimizations ? (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-500 mx-auto" />
            <p className="text-surface-400 mt-2">Loading optimizations...</p>
          </div>
        ) : optimizations?.hardware_optimizations ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {optimizations.hardware_optimizations.map((category, index) => (
              <OptimizationCategory key={index} category={category} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-surface-500">
            <Zap className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No optimization data available</p>
            <button onClick={fetchOptimizations} className="btn btn-secondary mt-4">
              Load Optimizations
            </button>
          </div>
        )}
      </div>

      {optimizations?.improvement_stats && (
        <div className="card">
          <h3 className="card-header">Improvement History</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="stat-card">
              <p className="stat-label">Total Improvements</p>
              <p className="stat-value">{optimizations.improvement_stats.total || 0}</p>
            </div>
            <div className="stat-card">
              <p className="stat-label">Successful</p>
              <p className="stat-value text-emerald-400">
                {optimizations.improvement_stats.successful || 0}
              </p>
            </div>
            <div className="stat-card">
              <p className="stat-label">Success Rate</p>
              <p className="stat-value text-primary-400">
                {optimizations.improvement_stats.success_rate?.toFixed(0) || 0}%
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Optimize;
