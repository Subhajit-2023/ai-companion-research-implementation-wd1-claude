import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const charactersAPI = {
  list: async (userId = 1) => {
    const response = await api.get(`/api/characters?user_id=${userId}`);
    return response.data;
  },

  get: async (characterId) => {
    const response = await api.get(`/api/characters/${characterId}`);
    return response.data;
  },

  create: async (characterData) => {
    const response = await api.post('/api/characters', characterData);
    return response.data;
  },

  update: async (characterId, characterData) => {
    const response = await api.put(`/api/characters/${characterId}`, characterData);
    return response.data;
  },

  delete: async (characterId) => {
    const response = await api.delete(`/api/characters/${characterId}`);
    return response.data;
  },

  createFromTemplate: async (templateName, userId = 1) => {
    const response = await api.post(`/api/characters/from-template?template_name=${templateName}&user_id=${userId}`);
    return response.data;
  },

  listTemplates: async () => {
    const response = await api.get('/api/characters/templates/list');
    return response.data;
  },

  generateAvatar: async (characterId, style = 'realistic') => {
    const response = await api.post(`/api/characters/${characterId}/avatar?style=${style}`);
    return response.data;
  },
};

export const chatAPI = {
  sendMessage: async (characterId, message, userId = 1, stream = false) => {
    if (!stream) {
      const response = await api.post('/api/chat/send', {
        character_id: characterId,
        message,
        user_id: userId,
        stream: false,
        include_memory: true,
      });
      return response.data;
    }
    return null;
  },

  getHistory: async (characterId, limit = 50) => {
    const response = await api.get(`/api/chat/history/${characterId}?limit=${limit}`);
    return response.data;
  },

  clearHistory: async (characterId) => {
    const response = await api.delete(`/api/chat/history/${characterId}`);
    return response.data;
  },
};

export const imagesAPI = {
  generate: async (imageData) => {
    const response = await api.post('/api/images/generate', imageData);
    return response.data;
  },

  generateCharacter: async (characterId, situation = 'portrait', style = 'realistic', userId = 1) => {
    const response = await api.post('/api/images/generate-character', {
      character_id: characterId,
      situation,
      style,
      user_id: userId,
    });
    return response.data;
  },

  getGallery: async (characterId = null, userId = 1, limit = 20) => {
    let url = `/api/images/gallery?user_id=${userId}&limit=${limit}`;
    if (characterId) {
      url += `&character_id=${characterId}`;
    }
    const response = await api.get(url);
    return response.data;
  },

  delete: async (imageId) => {
    const response = await api.delete(`/api/images/${imageId}`);
    return response.data;
  },

  checkStatus: async () => {
    const response = await api.get('/api/images/status/check');
    return response.data;
  },
};

export const memoryAPI = {
  add: async (characterId, content, memoryType = 'episodic', importance = 1.0) => {
    const response = await api.post('/api/memory/add', {
      character_id: characterId,
      content,
      memory_type: memoryType,
      importance,
    });
    return response.data;
  },

  search: async (characterId, query, limit = null) => {
    const response = await api.post('/api/memory/search', {
      character_id: characterId,
      query,
      limit,
    });
    return response.data;
  },

  getRecent: async (characterId, limit = 10) => {
    const response = await api.get(`/api/memory/recent/${characterId}?limit=${limit}`);
    return response.data;
  },

  getStats: async (characterId) => {
    const response = await api.get(`/api/memory/stats/${characterId}`);
    return response.data;
  },

  clear: async (characterId) => {
    const response = await api.delete(`/api/memory/${characterId}`);
    return response.data;
  },
};

export const searchAPI = {
  search: async (query, maxResults = 5) => {
    const response = await api.post('/api/search/', {
      query,
      max_results: maxResults,
    });
    return response.data;
  },

  searchNews: async (query, maxResults = 5) => {
    const response = await api.post('/api/search/news', {
      query,
      max_results: maxResults,
    });
    return response.data;
  },

  getQuickAnswer: async (query) => {
    const response = await api.get(`/api/search/quick-answer?query=${encodeURIComponent(query)}`);
    return response.data;
  },

  getCurrentInfo: async (topic) => {
    const response = await api.get(`/api/search/current-info?topic=${encodeURIComponent(topic)}`);
    return response.data;
  },
};

export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
