import { useEffect } from 'react';
import {
  Activity,
  Cpu,
  HardDrive,
  MemoryStick,
  Zap,
  ListTodo,
  CheckCircle,
  Clock,
  AlertTriangle,
  BookOpen,
  TrendingUp,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import useStore from '../store/useStore';

const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#6366f1', '#8b5cf6'];

function StatCard({ icon: Icon, label, value, subValue, trend, color = 'primary' }) {
  const colorClasses = {
    primary: 'text-primary-500',
    success: 'text-emerald-500',
    warning: 'text-amber-500',
    error: 'text-red-500',
  };

  return (
    <div className="stat-card">
      <div className="flex items-start justify-between">
        <div>
          <p className="stat-label">{label}</p>
          <p className="stat-value mt-1">{value}</p>
          {subValue && <p className="text-sm text-surface-400 mt-1">{subValue}</p>}
        </div>
        <Icon className={`w-8 h-8 ${colorClasses[color]}`} />
      </div>
      {trend && (
        <div className="flex items-center gap-1 mt-2">
          <TrendingUp className="w-4 h-4 text-emerald-500" />
          <span className="text-sm text-emerald-500">{trend}</span>
        </div>
      )}
    </div>
  );
}

function Dashboard() {
  const {
    status,
    health,
    systemMetrics,
    metrics,
    tasks,
    approvals,
    documents,
    loading,
    fetchStatus,
    fetchMetrics,
    fetchTasks,
    fetchApprovals,
    fetchDocuments,
  } = useStore();

  useEffect(() => {
    fetchStatus();
    fetchMetrics();
    fetchTasks();
    fetchApprovals();
    fetchDocuments();
  }, []);

  const tasksByStatus = tasks.reduce((acc, task) => {
    acc[task.status] = (acc[task.status] || 0) + 1;
    return acc;
  }, {});

  const taskPieData = Object.entries(tasksByStatus).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value,
  }));

  const mockUsageData = Array.from({ length: 12 }, (_, i) => ({
    time: `${i * 5}m`,
    cpu: Math.random() * 40 + 20,
    memory: Math.random() * 30 + 50,
    gpu: Math.random() * 50 + 30,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-surface-400 mt-1">System overview and real-time metrics</p>
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              health?.overall === 'healthy'
                ? 'bg-emerald-500'
                : health?.overall === 'degraded'
                ? 'bg-amber-500 animate-pulse'
                : 'bg-red-500 animate-pulse'
            }`}
          />
          <span className="text-sm text-surface-300 capitalize">
            System {health?.overall || 'checking...'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Cpu}
          label="CPU Usage"
          value={`${systemMetrics?.cpu_percent?.toFixed(1) || 0}%`}
          color={systemMetrics?.cpu_percent > 80 ? 'error' : 'primary'}
        />
        <StatCard
          icon={MemoryStick}
          label="Memory"
          value={`${systemMetrics?.memory_percent?.toFixed(1) || 0}%`}
          subValue={`${systemMetrics?.memory_used_gb?.toFixed(1) || 0}GB used`}
          color={systemMetrics?.memory_percent > 80 ? 'warning' : 'primary'}
        />
        <StatCard
          icon={Zap}
          label="GPU"
          value={systemMetrics?.gpu_percent ? `${systemMetrics.gpu_percent.toFixed(1)}%` : 'N/A'}
          subValue={
            systemMetrics?.gpu_memory_used_gb
              ? `${systemMetrics.gpu_memory_used_gb.toFixed(1)}GB VRAM`
              : null
          }
          color={systemMetrics?.gpu_percent > 90 ? 'warning' : 'success'}
        />
        <StatCard
          icon={HardDrive}
          label="Disk"
          value={`${systemMetrics?.disk_percent?.toFixed(1) || 0}%`}
          color={systemMetrics?.disk_percent > 90 ? 'error' : 'primary'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <StatCard
          icon={ListTodo}
          label="Total Tasks"
          value={tasks.length}
          subValue={`${tasksByStatus.in_progress || 0} running`}
        />
        <StatCard
          icon={CheckCircle}
          label="Pending Approvals"
          value={approvals.length}
          color={approvals.length > 0 ? 'warning' : 'success'}
        />
        <StatCard
          icon={BookOpen}
          label="Documents"
          value={documents.length}
          subValue="in knowledge base"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="card-header">Resource Usage</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockUsageData}>
                <defs>
                  <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorGpu" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="cpu"
                  stroke="#0ea5e9"
                  fill="url(#colorCpu)"
                  name="CPU"
                />
                <Area
                  type="monotone"
                  dataKey="memory"
                  stroke="#10b981"
                  fill="url(#colorMemory)"
                  name="Memory"
                />
                <Area
                  type="monotone"
                  dataKey="gpu"
                  stroke="#f59e0b"
                  fill="url(#colorGpu)"
                  name="GPU"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-primary-500" />
              <span className="text-sm text-surface-400">CPU</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-emerald-500" />
              <span className="text-sm text-surface-400">Memory</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-amber-500" />
              <span className="text-sm text-surface-400">GPU</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="card-header">Task Distribution</h3>
          <div className="h-64 flex items-center justify-center">
            {taskPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={taskPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {taskPieData.map((_, index) => (
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
              <div className="text-center text-surface-500">
                <ListTodo className="w-12 h-12 mx-auto mb-2" />
                <p>No tasks yet</p>
              </div>
            )}
          </div>
          {taskPieData.length > 0 && (
            <div className="flex flex-wrap items-center justify-center gap-4 mt-4">
              {taskPieData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-sm text-surface-400 capitalize">
                    {entry.name}: {entry.value}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {health?.issues?.length > 0 && (
        <div className="card border-amber-500/50">
          <h3 className="card-header flex items-center gap-2 text-amber-400">
            <AlertTriangle className="w-5 h-5" />
            System Alerts
          </h3>
          <ul className="space-y-2">
            {health.issues.map((issue, index) => (
              <li key={index} className="flex items-center gap-2 text-surface-300">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                {issue}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="card">
        <h3 className="card-header">Recent Activity</h3>
        <div className="space-y-3">
          {tasks.slice(0, 5).map((task) => (
            <div
              key={task.id}
              className="flex items-center justify-between py-3 border-b border-surface-700 last:border-0"
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-2 h-2 rounded-full ${
                    task.status === 'completed'
                      ? 'bg-emerald-500'
                      : task.status === 'in_progress'
                      ? 'bg-primary-500 animate-pulse'
                      : task.status === 'failed'
                      ? 'bg-red-500'
                      : 'bg-surface-500'
                  }`}
                />
                <div>
                  <p className="text-white">{task.title}</p>
                  <p className="text-sm text-surface-400">{task.category}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-surface-500" />
                <span className="text-sm text-surface-400">
                  {new Date(task.created_at).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
          {tasks.length === 0 && (
            <p className="text-center text-surface-500 py-8">No recent tasks</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
