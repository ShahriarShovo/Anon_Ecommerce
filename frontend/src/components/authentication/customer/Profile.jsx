import React, { useState, useEffect, useCallback, memo } from 'react'
import { useAuth } from '../../../contexts/AuthContext'

const Profile = memo(() => {
  const { user, updateProfile, logout, isLoading } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [profileData, setProfileData] = useState({
    username: '',
    full_name: '',
    phone: '',
    address: '',
    city: '',
    zipcode: '',
    country: ''
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Load user data when component mounts or user changes
  useEffect(() => {
    if (user) {
      setProfileData({
        username: user.username || '',
        full_name: user.full_name || '',
        phone: user.phone || '',
        address: user.address || '',
        city: user.city || '',
        zipcode: user.zipcode || '',
        country: user.country || ''
      })
    }
  }, [user])

  const handleInputChange = useCallback((e) => {
    setProfileData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }, [])

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    try {
      const result = await updateProfile(user.id, profileData)
      if (result.success) {
        setSuccess('Profile updated successfully!')
        setIsEditing(false)
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError(result.message)
      }
    } catch (error) {
      setError('An unexpected error occurred. Please try again.')
    }
  }, [profileData, user, updateProfile])

  const handleCancel = useCallback(() => {
    // Reset form data to original user data
    if (user) {
      setProfileData({
        username: user.username || '',
        full_name: user.full_name || '',
        phone: user.phone || '',
        address: user.address || '',
        city: user.city || '',
        zipcode: user.zipcode || '',
        country: user.country || ''
      })
    }
    setIsEditing(false)
    setError('')
    setSuccess('')
  }, [user])

  const handleLogout = useCallback(() => {
    logout()
  }, [logout])

  // Redirect to home if not authenticated
  if (!user) {
    return (
      <div className="profile-page">
        <div className="container">
          <div className="not-authenticated">
            <h2>Please login to view your profile</h2>
            <p>You need to be logged in to access this page.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={{ 
      background: '#f9fafb', 
      padding: '32px 0',
      minHeight: 'calc(100vh - 20px)'
    }}>
      <div style={{ 
        maxWidth: '100%', 
        margin: '0', 
        padding: '0 16px' 
      }}>
        <div style={{
          background: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          border: '1px solid #e5e7eb',
          padding: '24px'
        }}>
          <div className="profile-header">
            <div className="profile-avatar">
              <ion-icon name="person-circle-outline"></ion-icon>
            </div>
            <h2 className="profile-title">My Profile</h2>
            <p className="profile-subtitle">Manage your account information</p>
          </div>

          {/* Error and Success Messages */}
          {error && (
            <div className="profile-message error">
              <ion-icon name="alert-circle-outline"></ion-icon>
              {error}
            </div>
          )}
          
          {success && (
            <div className="profile-message success">
              <ion-icon name="checkmark-circle-outline"></ion-icon>
              {success}
            </div>
          )}

          <form className="profile-form" onSubmit={handleSubmit}>
            <div className="profile-section">
              <h3 className="section-title">Personal Information</h3>
              
              <div className="form-row">
                <div className="input-group">
                  <label htmlFor="username">Username</label>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={profileData.username}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'disabled' : ''}
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="full_name">Full Name</label>
                  <input
                    type="text"
                    id="full_name"
                    name="full_name"
                    value={profileData.full_name}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'disabled' : ''}
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="phone">Phone Number</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={profileData.phone}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={!isEditing ? 'disabled' : ''}
                />
              </div>
            </div>

            <div className="profile-section">
              <h3 className="section-title">Address Information</h3>
              
              <div className="input-group">
                <label htmlFor="address">Address</label>
                <textarea
                  id="address"
                  name="address"
                  value={profileData.address}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={!isEditing ? 'disabled' : ''}
                  rows="3"
                />
              </div>

              <div className="form-row">
                <div className="input-group">
                  <label htmlFor="city">City</label>
                  <input
                    type="text"
                    id="city"
                    name="city"
                    value={profileData.city}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'disabled' : ''}
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="zipcode">Zip Code</label>
                  <input
                    type="text"
                    id="zipcode"
                    name="zipcode"
                    value={profileData.zipcode}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'disabled' : ''}
                  />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="country">Country</label>
                <input
                  type="text"
                  id="country"
                  name="country"
                  value={profileData.country}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={!isEditing ? 'disabled' : ''}
                />
              </div>
            </div>

            <div className="profile-actions">
              {!isEditing ? (
                <button 
                  type="button" 
                  className="profile-btn edit-btn"
                  onClick={() => setIsEditing(true)}
                >
                  <ion-icon name="create-outline"></ion-icon>
                  Edit Profile
                </button>
              ) : (
                <div className="edit-actions">
                  <button 
                    type="button" 
                    className="profile-btn cancel-btn"
                    onClick={handleCancel}
                  >
                    <ion-icon name="close-outline"></ion-icon>
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    className="profile-btn save-btn"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <ion-icon name="hourglass-outline"></ion-icon>
                        Saving...
                      </>
                    ) : (
                      <>
                        <ion-icon name="checkmark-outline"></ion-icon>
                        Save Changes
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </form>

          <div className="profile-footer">
            <button 
              type="button" 
              className="logout-btn"
              onClick={handleLogout}
            >
              <ion-icon name="log-out-outline"></ion-icon>
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  )
})

export default Profile
