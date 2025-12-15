import { useState, useEffect } from 'react';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  FileCode,
  Loader2,
  ChevronDown,
  ChevronUp,
  Shield,
  Clock,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { approvalApi } from '../services/api';
import useStore from '../store/useStore';

const riskColors = {
  1: { label: 'Safe', color: 'text-emerald-400', bg: 'bg-emerald-500/20' },
  2: { label: 'Low', color: 'text-primary-400', bg: 'bg-primary-500/20' },
  3: { label: 'Medium', color: 'text-amber-400', bg: 'bg-amber-500/20' },
  4: { label: 'High', color: 'text-orange-400', bg: 'bg-orange-500/20' },
  5: { label: 'Critical', color: 'text-red-400', bg: 'bg-red-500/20' },
};

function DiffViewer({ diff }) {
  if (!diff) return null;

  const lines = diff.split('\n');

  return (
    <div className="font-mono text-xs bg-surface-900 rounded-lg overflow-x-auto">
      {lines.map((line, index) => {
        let bgColor = '';
        let textColor = 'text-surface-300';

        if (line.startsWith('+') && !line.startsWith('+++')) {
          bgColor = 'bg-emerald-500/10';
          textColor = 'text-emerald-400';
        } else if (line.startsWith('-') && !line.startsWith('---')) {
          bgColor = 'bg-red-500/10';
          textColor = 'text-red-400';
        } else if (line.startsWith('@@')) {
          bgColor = 'bg-primary-500/10';
          textColor = 'text-primary-400';
        }

        return (
          <div key={index} className={`px-4 py-0.5 ${bgColor} ${textColor}`}>
            {line || '\u00A0'}
          </div>
        );
      })}
    </div>
  );
}

function ChangeCard({ change, expanded, onToggle }) {
  const risk = riskColors[change.risk_level] || riskColors[3];

  return (
    <div className="border border-surface-700 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between hover:bg-surface-700/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <FileCode className="w-5 h-5 text-surface-400" />
          <div className="text-left">
            <p className="text-white font-medium">{change.title}</p>
            <p className="text-sm text-surface-400">{change.file_path || 'No file'}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className={`badge ${risk.bg} ${risk.color}`}>
            {risk.label} Risk
          </span>
          {expanded ? (
            <ChevronUp className="w-5 h-5 text-surface-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-surface-400" />
          )}
        </div>
      </button>

      {expanded && (
        <div className="p-4 border-t border-surface-700 space-y-4">
          <div>
            <h4 className="text-sm font-medium text-surface-300 mb-2">Description</h4>
            <p className="text-surface-400">{change.description}</p>
          </div>

          {change.rationale && (
            <div>
              <h4 className="text-sm font-medium text-surface-300 mb-2">Rationale</h4>
              <p className="text-surface-400">{change.rationale}</p>
            </div>
          )}

          {change.diff && (
            <div>
              <h4 className="text-sm font-medium text-surface-300 mb-2">Changes</h4>
              <DiffViewer diff={change.diff} />
            </div>
          )}

          {change.command && (
            <div>
              <h4 className="text-sm font-medium text-surface-300 mb-2">Command</h4>
              <code className="block p-3 bg-surface-900 rounded-lg text-amber-400 text-sm">
                {change.command}
              </code>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ApprovalCard({ approval, onApprove, onReject, loading }) {
  const [expanded, setExpanded] = useState(false);
  const [expandedChanges, setExpandedChanges] = useState({});
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);

  const toggleChange = (index) => {
    setExpandedChanges((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const handleReject = () => {
    onReject(approval.id, rejectReason);
    setShowRejectModal(false);
    setRejectReason('');
  };

  const maxRisk = Math.max(...approval.changes.map((c) => c.risk_level || 1));
  const risk = riskColors[maxRisk] || riskColors[3];

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${risk.bg}`}>
              <Shield className={`w-5 h-5 ${risk.color}`} />
            </div>
            <div>
              <h3 className="text-white font-medium">{approval.summary}</h3>
              <p className="text-sm text-surface-400">Request ID: {approval.id}</p>
            </div>
          </div>
          <div className="flex items-center gap-4 mt-3">
            <span className="badge badge-info">{approval.changes.length} change(s)</span>
            <span className={`badge ${risk.bg} ${risk.color}`}>{risk.label} Risk</span>
            <span className="text-xs text-surface-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatDistanceToNow(new Date(approval.created_at), { addSuffix: true })}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onApprove(approval.id)}
            disabled={loading}
            className="btn btn-success flex items-center gap-2"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <CheckCircle className="w-4 h-4" />
            )}
            Approve
          </button>
          <button
            onClick={() => setShowRejectModal(true)}
            disabled={loading}
            className="btn btn-danger flex items-center gap-2"
          >
            <XCircle className="w-4 h-4" />
            Reject
          </button>
        </div>
      </div>

      {approval.impact_analysis && (
        <div className="mt-4 p-3 bg-surface-700/50 rounded-lg">
          <h4 className="text-sm font-medium text-surface-300 mb-1">Impact Analysis</h4>
          <p className="text-sm text-surface-400">{approval.impact_analysis}</p>
        </div>
      )}

      {approval.rollback_plan && (
        <div className="mt-4 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg">
          <h4 className="text-sm font-medium text-amber-400 mb-1 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Rollback Plan
          </h4>
          <p className="text-sm text-surface-300 whitespace-pre-line">
            {approval.rollback_plan}
          </p>
        </div>
      )}

      <div className="mt-4">
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1"
        >
          {expanded ? (
            <>
              <ChevronUp className="w-4 h-4" />
              Hide Changes
            </>
          ) : (
            <>
              <ChevronDown className="w-4 h-4" />
              View Changes ({approval.changes.length})
            </>
          )}
        </button>

        {expanded && (
          <div className="mt-4 space-y-3">
            {approval.changes.map((change, index) => (
              <ChangeCard
                key={index}
                change={change}
                expanded={expandedChanges[index]}
                onToggle={() => toggleChange(index)}
              />
            ))}
          </div>
        )}
      </div>

      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card w-full max-w-md mx-4">
            <h3 className="text-lg font-bold text-white mb-4">Reject Changes</h3>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Reason for rejection (optional)..."
              className="textarea h-24 mb-4"
            />
            <div className="flex gap-3">
              <button
                onClick={() => setShowRejectModal(false)}
                className="btn btn-secondary flex-1"
              >
                Cancel
              </button>
              <button onClick={handleReject} className="btn btn-danger flex-1">
                Reject
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Approvals() {
  const { approvals, loading, fetchApprovals, processApproval } = useStore();
  const [processingId, setProcessingId] = useState(null);

  useEffect(() => {
    fetchApprovals();
  }, [fetchApprovals]);

  const handleApprove = async (requestId) => {
    setProcessingId(requestId);
    await processApproval(requestId, true);
    setProcessingId(null);
  };

  const handleReject = async (requestId, notes) => {
    setProcessingId(requestId);
    await processApproval(requestId, false, notes);
    setProcessingId(null);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Approvals</h1>
        <p className="text-surface-400 mt-1">
          Review and approve proposed changes before they are applied
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="stat-card">
          <p className="stat-label">Pending</p>
          <p className="stat-value text-amber-400">{approvals.length}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Auto-Approve Eligible</p>
          <p className="stat-value text-emerald-400">
            {approvals.filter((a) => a.auto_approve_eligible).length}
          </p>
        </div>
        <div className="stat-card">
          <p className="stat-label">High Risk</p>
          <p className="stat-value text-red-400">
            {approvals.filter((a) => a.changes.some((c) => c.risk_level >= 4)).length}
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {loading.approvals ? (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-500 mx-auto" />
            <p className="text-surface-400 mt-2">Loading approvals...</p>
          </div>
        ) : approvals.length > 0 ? (
          approvals.map((approval) => (
            <ApprovalCard
              key={approval.id}
              approval={approval}
              onApprove={handleApprove}
              onReject={handleReject}
              loading={processingId === approval.id}
            />
          ))
        ) : (
          <div className="text-center py-12">
            <CheckCircle className="w-12 h-12 mx-auto text-emerald-500 mb-4" />
            <p className="text-white font-medium">All caught up!</p>
            <p className="text-surface-400 mt-1">No pending approvals</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Approvals;
