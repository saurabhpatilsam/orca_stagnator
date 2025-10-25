// API configuration for backend authentication
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://orca-backend-api-production.up.railway.app';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('orca-auth-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  async post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();

// Authentication API functions
export const authAPI = {
  async signUp(email, password) {
    const response = await apiClient.post('/auth/signup', { email, password });
    if (response.access_token) {
      localStorage.setItem('orca-auth-token', response.access_token);
      localStorage.setItem('orca-user', JSON.stringify(response.user));
    }
    return response;
  },

  async signIn(email, password) {
    const response = await apiClient.post('/auth/signin', { email, password });
    if (response.access_token) {
      localStorage.setItem('orca-auth-token', response.access_token);
      localStorage.setItem('orca-user', JSON.stringify(response.user));
    }
    return response;
  },

  signOut() {
    localStorage.removeItem('orca-auth-token');
    localStorage.removeItem('orca-user');
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('orca-user');
    return userStr ? JSON.parse(userStr) : null;
  },

  getToken() {
    return localStorage.getItem('orca-auth-token');
  },

  isAuthenticated() {
    return !!this.getToken();
  }
};

export default apiClient;
