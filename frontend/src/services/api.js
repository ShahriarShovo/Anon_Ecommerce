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
      credentials: 'include', // Include cookies for session management
      ...options,
    };

    // Add Authorization header if token exists
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    try {
      console.log('🌐 API: Making request to:', url, 'with config:', config);
      console.log('🌐 API: Cookies being sent:', document.cookie);
      const response = await fetch(url, config);
      const data = await response.json();
      console.log('🌐 API: Response status:', response.status, 'Data:', data);
      console.log('🌐 API: Response cookies:', response.headers.get('Set-Cookie'));

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('🌐 API: Request failed:', error);
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

  // Homepage Products API
  async getHomepageProducts() {
    return this.request('/api/products/homepage/', {
      method: 'GET',
    });
  }

  // Single Product API
  async getSingleProduct(slug) {
    return this.request(`/api/products/product-detail/${slug}/`, {
      method: 'GET',
    });
  }

  // Product Reviews API
  async getProductReviews(slug) {
    return this.request(`/api/products/product-reviews/${slug}/`, {
      method: 'GET',
    });
  }

  async createProductReview(slug, reviewData) {
    return this.request(`/api/products/product-reviews/${slug}/create/`, {
      method: 'POST',
      body: JSON.stringify(reviewData),
    });
  }

  // Cart APIs
  async addToCart(productId, quantity = 1, variantId = null) {
    return this.request('/api/cart/add/', {
      method: 'POST',
      body: JSON.stringify({
        product_id: productId,
        quantity: quantity,
        variant_id: variantId
      }),
    });
  }

  async getCart() {
    return this.request('/api/cart/', {
      method: 'GET',
    });
  }

  async increaseCartItemQuantity(itemId) {
    return this.request(`/api/cart/items/${itemId}/increase/`, {
      method: 'POST',
    });
  }

  async decreaseCartItemQuantity(itemId) {
    return this.request(`/api/cart/items/${itemId}/decrease/`, {
      method: 'POST',
    });
  }

  async removeCartItem(itemId) {
    console.log('🌐 API: Removing cart item with ID:', itemId);
    return this.request(`/api/cart/items/${itemId}/remove/`, {
      method: 'DELETE',
    });
  }

  async clearCart() {
    return this.request('/api/cart/clear/', {
      method: 'DELETE',
    });
  }

  // Order APIs
  async placeOrder(orderData) {
    return this.request('/api/orders/create/', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  }

  async getOrders() {
    return this.request('/api/orders/', {
      method: 'GET',
    });
  }

  async getOrder(orderId) {
    return this.request(`/api/orders/${orderId}/`, {
      method: 'GET',
    });
  }

  // Invoice APIs
  async generateInvoice(orderId) {
    return this.request(`/api/invoice/generate/${orderId}/`, {
      method: 'GET',
    });
  }

  async getInvoices() {
    return this.request('/api/invoice/', {
      method: 'GET',
    });
  }

  async getInvoice(invoiceId) {
    return this.request(`/api/invoice/${invoiceId}/`, {
      method: 'GET',
    });
  }

  // Wishlist APIs
  async addToWishlist(productId, variantId = null) {
    return this.request('/api/wishlist/add/', {
      method: 'POST',
      body: JSON.stringify({
        product_id: productId,
        variant_id: variantId
      }),
    });
  }

  async getWishlist() {
    return this.request('/api/wishlist/', {
      method: 'GET',
    });
  }

  async removeFromWishlist(itemId) {
    return this.request(`/api/wishlist/items/${itemId}/remove/`, {
      method: 'DELETE',
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
