import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Claims API
export const claimsAPI = {
  ingest: (data) => api.post('/api/ingest', data),
  getClaims: (params) => api.get('/api/claims', { params }),
  getClaimById: (id) => api.get(`/api/claims/${id}`),
  getStats: () => api.get('/api/stats'),
};

// Verification API
export const verificationAPI = {
  verifyClaim: (claimId, forceReverify = false) => 
    api.post(`/api/verify/${claimId}`, { force_reverify: forceReverify }),
  reviewVerdict: (verdictId, data) => api.post(`/api/review/${verdictId}`, data),
};

// Clusters API
export const clustersAPI = {
  getClusters: (limit = 10) => api.get('/api/clusters', { params: { limit } }),
  refreshClusters: (hours = 24) => api.post('/api/clusters/refresh', null, { params: { hours } }),
  getClusterById: (clusterId) => api.get(`/api/clusters/${clusterId}`),
};

// Feedback API
export const feedbackAPI = {
  submitFeedback: (data) => api.post('/api/feedback', data),
  getFeedbackByClaim: (claimId) => api.get(`/api/feedback/${claimId}`),
};

// Alerts API
export const alertsAPI = {
  getAlerts: (params) => api.get('/api/alerts', { params }),
  resolveAlert: (alertId) => api.post(`/api/alerts/${alertId}/resolve`),
  subscribe: (email, severityThreshold) => 
    api.post('/api/alerts/subscribe', { email, severity_threshold: severityThreshold }),
};

export default api;
