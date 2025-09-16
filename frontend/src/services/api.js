// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

// API Service Class
class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add Authorization header if token exists
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Authentication APIs
  async signup(userData) {
    return this.request('/accounts/signup/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(credentials) {
    return this.request('/accounts/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async getProfile() {
    return this.request('/accounts/profile/', {
      method: 'GET',
    });
  }

  async updateProfile(userId, profileData) {
    return this.request(`/accounts/update-profile/${userId}/`, {
      method: 'POST',
      body: JSON.stringify(profileData),
    });
  }

  async changePassword(passwordData) {
    return this.request('/accounts/change-password/', {
      method: 'POST',
      body: JSON.stringify(passwordData),
    });
  }

  // Categories APIs
  async getCategories() {
    return this.request('/api/products/category/', {
      method: 'GET',
    });
  }

  async getCategory(slug) {
    return this.request(`/api/products/category/${slug}/`, {
      method: 'GET',
    });
  }

  async getSubCategories() {
    return this.request('/api/products/subcategory/', {
      method: 'GET',
    });
  }

  async getSubCategory(slug) {
    return this.request(`/api/products/subcategory/${slug}/`, {
      method: 'GET',
    });
  }

  async getSubCategoriesByCategory(categorySlug) {
    return this.request(`/api/products/category/${categorySlug}/subcategories/`, {
      method: 'GET',
    });
  }

  // Products APIs
  async getProducts() {
    return this.request('/api/products/product/', {
      method: 'GET',
    });
  }

  async getProduct(slug) {
    return this.request(`/api/products/product/${slug}/`, {
      method: 'GET',
    });
  }

  // Token management
  setTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  getAccessToken() {
    return localStorage.getItem('access_token');
  }

  getRefreshToken() {
    return localStorage.getItem('refresh_token');
  }

  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  isAuthenticated() {
    return !!this.getAccessToken();
  }
}

// Create and export a singleton instance
const apiService = new ApiService();
export default apiService;
