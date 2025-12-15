import { useState, useEffect } from 'react';
import {
  ListTodo,
  Plus,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  AlertCircle,
  Trash2,
  Filter,
  ChevronDown,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import useStore from '../store/useStore';

const statusConfig = {
  pending: { icon: Clock, color: 'text-surface-400', bg: 'bg-surface-500/20' },
  in_progress: { icon: Loader2, color: 'text-primary-400', bg: 'bg-primary-500/20', animate: true },
  completed: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/20' },
  failed: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/20' },
  awaiting_approval: { icon: AlertCircle, color: 'text-amber-400', bg: 'bg-amber-500/20' },
  cancelled: { icon: XCircle, color: 'text-surface-500', bg: 'bg-surface-500/20' },
};

const categoryColors = {
  research: 'border-primary-500/50',
  code: 'border-emerald-500/50',
  debug: 'border-red-500/50',
  optimize: 'border-amber-500/50',
  advise: 'border-purple-500/50',
  system: 'border-surface-500/50',
};

function TaskCard({ task, onCancel }) {
  const config = statusConfig[task.status] || statusConfig.pending;
  const StatusIcon = config.icon;

  return (
    <div
      className={`card border-l-4 ${categoryColors[task.category] || 'border-surface-500/50'}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${config.bg}`}>
            <StatusIcon
              className={`w-5 h-5 ${config.color} ${config.animate ? 'animate-spin' : ''}`}
            />
          </div>
          <div>
            <h3 className="text-white font-medium">{task.title}</h3>
            <p className="text-sm text-surface-400 mt-1 line-clamp-2">{task.description}</p>
            <div className="flex items-center gap-4 mt-3">
              <span className="badge badge-info capitalize">{task.category}</span>
              <span className="text-xs text-surface-500">
                {formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}
              </span>
              {task.requires_approval && (
                <span className="badge badge-warning">Requires Approval</span>
              )}
            </div>
          </div>
        </div>
        {(task.status === 'pending' || task.status === 'awaiting_approval') && (
          <button
            onClick={() => onCancel(task.id)}
            className="p-2 text-surface-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      {task.result && (
        <div className="mt-4 pt-4 border-t border-surface-700">
          {task.result.success ? (
            <div className="text-sm text-emerald-400">
              <CheckCircle className="w-4 h-4 inline mr-2" />
              Completed successfully
            </div>
          ) : (
            <div className="text-sm text-red-400">
              <XCircle className="w-4 h-4 inline mr-2" />
              {task.result.error || 'Task failed'}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function CreateTaskModal({ isOpen, onClose, onCreate }) {
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'advise',
    priority: 'normal',
    requireApproval: false,
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const success = await onCreate({
      title: form.title,
      description: form.description,
      category: form.category,
      priority: form.priority,
      require_approval: form.requireApproval,
    });
    setLoading(false);
    if (success) {
      setForm({
        title: '',
        description: '',
        category: 'advise',
        priority: 'normal',
        requireApproval: false,
      });
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="card w-full max-w-lg mx-4">
        <h2 className="text-xl font-bold text-white mb-4">Create New Task</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-surface-400 mb-2">Title</label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
              className="input"
              placeholder="Task title..."
              required
            />
          </div>
          <div>
            <label className="block text-sm text-surface-400 mb-2">Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
              className="textarea h-24"
              placeholder="What should this task accomplish?"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-surface-400 mb-2">Category</label>
              <select
                value={form.category}
                onChange={(e) => setForm((prev) => ({ ...prev, category: e.target.value }))}
                className="input"
              >
                <option value="research">Research</option>
                <option value="code">Code</option>
                <option value="debug">Debug</option>
                <option value="optimize">Optimize</option>
                <option value="advise">Advise</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-surface-400 mb-2">Priority</label>
              <select
                value={form.priority}
                onChange={(e) => setForm((prev) => ({ ...prev, priority: e.target.value }))}
                className="input"
              >
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm text-surface-300">
            <input
              type="checkbox"
              checked={form.requireApproval}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, requireApproval: e.target.checked }))
              }
              className="rounded border-surface-600 bg-surface-700 text-primary-500"
            />
            Require approval before execution
          </label>
          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !form.title.trim()}
              className="btn btn-primary flex-1 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Create Task
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Tasks() {
  const { tasks, loading, fetchTasks, createTask, cancelTask } = useStore();
  const [modalOpen, setModalOpen] = useState(false);
  const [filter, setFilter] = useState('all');
  const [filterOpen, setFilterOpen] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'all') return true;
    return task.status === filter;
  });

  const taskCounts = tasks.reduce((acc, task) => {
    acc[task.status] = (acc[task.status] || 0) + 1;
    return acc;
  }, {});

  const filterOptions = [
    { value: 'all', label: 'All Tasks', count: tasks.length },
    { value: 'pending', label: 'Pending', count: taskCounts.pending || 0 },
    { value: 'in_progress', label: 'In Progress', count: taskCounts.in_progress || 0 },
    { value: 'awaiting_approval', label: 'Awaiting Approval', count: taskCounts.awaiting_approval || 0 },
    { value: 'completed', label: 'Completed', count: taskCounts.completed || 0 },
    { value: 'failed', label: 'Failed', count: taskCounts.failed || 0 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Tasks</h1>
          <p className="text-surface-400 mt-1">Manage and monitor AI tasks</p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Task
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {filterOptions.map(({ value, label, count }) => (
          <button
            key={value}
            onClick={() => setFilter(value)}
            className={`stat-card text-center transition-colors ${
              filter === value ? 'ring-2 ring-primary-500' : ''
            }`}
          >
            <p className="stat-value">{count}</p>
            <p className="stat-label">{label}</p>
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {loading.tasks ? (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-500 mx-auto" />
            <p className="text-surface-400 mt-2">Loading tasks...</p>
          </div>
        ) : filteredTasks.length > 0 ? (
          filteredTasks.map((task) => (
            <TaskCard key={task.id} task={task} onCancel={cancelTask} />
          ))
        ) : (
          <div className="text-center py-12">
            <ListTodo className="w-12 h-12 mx-auto text-surface-600 mb-4" />
            <p className="text-surface-400">No tasks found</p>
            <button
              onClick={() => setModalOpen(true)}
              className="btn btn-secondary mt-4"
            >
              Create your first task
            </button>
          </div>
        )}
      </div>

      <CreateTaskModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreate={createTask}
      />
    </div>
  );
}

export default Tasks;
