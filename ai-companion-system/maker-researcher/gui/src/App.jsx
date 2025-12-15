import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Research from './pages/Research';
import CodeTools from './pages/CodeTools';
import Tasks from './pages/Tasks';
import Approvals from './pages/Approvals';
import Knowledge from './pages/Knowledge';
import Optimize from './pages/Optimize';
import Reports from './pages/Reports';
import useStore from './store/useStore';

function App() {
  const refreshAll = useStore((state) => state.refreshAll);

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 30000);
    return () => clearInterval(interval);
  }, [refreshAll]);

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/research" element={<Research />} />
        <Route path="/code" element={<CodeTools />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/approvals" element={<Approvals />} />
        <Route path="/knowledge" element={<Knowledge />} />
        <Route path="/optimize" element={<Optimize />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
