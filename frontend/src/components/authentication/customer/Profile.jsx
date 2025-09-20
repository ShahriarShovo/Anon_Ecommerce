import React, {useState, useEffect, useCallback, memo} from 'react'
import {useAuth} from '../../../contexts/AuthContext'
import apiService from '../../../services/api'

const Profile = memo(() => {
  const {user, updateProfile, isLoading} = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [profileData, setProfileData] = useState({
    username: '',
    full_name: '',
    address: '',
    city: '',
    zipcode: '',
    country: ''
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [addresses, setAddresses] = useState([])
  const [defaultAddress, setDefaultAddress] = useState(null)
  const [showAddressForm, setShowAddressForm] = useState(false)
  const [editingAddress, setEditingAddress] = useState(null)
  const [addressForm, setAddressForm] = useState({
    full_name: '',
    phone_number: '',
    city: '',
    address_line_1: '',
    address_line_2: '',
    postal_code: '',
    country: 'Bangladesh',
    address_type: 'home',
    is_default: false
  })
  const [isSubmittingAddress, setIsSubmittingAddress] = useState(false)


  // Load addresses
  const loadAddresses = useCallback(async () => {
    if(!user?.id) {
      console.log('🔄 No user ID, skipping address load')
      return
    }

    try {
      console.log('🔄 Loading addresses for user:', user?.email, '(ID:', user?.id, ')')
      const response = await apiService.getAddresses()
      console.log('📋 Address API response:', response)

      // Django REST framework returns array directly for ListAPIView
      if(Array.isArray(response)) {
        console.log('📋 Direct array response:', response)
        console.log('📋 Addresses belong to users:', response.map(addr => ({
          id: addr.id,
          user_id: addr.user,
          full_name: addr.full_name,
          is_default: addr.is_default
        })))
        console.log('📋 Full address details:', response)

        // Check address isolation
        const currentUserId = user?.id
        const allUserIds = response.map(addr => addr.user)
        const uniqueUserIds = [...new Set(allUserIds)]
        console.log('🔍 Address Isolation Check:')
        console.log('  Current User ID:', currentUserId)
        console.log('  All User IDs in addresses:', allUserIds)
        console.log('  Unique User IDs:', uniqueUserIds)
        console.log('  Is Isolation Correct?', uniqueUserIds.length === 1 && uniqueUserIds[0] === currentUserId)
        setAddresses(response)
        const defaultAddr = response.find(addr => addr.is_default)
        setDefaultAddress(defaultAddr || null)
      } else {
        console.log('📋 Non-array response:', response)
        setAddresses([])
        setDefaultAddress(null)
      }
    } catch(error) {
      console.error('❌ Error loading addresses:', error)
      setAddresses([])
      setDefaultAddress(null)
    }
  }, [user])

  // Load user data when component mounts or user changes
  useEffect(() => {
    if(user) {
      setProfileData({
        username: user.username || '',
        full_name: user.full_name || '',
        address: user.address || '',
        city: user.city || '',
        zipcode: user.zipcode || '',
        country: user.country || ''
      })
      loadAddresses()
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

    console.log('🔍 Profile Submit - User object:', user)
    console.log('🔍 Profile Submit - User ID:', user?.id)
    console.log('🔍 Profile Submit - Profile Data:', profileData)

    if(!user?.id) {
      setError('User ID not found. Please refresh the page and try again.')
      return
    }

    try {
      const result = await updateProfile(user.id, profileData)
      if(result.success) {
        setSuccess('Profile updated successfully!')
        setIsEditing(false)
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError(result.message)
      }
    } catch(error) {
      console.error('❌ Profile update error:', error)
      setError('An unexpected error occurred. Please try again.')
    }
  }, [profileData, user, updateProfile])

  const handleCancel = useCallback(() => {
    // Reset form data to original user data
    if(user) {
      setProfileData({
        username: user.username || '',
        full_name: user.full_name || '',
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


  // Address functions
  const handleAddressInputChange = useCallback((e) => {
    setAddressForm(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }, [])

  const handleCreateAddress = useCallback(async (e) => {
    e.preventDefault()

    if(isSubmittingAddress) {
      return // Prevent multiple submissions
    }

    setIsSubmittingAddress(true)
    setError('')
    setSuccess('')

    try {
      const response = await apiService.createAddress(addressForm)
      console.log('✅ Address creation response:', response)

      // Django REST framework returns the created object directly
      if(response && response.id) {
        setSuccess('Address created successfully!')
        setShowAddressForm(false)
        setAddressForm({
          full_name: '',
          phone_number: '',
          city: '',
          address_line_1: '',
          address_line_2: '',
          postal_code: '',
          country: 'Bangladesh',
          address_type: 'home',
          is_default: false
        })
        loadAddresses()
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Failed to create address')
      }
    } catch(error) {
      console.error('❌ Address creation error:', error)
      setError('An unexpected error occurred. Please try again.')
    } finally {
      setIsSubmittingAddress(false)
    }
  }, [addressForm, loadAddresses, isSubmittingAddress])

  const handleUpdateAddress = useCallback(async (e) => {
    e.preventDefault()

    if(isSubmittingAddress) {
      return // Prevent multiple submissions
    }

    setIsSubmittingAddress(true)
    setError('')
    setSuccess('')

    try {
      console.log('✏️ Updating address ID:', editingAddress.id)
      console.log('✏️ Update data:', addressForm)
      const response = await apiService.updateAddress(editingAddress.id, addressForm)
      console.log('✏️ Update response:', response)

      // Django REST framework returns the updated object directly
      if(response && response.id) {
        setSuccess('Address updated successfully!')
        setShowAddressForm(false)
        setEditingAddress(null)
        setAddressForm({
          full_name: '',
          phone_number: '',
          city: '',
          address_line_1: '',
          address_line_2: '',
          postal_code: '',
          country: 'Bangladesh',
          address_type: 'home',
          is_default: false
        })
        loadAddresses()
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError(response.message || 'Failed to update address')
      }
    } catch(error) {
      console.error('❌ Address update error:', error)
      setError('An unexpected error occurred. Please try again.')
    } finally {
      setIsSubmittingAddress(false)
    }
  }, [addressForm, editingAddress, loadAddresses, isSubmittingAddress])

  const handleDeleteAddress = useCallback(async (addressId) => {
    if(window.confirm('Are you sure you want to delete this address?')) {
      try {
        console.log('🗑️ Deleting address ID:', addressId)
        const response = await apiService.deleteAddress(addressId)
        console.log('🗑️ Delete response:', response)

        // Django REST framework DELETE returns 204 No Content on success
        // If we get here without error, deletion was successful
        setSuccess('Address deleted successfully!')
        loadAddresses()
        setTimeout(() => setSuccess(''), 3000)
      } catch(error) {
        console.error('❌ Address deletion error:', error)

        // Check if it's a protected foreign key error
        if(error.message && error.message.includes('protected_foreign_key')) {
          setError('Cannot delete this address because it is being used in an existing order. Please contact support if you need to remove it.')
        } else if(error.message && error.message.includes('Cannot delete')) {
          setError('Cannot delete this address because it is being used in an existing order. Please contact support if you need to remove it.')
        } else {
          setError('An unexpected error occurred. Please try again.')
        }
      }
    }
  }, [loadAddresses])

  const handleSetDefaultAddress = useCallback(async (addressId) => {
    try {
      const response = await apiService.setDefaultAddress(addressId)
      if(response.success) {
        setSuccess('Default address updated successfully!')
        loadAddresses()
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError(response.message || 'Failed to set default address')
      }
    } catch(error) {
      setError('An unexpected error occurred. Please try again.')
    }
  }, [loadAddresses])

  const handleEditAddress = useCallback((address) => {
    setEditingAddress(address)
    setAddressForm({
      full_name: address.full_name || '',
      phone_number: address.phone_number || '',
      city: address.city || '',
      address_line_1: address.address_line_1 || '',
      address_line_2: address.address_line_2 || '',
      postal_code: address.postal_code || '',
      country: address.country || 'Bangladesh',
      address_type: address.address_type || 'home',
      is_default: address.is_default || false
    })
    setShowAddressForm(true)
  }, [])

  const handleCancelAddressForm = useCallback(() => {
    setShowAddressForm(false)
    setEditingAddress(null)
    setAddressForm({
      full_name: '',
      phone_number: '',
      city: '',
      address_line_1: '',
      address_line_2: '',
      postal_code: '',
      country: 'Bangladesh',
      address_type: 'home',
      is_default: false
    })
  }, [])

  // Redirect to home if not authenticated
  if(!user) {
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

            </div>

            <div className="profile-section">
              <div className="section-header">
                <h3 className="section-title">Address Information</h3>
                <button
                  type="button"
                  className="add-address-btn"
                  onClick={() => setShowAddressForm(true)}
                >
                  <ion-icon name="add-outline"></ion-icon>
                  Add Address
                </button>
              </div>

              {/* Debug Info */}
              {console.log('🏠 Address Display Debug:', {
                addresses: addresses,
                defaultAddress: defaultAddress,
                addressesLength: addresses.length
              })}

              {/* Default Address Display */}
              {defaultAddress ? (
                <div className="default-address-card">
                  <div className="address-header">
                    <h4>Default Address</h4>
                    <span className="address-type-badge">{defaultAddress.address_type}</span>
                  </div>
                  <div className="address-details">
                    <p><strong>{defaultAddress.full_name}</strong></p>
                    <p>{defaultAddress.phone_number}</p>
                    <p>{defaultAddress.address_line_1}</p>
                    {defaultAddress.address_line_2 && <p>{defaultAddress.address_line_2}</p>}
                    <p>{defaultAddress.city}, {defaultAddress.postal_code}</p>
                    <p>{defaultAddress.country}</p>
                  </div>
                  <div className="address-actions">
                    <button
                      type="button"
                      className="address-action-btn edit"
                      onClick={() => handleEditAddress(defaultAddress)}
                    >
                      <ion-icon name="create-outline"></ion-icon>
                      Edit
                    </button>
                    <button
                      type="button"
                      className="address-action-btn delete"
                      onClick={() => handleDeleteAddress(defaultAddress.id)}
                    >
                      <ion-icon name="trash-outline"></ion-icon>
                      Delete
                    </button>
                  </div>
                </div>
              ) : (
                <div className="no-address">
                  <p>No default address set. Add an address to get started.</p>
                  <p style={{fontSize: '12px', color: '#999', marginTop: '8px'}}>
                    Debug: {addresses.length} addresses found
                  </p>
                </div>
              )}

              {/* All Addresses List */}
              {addresses.length > 1 && (
                <div className="all-addresses">
                  <h4>All Addresses</h4>
                  {addresses.filter(addr => !addr.is_default && addr.id !== defaultAddress?.id).map((address) => (
                    <div key={address.id} className="address-card">
                      <div className="address-header">
                        <h5>{address.full_name}</h5>
                        <span className="address-type-badge">{address.address_type}</span>
                      </div>
                      <div className="address-details">
                        <p>{address.phone_number}</p>
                        <p>{address.address_line_1}</p>
                        {address.address_line_2 && <p>{address.address_line_2}</p>}
                        <p>{address.city}, {address.postal_code}</p>
                        <p>{address.country}</p>
                      </div>
                      <div className="address-actions">
                        <button
                          type="button"
                          className="address-action-btn set-default"
                          onClick={() => handleSetDefaultAddress(address.id)}
                        >
                          <ion-icon name="star-outline"></ion-icon>
                          Set Default
                        </button>
                        <button
                          type="button"
                          className="address-action-btn edit"
                          onClick={() => handleEditAddress(address)}
                        >
                          <ion-icon name="create-outline"></ion-icon>
                          Edit
                        </button>
                        <button
                          type="button"
                          className="address-action-btn delete"
                          onClick={() => handleDeleteAddress(address.id)}
                        >
                          <ion-icon name="trash-outline"></ion-icon>
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
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

        </div>
      </div>

      {/* Address Form Modal */}
      {showAddressForm && (
        <div className="address-form-modal">
          <div className="address-form-overlay" onClick={handleCancelAddressForm}></div>
          <div className="address-form-container">
            <div className="address-form-header">
              <h3>{editingAddress ? 'Edit Address' : 'Add New Address'}</h3>
              <button
                type="button"
                className="close-btn"
                onClick={handleCancelAddressForm}
              >
                <ion-icon name="close-outline"></ion-icon>
              </button>
            </div>

            <form
              className="address-form"
              onSubmit={editingAddress ? handleUpdateAddress : handleCreateAddress}
            >
              <div className="form-row">
                <div className="input-group">
                  <label htmlFor="full_name">Full Name *</label>
                  <input
                    type="text"
                    id="full_name"
                    name="full_name"
                    value={addressForm.full_name}
                    onChange={handleAddressInputChange}
                    required
                  />
                </div>
                <div className="input-group">
                  <label htmlFor="phone_number">Phone Number *</label>
                  <input
                    type="tel"
                    id="phone_number"
                    name="phone_number"
                    value={addressForm.phone_number}
                    onChange={handleAddressInputChange}
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="address_line_1">Address Line 1 *</label>
                <input
                  type="text"
                  id="address_line_1"
                  name="address_line_1"
                  value={addressForm.address_line_1}
                  onChange={handleAddressInputChange}
                  required
                />
              </div>

              <div className="input-group">
                <label htmlFor="address_line_2">Address Line 2</label>
                <input
                  type="text"
                  id="address_line_2"
                  name="address_line_2"
                  value={addressForm.address_line_2}
                  onChange={handleAddressInputChange}
                />
              </div>

              <div className="form-row">
                <div className="input-group">
                  <label htmlFor="city">City *</label>
                  <input
                    type="text"
                    id="city"
                    name="city"
                    value={addressForm.city}
                    onChange={handleAddressInputChange}
                    required
                  />
                </div>
                <div className="input-group">
                  <label htmlFor="postal_code">Postal Code</label>
                  <input
                    type="text"
                    id="postal_code"
                    name="postal_code"
                    value={addressForm.postal_code}
                    onChange={handleAddressInputChange}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="input-group">
                  <label htmlFor="country">Country *</label>
                  <input
                    type="text"
                    id="country"
                    name="country"
                    value={addressForm.country}
                    onChange={handleAddressInputChange}
                    required
                  />
                </div>
                <div className="input-group">
                  <label htmlFor="address_type">Address Type</label>
                  <select
                    id="address_type"
                    name="address_type"
                    value={addressForm.address_type}
                    onChange={handleAddressInputChange}
                  >
                    <option value="home">Home</option>
                    <option value="office">Office</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={handleCancelAddressForm}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="save-btn"
                  disabled={isSubmittingAddress}
                >
                  {isSubmittingAddress ? (
                    <>
                      <ion-icon name="hourglass-outline"></ion-icon>
                      {editingAddress ? 'Updating...' : 'Adding...'}
                    </>
                  ) : (
                    editingAddress ? 'Update Address' : 'Add Address'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
})

export default Profile
