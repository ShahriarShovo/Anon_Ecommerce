import React, { useState } from 'react'

const ForgotPassword = ({ isOpen, onClose }) => {
  const [email, setEmail] = useState('')
  const [isEmailSent, setIsEmailSent] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    // Handle forgot password logic here
    console.log('Password reset requested for:', email)
    setIsEmailSent(true)
  }

  const handleBackToLogin = () => {
    setIsEmailSent(false)
    setEmail('')
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="modal" data-modal>
      <div className="modal-close-overlay" data-modal-overlay onClick={onClose}></div>
      <div className="modal-content">
        <button className="modal-close-btn" data-modal-close onClick={onClose}>
          <ion-icon name="close-outline"></ion-icon>
        </button>

        <div className="auth-container">
          {!isEmailSent ? (
            <>
              <div className="auth-header">
                <h2 className="auth-title">Forgot Password?</h2>
                <p className="auth-subtitle">
                  Don't worry! Enter your email address and we'll send you a link to reset your password.
                </p>
              </div>

              <form className="auth-form" onSubmit={handleSubmit}>
                <div className="input-group">
                  <label htmlFor="email">Email Address</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email address"
                    required
                  />
                </div>

                <button type="submit" className="auth-btn">
                  Send Reset Link
                </button>
              </form>

              <div className="auth-footer">
                <p>
                  Remember your password?
                  <button 
                    type="button" 
                    className="auth-toggle"
                    onClick={handleBackToLogin}
                  >
                    Sign In
                  </button>
                </p>
              </div>
            </>
          ) : (
            <>
              <div className="auth-header">
                <div className="success-icon">
                  <ion-icon name="checkmark-circle-outline"></ion-icon>
                </div>
                <h2 className="auth-title">Check Your Email</h2>
                <p className="auth-subtitle">
                  We've sent a password reset link to <strong>{email}</strong>
                </p>
                <p className="auth-subtitle">
                  Please check your email and click the link to reset your password.
                </p>
              </div>

              <div className="auth-footer">
                <p>
                  Didn't receive the email?
                  <button 
                    type="button" 
                    className="auth-toggle"
                    onClick={() => setIsEmailSent(false)}
                  >
                    Try Again
                  </button>
                </p>
                <p>
                  Remember your password?
                  <button 
                    type="button" 
                    className="auth-toggle"
                    onClick={handleBackToLogin}
                  >
                    Sign In
                  </button>
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default ForgotPassword
