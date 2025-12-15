import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  Code,
  ListTodo,
  CheckCircle,
  BookOpen,
  Zap,
  BarChart3,
  Activity,
  AlertCircle,
} from 'lucide-react';
import useStore from '../store/useStore';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/research', icon: Search, label: 'Research' },
  { path: '/code', icon: Code, label: 'Code Tools' },
  { path: '/tasks', icon: ListTodo, label: 'Tasks' },
  { path: '/approvals', icon: CheckCircle, label: 'Approvals' },
  { path: '/knowledge', icon: BookOpen, label: 'Knowledge' },
  { path: '/optimize', icon: Zap, label: 'Optimize' },
  { path: '/reports', icon: BarChart3, label: 'Reports' },
];

function Layout({ children }) {
  const { health, approvals, status } = useStore();

  const healthStatus = health?.overall || 'unknown';
  const pendingApprovals = approvals?.length || 0;
  const isRunning = status?.running ?? false;

  return (
    <div className="flex min-h-screen bg-surface-900">
      <aside className="w-64 bg-surface-800 border-r border-surface-700 flex flex-col">
        <div className="p-6 border-b border-surface-700">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-6 h-6 text-primary-500" />
            Maker-Researcher
          </h1>
          <p className="text-sm text-surface-400 mt-1">AI Research Assistant</p>
        </div>

        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {navItems.map(({ path, icon: Icon, label }) => (
              <li key={path}>
                <NavLink
                  to={path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary-600 text-white'
                        : 'text-surface-300 hover:bg-surface-700 hover:text-white'
                    }`
                  }
                >
                  <Icon className="w-5 h-5" />
                  <span>{label}</span>
                  {label === 'Approvals' && pendingApprovals > 0 && (
                    <span className="ml-auto bg-amber-500 text-white text-xs px-2 py-0.5 rounded-full">
                      {pendingApprovals}
                    </span>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4 border-t border-surface-700">
          <div className="flex items-center gap-3 px-4 py-3 bg-surface-700/50 rounded-lg">
            <div
              className={`w-3 h-3 rounded-full ${
                healthStatus === 'healthy'
                  ? 'bg-emerald-500'
                  : healthStatus === 'degraded'
                  ? 'bg-amber-500'
                  : 'bg-red-500'
              }`}
            />
            <div className="flex-1">
              <p className="text-sm text-white capitalize">{healthStatus}</p>
              <p className="text-xs text-surface-400">
                {isRunning ? 'Running' : 'Stopped'}
              </p>
            </div>
            {health?.issues?.length > 0 && (
              <AlertCircle className="w-4 h-4 text-amber-500" />
            )}
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}

export default Layout;
