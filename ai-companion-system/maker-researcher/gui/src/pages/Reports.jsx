import { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  Activity,
  Calendar,
  Download,
  RefreshCw,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend,
  AreaChart,
  Area,
} from 'recharts';
import { statusApi } from '../services/api';
import useStore from '../store/useStore';

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function Reports() {
  const { tasks, metrics, systemMetrics, status, fetchMetrics } = useStore();
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState('week');

  const tasksByCategory = tasks.reduce((acc, task) => {
    acc[task.category] = (acc[task.category] || 0) + 1;
    return acc;
  }, {});

  const categoryData = Object.entries(tasksByCategory).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }));

  const tasksByStatus = tasks.reduce((acc, task) => {
    acc[task.status] = (acc[task.status] || 0) + 1;
    return acc;
  }, {});

  const statusData = Object.entries(tasksByStatus).map(([name, value]) => ({
    name: name.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
    value,
  }));

  const completedTasks = tasks.filter((t) => t.status === 'completed');
  const failedTasks = tasks.filter((t) => t.status === 'failed');
  const successRate = tasks.length > 0
    ? ((completedTasks.length / tasks.length) * 100).toFixed(1)
    : 0;

  const mockTimelineData = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    return {
      date: date.toLocaleDateString('en-US', { weekday: 'short' }),
      tasks: Math.floor(Math.random() * 10) + 1,
      completed: Math.floor(Math.random() * 8) + 1,
    };
  });

  const mockPerformanceData = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}:00`,
    responseTime: Math.random() * 3 + 1,
    requests: Math.floor(Math.random() * 20) + 5,
  }));

  const handleExport = () => {
    const report = {
      generated_at: new Date().toISOString(),
      summary: {
        total_tasks: tasks.length,
        completed: completedTasks.length,
        failed: failedTasks.length,
        success_rate: successRate,
      },
      tasks_by_category: tasksByCategory,
      tasks_by_status: tasksByStatus,
      system_metrics: systemMetrics,
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `researcher-report-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Reports & Analytics</h1>
          <p className="text-surface-400 mt-1">
            Detailed insights into system performance and task execution
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchMetrics()}
            className="btn btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={handleExport}
            className="btn btn-primary flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export Report
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Total Tasks</p>
              <p className="stat-value">{tasks.length}</p>
            </div>
            <BarChart3 className="w-8 h-8 text-primary-500" />
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Completed</p>
              <p className="stat-value text-emerald-400">{completedTasks.length}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-emerald-500" />
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Failed</p>
              <p className="stat-value text-red-400">{failedTasks.length}</p>
            </div>
            <XCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Success Rate</p>
              <p className="stat-value text-primary-400">{successRate}%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-primary-500" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="card-header">Tasks by Category</h3>
          <div className="h-64">
            {categoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {categoryData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-surface-500">
                No data available
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="card-header">Tasks by Status</h3>
          <div className="h-64">
            {statusData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={statusData} layout="vertical">
                  <XAxis type="number" stroke="#64748b" />
                  <YAxis type="category" dataKey="name" stroke="#64748b" width={100} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="value" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-surface-500">
                No data available
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="card-header">Task Activity Timeline</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={mockTimelineData}>
              <defs>
                <linearGradient id="colorTasks" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorCompleted" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="tasks"
                stroke="#0ea5e9"
                fill="url(#colorTasks)"
                name="Created"
              />
              <Area
                type="monotone"
                dataKey="completed"
                stroke="#10b981"
                fill="url(#colorCompleted)"
                name="Completed"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="card-header">Response Time (24h)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockPerformanceData}>
                <XAxis dataKey="hour" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="responseTime"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  dot={false}
                  name="Response Time (s)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="card-header">Request Volume (24h)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockPerformanceData}>
                <XAxis dataKey="hour" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="requests" fill="#8b5cf6" name="Requests" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="card-header">System Health Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-surface-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-primary-500" />
              <span className="text-sm text-surface-400">CPU Usage</span>
            </div>
            <p className="text-2xl font-bold text-white">
              {systemMetrics?.cpu_percent?.toFixed(1) || 0}%
            </p>
            <div className="mt-2 h-2 bg-surface-600 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500"
                style={{ width: `${systemMetrics?.cpu_percent || 0}%` }}
              />
            </div>
          </div>
          <div className="p-4 bg-surface-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-emerald-500" />
              <span className="text-sm text-surface-400">Memory</span>
            </div>
            <p className="text-2xl font-bold text-white">
              {systemMetrics?.memory_percent?.toFixed(1) || 0}%
            </p>
            <div className="mt-2 h-2 bg-surface-600 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500"
                style={{ width: `${systemMetrics?.memory_percent || 0}%` }}
              />
            </div>
          </div>
          <div className="p-4 bg-surface-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-amber-500" />
              <span className="text-sm text-surface-400">GPU</span>
            </div>
            <p className="text-2xl font-bold text-white">
              {systemMetrics?.gpu_percent?.toFixed(1) || 'N/A'}%
            </p>
            <div className="mt-2 h-2 bg-surface-600 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500"
                style={{ width: `${systemMetrics?.gpu_percent || 0}%` }}
              />
            </div>
          </div>
          <div className="p-4 bg-surface-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-red-500" />
              <span className="text-sm text-surface-400">Disk</span>
            </div>
            <p className="text-2xl font-bold text-white">
              {systemMetrics?.disk_percent?.toFixed(1) || 0}%
            </p>
            <div className="mt-2 h-2 bg-surface-600 rounded-full overflow-hidden">
              <div
                className="h-full bg-red-500"
                style={{ width: `${systemMetrics?.disk_percent || 0}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Reports;
