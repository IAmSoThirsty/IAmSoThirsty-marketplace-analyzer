import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Image endpoints
export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_URL}/images/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getImages = async () => {
  const response = await api.get('/images/');
  return response.data;
};

export const getImage = async (imageId) => {
  const response = await api.get(`/images/${imageId}`);
  return response.data;
};

export const getImageDownloadUrl = async (imageId) => {
  const response = await api.get(`/images/${imageId}/download-url`);
  return response.data;
};

// Analysis endpoints
export const startAnalysis = async (imageId) => {
  const response = await api.post('/analysis/', { image_id: imageId });
  return response.data;
};

export const getAnalysisJob = async (jobId) => {
  const response = await api.get(`/analysis/jobs/${jobId}`);
  return response.data;
};

export const getImageAnalyses = async (imageId) => {
  const response = await api.get(`/analysis/image/${imageId}`);
  return response.data;
};

export const getAnalysis = async (analysisId) => {
  const response = await api.get(`/analysis/${analysisId}`);
  return response.data;
};

// Marketplace endpoints
export const startMarketplaceSearch = async (analysisId, providers = null) => {
  const response = await api.post('/marketplace/search', {
    analysis_id: analysisId,
    providers: providers,
  });
  return response.data;
};

export const getMarketplaceJob = async (jobId) => {
  const response = await api.get(`/marketplace/jobs/${jobId}`);
  return response.data;
};

export const getMarketplaceItems = async (analysisId) => {
  const response = await api.get(`/marketplace/analysis/${analysisId}`);
  return response.data;
};

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
