import React, { createContext, useContext, useState, useEffect } from 'react';
import apiService from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userType, setUserType] = useState(null); // 'admin' or 'customer'

  // Check if user is authenticated on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      if (apiService.isAuthenticated()) {
        const userData = await apiService.getProfile();
        setUser(userData);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      apiService.clearTokens();
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (userData) => {
    try {
      setIsLoading(true);
      const response = await apiService.signup(userData);
      
      // Store tokens
      apiService.setTokens(response.token.access, response.token.refresh);
      
      // Get user profile
      const userProfile = await apiService.getProfile();
      setUser(userProfile);
      setIsAuthenticated(true);
      
      return { success: true, message: response.message, user: userProfile };
    } catch (error) {
      console.error('Signup failed:', error);
      return { success: false, message: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      setIsLoading(true);
      const response = await apiService.login(credentials);
      
      // Store tokens
      apiService.setTokens(response.token.access, response.token.refresh);
      
      // Get user profile
      const userProfile = await apiService.getProfile();
      setUser(userProfile);
      setIsAuthenticated(true);
      
      // Set user type based on response
      if (response.user_type) {
        setUserType(response.user_type);
      }
      
      return { 
        success: true, 
        message: response.message,
        user_type: response.user_type,
        is_admin: response.is_admin
      };
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, message: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    apiService.clearTokens();
    setUser(null);
    setIsAuthenticated(false);
    setUserType(null);
  };

  const updateProfile = async (userId, profileData) => {
    try {
      setIsLoading(true);
      const updatedProfile = await apiService.updateProfile(userId, profileData);
      setUser(updatedProfile);
      return { success: true, data: updatedProfile };
    } catch (error) {
      console.error('Profile update failed:', error);
      return { success: false, message: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const changePassword = async (passwordData) => {
    try {
      setIsLoading(true);
      const response = await apiService.changePassword(passwordData);
      return { success: true, message: response.message };
    } catch (error) {
      console.error('Password change failed:', error);
      return { success: false, message: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    userType,
    signup,
    login,
    logout,
    updateProfile,
    changePassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
