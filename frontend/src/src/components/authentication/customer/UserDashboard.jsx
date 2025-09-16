import React, { useState, memo } from 'react'
import { useAuth } from '../../../contexts/AuthContext'
import UserSidebar from './UserSidebar'
import Profile from './Profile'

const UserDashboard = memo(() => {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('dashboard')

  // Redirect to home if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Please login to access your dashboard</h2>
            <p className="text-gray-600">You need to be logged in to access this page.</p>
          </div>
        </div>
      </div>
    )
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
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
              
              {/* Page Header */}
              <div style={{ marginBottom: '32px' }}>
                <h1 style={{ 
                  fontSize: '30px', 
                  fontWeight: 'bold', 
                  color: '#111827',
                  margin: '0 0 8px 0'
                }}>Account</h1>
                <p style={{ 
                  fontSize: '14px', 
                  color: '#6b7280',
                  margin: '0'
                }}>
                  Manage your account, view orders, and update your information.
                </p>
              </div>

              {/* Welcome Section */}
              <div style={{
                background: 'white',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e5e7eb',
                padding: '24px',
                marginBottom: '32px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{ flexShrink: 0 }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      background: '#eef2ff',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <span style={{ fontSize: '24px' }}>👤</span>
                    </div>
                  </div>
                  <div style={{ marginLeft: '16px' }}>
                    <h2 style={{ 
                      fontSize: '20px', 
                      fontWeight: '600', 
                      color: '#111827',
                      margin: '0 0 4px 0'
                    }}>Welcome back, {user?.full_name || user?.username}!</h2>
                    <p style={{ 
                      fontSize: '14px', 
                      color: '#6b7280',
                      margin: '0'
                    }}>Here's what's happening with your account.</p>
                  </div>
                </div>
              </div>

              {/* Account Statistics */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '24px',
                marginBottom: '32px'
              }}>
                <div style={{
                  background: 'white',
                  borderRadius: '8px',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                  border: '1px solid #e5e7eb',
                  padding: '24px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <div style={{ flexShrink: 0 }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        background: '#dbeafe',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{ fontSize: '16px' }}>📦</span>
                      </div>
                    </div>
                    <div style={{ marginLeft: '16px' }}>
                      <p style={{ 
                        fontSize: '14px', 
                        fontWeight: '500', 
                        color: '#6b7280',
                        margin: '0 0 4px 0'
                      }}>Total Orders</p>
                      <p style={{ 
                        fontSize: '24px', 
                        fontWeight: 'bold', 
                        color: '#111827',
                        margin: '0'
                      }}>0</p>
                    </div>
                  </div>
                </div>

                <div style={{
                  background: 'white',
                  borderRadius: '8px',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                  border: '1px solid #e5e7eb',
                  padding: '24px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <div style={{ flexShrink: 0 }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        background: '#dcfce7',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{ fontSize: '16px' }}>💰</span>
                      </div>
                    </div>
                    <div style={{ marginLeft: '16px' }}>
                      <p style={{ 
                        fontSize: '14px', 
                        fontWeight: '500', 
                        color: '#6b7280',
                        margin: '0 0 4px 0'
                      }}>Total Spent</p>
                      <p style={{ 
                        fontSize: '24px', 
                        fontWeight: 'bold', 
                        color: '#111827',
                        margin: '0'
                      }}>$0.00</p>
                    </div>
                  </div>
                </div>

                <div style={{
                  background: 'white',
                  borderRadius: '8px',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                  border: '1px solid #e5e7eb',
                  padding: '24px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <div style={{ flexShrink: 0 }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        background: '#f3e8ff',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{ fontSize: '16px' }}>📍</span>
                      </div>
                    </div>
                    <div style={{ marginLeft: '16px' }}>
                      <p style={{ 
                        fontSize: '14px', 
                        fontWeight: '500', 
                        color: '#6b7280',
                        margin: '0 0 4px 0'
                      }}>Saved Addresses</p>
                      <p style={{ 
                        fontSize: '24px', 
                        fontWeight: 'bold', 
                        color: '#111827',
                        margin: '0'
                      }}>0</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div style={{
                background: 'white',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e5e7eb',
                padding: '24px',
                marginBottom: '32px'
              }}>
                <h3 style={{ 
                  fontSize: '18px', 
                  fontWeight: '500', 
                  color: '#111827',
                  margin: '0 0 16px 0'
                }}>Quick Actions</h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '16px'
                }}>
                  <button 
                    onClick={() => setActiveTab('profile')}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '12px 16px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#374151',
                      background: 'white',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = '#f9fafb'
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'white'
                    }}
                  >
                    <span style={{ marginRight: '8px', fontSize: '16px' }}>👤</span>
                    Edit Profile
                  </button>
                  <button 
                    onClick={() => setActiveTab('addresses')}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '12px 16px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#374151',
                      background: 'white',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = '#f9fafb'
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'white'
                    }}
                  >
                    <span style={{ marginRight: '8px', fontSize: '16px' }}>📍</span>
                    Manage Addresses
                  </button>
                  <button 
                    onClick={() => setActiveTab('orders')}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '12px 16px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#374151',
                      background: 'white',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = '#f9fafb'
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'white'
                    }}
                  >
                    <span style={{ marginRight: '8px', fontSize: '16px' }}>📦</span>
                    View All Orders
                  </button>
                </div>
              </div>

              {/* Recent Orders */}
              <div style={{
                background: 'white',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{
                  padding: '16px 24px',
                  borderBottom: '1px solid #e5e7eb',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <h3 style={{ 
                    fontSize: '18px', 
                    fontWeight: '500', 
                    color: '#111827',
                    margin: '0'
                  }}>Recent Orders</h3>
                  <button 
                    onClick={() => setActiveTab('orders')}
                    style={{
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#6366f1',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer'
                    }}
                  >
                    View all
                  </button>
                </div>
                <div style={{ padding: '24px' }}>
                  <div style={{ textAlign: 'center', padding: '48px 0' }}>
                    <span style={{ fontSize: '48px', color: '#9ca3af' }}>📦</span>
                    <h3 style={{ 
                      marginTop: '8px',
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#111827',
                      margin: '8px 0 4px 0'
                    }}>No orders yet</h3>
                    <p style={{ 
                      fontSize: '14px', 
                      color: '#6b7280',
                      margin: '0'
                    }}>
                      When you place your first order, it will appear here.
                    </p>
                  </div>
                </div>
              </div>

              {/* Account Information */}
              <div style={{
                marginTop: '32px',
                background: 'white',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{
                  padding: '16px 24px',
                  borderBottom: '1px solid #e5e7eb'
                }}>
                  <h3 style={{ 
                    fontSize: '18px', 
                    fontWeight: '500', 
                    color: '#111827',
                    margin: '0'
                  }}>Account Information</h3>
                </div>
                <div style={{ padding: '24px' }}>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: '24px'
                  }}>
                    <div>
                      <h4 style={{ 
                        fontSize: '14px', 
                        fontWeight: '500', 
                        color: '#111827',
                        margin: '0 0 8px 0'
                      }}>Contact Information</h4>
                      <div style={{ fontSize: '14px', color: '#6b7280' }}>
                        <p style={{ margin: '0 0 4px 0' }}>{user?.full_name || user?.username}</p>
                        <p style={{ margin: '0 0 4px 0' }}>{user?.email}</p>
                        {user?.phone && <p style={{ margin: '0' }}>{user.phone}</p>}
                      </div>
                    </div>
                    <div>
                      <h4 style={{ 
                        fontSize: '14px', 
                        fontWeight: '500', 
                        color: '#111827',
                        margin: '0 0 8px 0'
                      }}>Marketing Preferences</h4>
                      <div style={{ fontSize: '14px', color: '#6b7280' }}>
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                          <span style={{ marginRight: '8px', fontSize: '16px' }}>❌</span>
                          You're not subscribed to marketing emails
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        )
      case 'profile':
        return <Profile />
      case 'orders':
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
              
              {/* Page Header */}
              <div style={{ marginBottom: '32px' }}>
                <h1 style={{ 
                  fontSize: '30px', 
                  fontWeight: 'bold', 
                  color: '#111827',
                  margin: '0 0 8px 0'
                }}>My Orders</h1>
                <p style={{ 
                  fontSize: '14px', 
                  color: '#6b7280',
                  margin: '0'
                }}>
                  View and track your order history.
                </p>
              </div>

              {/* Orders List */}
              <div style={{
                background: 'white',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{
                  padding: '16px 24px',
                  borderBottom: '1px solid #e5e7eb'
                }}>
                  <h3 style={{ 
                    fontSize: '18px', 
                    fontWeight: '500', 
                    color: '#111827',
                    margin: '0'
                  }}>Order History</h3>
                </div>
                <div style={{ padding: '24px' }}>
                  <div style={{ textAlign: 'center', padding: '48px 0' }}>
                    <span style={{ fontSize: '48px', color: '#9ca3af' }}>📦</span>
                    <h3 style={{ 
                      marginTop: '8px',
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#111827',
                      margin: '8px 0 4px 0'
                    }}>No orders yet</h3>
                    <p style={{ 
                      fontSize: '14px', 
                      color: '#6b7280',
                      margin: '0 0 24px 0'
                    }}>
                      When you place your first order, it will appear here.
                    </p>
                    <button style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '8px 16px',
                      border: 'none',
                      borderRadius: '6px',
                      boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: 'white',
                      background: '#6366f1',
                      cursor: 'pointer'
                    }}>
                      Start Shopping
                    </button>
                  </div>
                </div>
              </div>

            </div>
          </div>
        )
      case 'addresses':
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
              
              {/* Page Header */}
              <div style={{ marginBottom: '32px' }}>
                <h1 style={{ 
                  fontSize: '30px', 
                  fontWeight: 'bold', 
                  color: '#111827',
                  margin: '0 0 8px 0'
                }}>My Addresses</h1>
                <p style={{ 
                  fontSize: '14px', 
                  color: '#6b7280',
                  margin: '0'
                }}>
                  Manage your shipping addresses.
                </p>
              </div>

              {/* Addresses List */}
              <div style={{
                background: 'white',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{
                  padding: '16px 24px',
                  borderBottom: '1px solid #e5e7eb',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <h3 style={{ 
                    fontSize: '18px', 
                    fontWeight: '500', 
                    color: '#111827',
                    margin: '0'
                  }}>Saved Addresses</h3>
                  <button style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    padding: '8px 16px',
                    border: 'none',
                    borderRadius: '6px',
                    boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: 'white',
                    background: '#6366f1',
                    cursor: 'pointer'
                  }}>
                    Add New Address
                  </button>
                </div>
                <div style={{ padding: '24px' }}>
                  <div style={{ textAlign: 'center', padding: '48px 0' }}>
                    <span style={{ fontSize: '48px', color: '#9ca3af' }}>📍</span>
                    <h3 style={{ 
                      marginTop: '8px',
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#111827',
                      margin: '8px 0 4px 0'
                    }}>No addresses yet</h3>
                    <p style={{ 
                      fontSize: '14px', 
                      color: '#6b7280',
                      margin: '0'
                    }}>
                      Add your first address to get started.
                    </p>
                  </div>
                </div>
              </div>

            </div>
          </div>
        )
      default:
        return <Profile />
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb', paddingTop: '20px' }}>
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        display: 'flex', 
        minHeight: 'calc(100vh - 20px)',
        padding: '0 20px'
      }}>
        <UserSidebar activeTab={activeTab} onTabChange={setActiveTab} />
        <div style={{ flex: 1, overflow: 'hidden' }}>
          {renderContent()}
        </div>
      </div>
    </div>
  )
})

export default UserDashboard
