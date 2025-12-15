import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const statusApi = {
  getStatus: () => api.get('/status'),
  getHealth: () => api.get('/health'),
  getMetrics: () => api.get('/metrics'),
  getSystemMetrics: () => api.get('/metrics/system'),
};

export const chatApi = {
  sendMessage: (message, context = null) =>
    api.post('/chat', { message, context }),
};

export const researchApi = {
  search: (query, options = {}) =>
    api.post('/research', {
      query,
      include_papers: options.includePapers ?? true,
      include_code: options.includeCode ?? true,
      include_news: options.includeNews ?? false,
    }),
  getSession: (sessionId) => api.get(`/research/${sessionId}`),
};

export const codeApi = {
  generate: (description, language = 'python', context = null, filePath = null) =>
    api.post('/code/generate', {
      description,
      language,
      context,
      file_path: filePath,
    }),
  analyze: (filePath) =>
    api.post('/code/analyze', null, { params: { file_path: filePath } }),
  analyzeProject: (projectPath = null) =>
    api.get('/code/project', { params: { project_path: projectPath } }),
};

export const debugApi = {
  analyze: (errorText, language = 'python', additionalContext = null) =>
    api.post('/debug', {
      error_text: errorText,
      language,
      additional_context: additionalContext,
    }),
};

export const taskApi = {
  list: (status = null) =>
    api.get('/tasks', { params: status ? { status } : {} }),
  get: (taskId) => api.get(`/tasks/${taskId}`),
  create: (task) => api.post('/tasks', task),
  cancel: (taskId) => api.delete(`/tasks/${taskId}`),
};

export const approvalApi = {
  list: () => api.get('/approvals'),
  get: (requestId) => api.get(`/approvals/${requestId}`),
  process: (requestId, approve, notes = '') =>
    api.post(`/approvals/${requestId}`, {
      request_id: requestId,
      approve,
      notes,
    }),
};

export const documentApi = {
  list: () => api.get('/documents'),
  add: (filePath) => api.post('/documents', { file_path: filePath }),
  delete: (docId) => api.delete(`/documents/${docId}`),
  search: (query, nResults = 5, documentIds = null) =>
    api.post('/knowledge/search', {
      query,
      n_results: nResults,
      document_ids: documentIds,
    }),
};

export const optimizeApi = {
  getOptimizations: () => api.get('/optimize'),
  analyze: (area = null) =>
    api.post('/optimize/analyze', null, { params: area ? { area } : {} }),
};

export default api;
