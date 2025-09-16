import React, { useState, useCallback, useMemo, memo } from 'react'
import { useAuth } from '../../contexts/AuthContext'

const LoginModal = memo(({ isOpen, onClose }) => {
  const { signup, login, isLoading } = useAuth()
  const [isSignUp, setIsSignUp] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirm_password: ''
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleInputChange = useCallback((e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }, [])

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    try {
      if (isSignUp) {
        // Sign up logic
        const result = await signup(formData)
        if (result.success) {
          setSuccess(`${result.message} Your username is: ${result.user?.username || 'Generated'}`)
          // Reset form
          setFormData({
            full_name: '',
            email: '',
            password: '',
            confirm_password: ''
          })
          // Close modal after successful signup
          setTimeout(() => {
            onClose()
          }, 3000)
        } else {
          setError(result.message)
        }
      } else {
        // Login logic
        const loginData = {
          email: formData.email,
          password: formData.password
        }
        const result = await login(loginData)
        if (result.success) {
          setSuccess(result.message)
          
          // Redirect based on user type
          if (result.is_admin) {
            // Admin login - redirect to admin dashboard
            setTimeout(() => {
              onClose()
              window.location.replace('/admin-dashboard')
            }, 1000)
          } else {
            // Customer login - stay on home page
            setTimeout(() => {
              onClose()
            }, 1000)
          }
        } else {
          setError(result.message)
        }
      }
    } catch (error) {
      setError('An unexpected error occurred. Please try again.')
    }
  }, [formData, isSignUp, signup, login, onClose])

  const toggleSignUp = useCallback(() => {
    setIsSignUp(prev => !prev)
  }, [])

  if (!isOpen) return null

  return (
    <div className="modal" data-modal>
      <div className="modal-close-overlay" data-modal-overlay onClick={onClose}></div>
      <div className="modal-content">
        <button className="modal-close-btn" data-modal-close onClick={onClose}>
          <ion-icon name="close-outline"></ion-icon>
        </button>

        <div className="auth-container">
          <div className="auth-header">
            <h2 className="auth-title">
              {isSignUp ? 'Create Account' : 'Welcome Back'}
            </h2>
            <p className="auth-subtitle">
              {isSignUp 
                ? 'Sign up to get started with Anon' 
                : 'Sign in to your account to continue'
              }
            </p>
          </div>

          {/* Error and Success Messages */}
          {error && (
            <div className="auth-message error">
              <ion-icon name="alert-circle-outline"></ion-icon>
              {error}
            </div>
          )}
          
          {success && (
            <div className="auth-message success">
              <ion-icon name="checkmark-circle-outline"></ion-icon>
              {success}
            </div>
          )}

          <form className="auth-form" onSubmit={handleSubmit}>
            {isSignUp && (
              <div className="input-group">
                <label htmlFor="full_name">Full Name</label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  placeholder="Enter your full name"
                  required
                />
              </div>
            )}

            <div className="input-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter your email"
                required
              />
            </div>

            <div className="input-group">
              <label htmlFor="password">Password</label>
              <div className="password-input-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  <ion-icon name={showPassword ? "eye-off-outline" : "eye-outline"}></ion-icon>
                </button>
              </div>
            </div>

            {isSignUp && (
              <div className="input-group">
                <label htmlFor="confirm_password">Confirm Password</label>
                <div className="password-input-wrapper">
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    id="confirm_password"
                    name="confirm_password"
                    value={formData.confirm_password}
                    onChange={handleInputChange}
                    placeholder="Confirm your password"
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    <ion-icon name={showConfirmPassword ? "eye-off-outline" : "eye-outline"}></ion-icon>
                  </button>
                </div>
              </div>
            )}

            {!isSignUp && (
              <div className="forgot-password">
                <a href="#" className="forgot-link">Forgot Password?</a>
              </div>
            )}

            <button type="submit" className="auth-btn" disabled={isLoading}>
              {isLoading ? (
                <>
                  <ion-icon name="hourglass-outline"></ion-icon>
                  {isSignUp ? 'Creating Account...' : 'Signing In...'}
                </>
              ) : (
                isSignUp ? 'Create Account' : 'Sign In'
              )}
            </button>

            <div className="auth-divider">
              <span>or</span>
            </div>

            <button type="button" className="social-auth-btn">
              <ion-icon name="logo-google"></ion-icon>
              Continue with Google
            </button>

            <button type="button" className="social-auth-btn">
              <ion-icon name="logo-facebook"></ion-icon>
              Continue with Facebook
            </button>
          </form>

          <div className="auth-footer">
            <p>
              {isSignUp ? 'Already have an account?' : "Don't have an account?"}
              <button 
                type="button" 
                className="auth-toggle"
                onClick={toggleSignUp}
              >
                {isSignUp ? 'Sign In' : 'Sign Up'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
})

export default LoginModal
