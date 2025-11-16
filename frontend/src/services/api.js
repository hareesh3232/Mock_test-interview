import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message || 
                        error.message || 
                        'An unexpected error occurred';
    
    // Handle specific error codes
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    }
    
    return Promise.reject(new Error(errorMessage));
  }
);

// API endpoints
export const apiEndpoints = {
  // Health check
  health: () => api.get('/'),
  
  // Resume endpoints
  uploadResume: (formData) => {
    return api.post('/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getResume: (resumeId) => api.get(`/resume/${resumeId}`),
  
  // Job endpoints
  searchJobs: (params) => {
    const { skills, location = 'us', count = 10 } = params;
    return api.get('/jobs/search', {
      params: {
        skills: Array.isArray(skills) ? skills.join(',') : skills,
        location,
        count,
      },
    });
  },
  
  getJob: (jobId) => api.get(`/jobs/${jobId}`),
  
  // Interview endpoints
  generateQuestions: (data) => api.post('/interview/generate', data),
  
  startInterview: (data) => api.post('/interview/start', data),
  
  submitAnswer: (data) => api.post('/interview/submit', data),
  
  getInterview: (interviewId) => api.get(`/interview/${interviewId}`),
  
  getResults: (interviewId) => api.get(`/interview/${interviewId}/results`),
  
  // Analytics endpoints
  getUserStats: (userId) => api.get(`/analytics/user/${userId}`),
  
  getInterviewHistory: (userId) => api.get(`/analytics/history/${userId}`),
};

// Convenience functions
export const uploadResume = (formData) => apiEndpoints.uploadResume(formData);

export const searchJobs = (skills, location = 'us', count = 10) => 
  apiEndpoints.searchJobs({ skills, location, count });

export const generateInterviewQuestions = (resumeId, jobId, questionCount = 5) =>
  apiEndpoints.generateQuestions({
    resume_id: resumeId,
    job_id: jobId,
    question_count: questionCount,
  });

export const startInterview = (resumeId, jobId, questions) =>
  apiEndpoints.startInterview({
    resume_id: resumeId,
    job_id: jobId,
    questions,
  });

export const submitInterviewAnswer = (interviewId, questionIndex, answer) =>
  apiEndpoints.submitAnswer({
    interview_id: interviewId,
    question_index: questionIndex,
    answer,
  });

// Utility functions
export const handleApiError = (error) => {
  console.error('API Error:', error);
  
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const message = error.response.data?.detail || error.response.data?.message || 'Server error';
    
    switch (status) {
      case 400:
        return `Bad Request: ${message}`;
      case 401:
        return 'Authentication required. Please log in.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 422:
        return `Validation Error: ${message}`;
      case 500:
        return 'Internal server error. Please try again later.';
      default:
        return message;
    }
  } else if (error.request) {
    // Network error
    return 'Network error. Please check your connection and try again.';
  } else {
    // Other error
    return error.message || 'An unexpected error occurred.';
  }
};

// Check if API is available
export const checkApiHealth = async () => {
  try {
    await apiEndpoints.health();
    return true;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
};

export default api;