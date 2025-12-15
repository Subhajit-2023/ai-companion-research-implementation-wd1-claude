import { create } from 'zustand';
import { statusApi, researchApi, taskApi, approvalApi, documentApi, optimizeApi } from '../services/api';

const useStore = create((set, get) => ({
  status: null,
  health: null,
  metrics: null,
  systemMetrics: null,
  tasks: [],
  approvals: [],
  documents: [],
  researchSessions: [],
  optimizations: null,
  loading: {},
  errors: {},

  setLoading: (key, value) =>
    set((state) => ({ loading: { ...state.loading, [key]: value } })),

  setError: (key, error) =>
    set((state) => ({ errors: { ...state.errors, [key]: error } })),

  clearError: (key) =>
    set((state) => {
      const newErrors = { ...state.errors };
      delete newErrors[key];
      return { errors: newErrors };
    }),

  fetchStatus: async () => {
    const { setLoading, setError } = get();
    setLoading('status', true);
    try {
      const [statusRes, healthRes] = await Promise.all([
        statusApi.getStatus(),
        statusApi.getHealth(),
      ]);
      set({ status: statusRes.data, health: healthRes.data });
    } catch (error) {
      setError('status', error.message);
    } finally {
      setLoading('status', false);
    }
  },

  fetchMetrics: async () => {
    const { setLoading, setError } = get();
    setLoading('metrics', true);
    try {
      const [metricsRes, sysMetricsRes] = await Promise.all([
        statusApi.getMetrics(),
        statusApi.getSystemMetrics(),
      ]);
      set({ metrics: metricsRes.data, systemMetrics: sysMetricsRes.data });
    } catch (error) {
      setError('metrics', error.message);
    } finally {
      setLoading('metrics', false);
    }
  },

  fetchTasks: async (status = null) => {
    const { setLoading, setError } = get();
    setLoading('tasks', true);
    try {
      const res = await taskApi.list(status);
      set({ tasks: res.data.tasks });
    } catch (error) {
      setError('tasks', error.message);
    } finally {
      setLoading('tasks', false);
    }
  },

  createTask: async (task) => {
    const { setLoading, setError, fetchTasks } = get();
    setLoading('createTask', true);
    try {
      await taskApi.create(task);
      await fetchTasks();
      return true;
    } catch (error) {
      setError('createTask', error.message);
      return false;
    } finally {
      setLoading('createTask', false);
    }
  },

  cancelTask: async (taskId) => {
    const { fetchTasks } = get();
    try {
      await taskApi.cancel(taskId);
      await fetchTasks();
      return true;
    } catch {
      return false;
    }
  },

  fetchApprovals: async () => {
    const { setLoading, setError } = get();
    setLoading('approvals', true);
    try {
      const res = await approvalApi.list();
      set({ approvals: res.data.pending });
    } catch (error) {
      setError('approvals', error.message);
    } finally {
      setLoading('approvals', false);
    }
  },

  processApproval: async (requestId, approve, notes = '') => {
    const { fetchApprovals, fetchTasks } = get();
    try {
      await approvalApi.process(requestId, approve, notes);
      await fetchApprovals();
      await fetchTasks();
      return true;
    } catch {
      return false;
    }
  },

  fetchDocuments: async () => {
    const { setLoading, setError } = get();
    setLoading('documents', true);
    try {
      const res = await documentApi.list();
      set({ documents: res.data.documents });
    } catch (error) {
      setError('documents', error.message);
    } finally {
      setLoading('documents', false);
    }
  },

  addDocument: async (filePath) => {
    const { fetchDocuments } = get();
    try {
      await documentApi.add(filePath);
      await fetchDocuments();
      return true;
    } catch {
      return false;
    }
  },

  deleteDocument: async (docId) => {
    const { fetchDocuments } = get();
    try {
      await documentApi.delete(docId);
      await fetchDocuments();
      return true;
    } catch {
      return false;
    }
  },

  fetchOptimizations: async () => {
    const { setLoading, setError } = get();
    setLoading('optimizations', true);
    try {
      const res = await optimizeApi.getOptimizations();
      set({ optimizations: res.data });
    } catch (error) {
      setError('optimizations', error.message);
    } finally {
      setLoading('optimizations', false);
    }
  },

  addResearchSession: (session) =>
    set((state) => ({
      researchSessions: [session, ...state.researchSessions].slice(0, 20),
    })),

  refreshAll: async () => {
    const { fetchStatus, fetchMetrics, fetchTasks, fetchApprovals, fetchDocuments } = get();
    await Promise.all([
      fetchStatus(),
      fetchMetrics(),
      fetchTasks(),
      fetchApprovals(),
      fetchDocuments(),
    ]);
  },
}));

export default useStore;
