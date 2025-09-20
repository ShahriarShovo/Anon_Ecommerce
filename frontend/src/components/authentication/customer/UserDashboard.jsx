import React, {useState, useEffect, memo} from 'react'
import {useAuth} from '../../../contexts/AuthContext'
import UserSidebar from './UserSidebar'
import Profile from './Profile'
import apiService from '../../../services/api'

const UserDashboard = memo(() => {
  const {user} = useAuth()
  const [activeTab, setActiveTab] = useState('dashboard')
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [addresses, setAddresses] = useState([])
  const [addressLoading, setAddressLoading] = useState(false)

  // Fetch orders when component mounts or user changes
  useEffect(() => {
    const fetchOrders = async () => {
      if(!user) return

      setLoading(true)
      setError(null)

      try {
        console.log('🛒 UserDashboard: Fetching orders for user:', user.id)
        const ordersData = await apiService.getOrders()
        console.log('🛒 UserDashboard: Orders fetched:', ordersData)

        // Debug order items structure
        if(ordersData && ordersData.length > 0) {
          console.log('🛒 UserDashboard: First order structure:', ordersData[0])
          if(ordersData[0].items && ordersData[0].items.length > 0) {
            console.log('🛒 UserDashboard: First order item structure:', ordersData[0].items[0])
            console.log('🛒 UserDashboard: Product data in item:', ordersData[0].items[0].product)
          }
        }

        setOrders(ordersData)
      } catch(err) {
        console.error('🛒 UserDashboard: Error fetching orders:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchOrders()
  }, [user])

  // Fetch addresses when component mounts or user changes
  useEffect(() => {
    const fetchAddresses = async () => {
      if(!user) return

      setAddressLoading(true)

      try {
        console.log('🏠 UserDashboard: Fetching addresses for user:', user.id)
        const addressesData = await apiService.getAddresses()
        console.log('🏠 UserDashboard: Addresses fetched:', addressesData)
        setAddresses(addressesData)
      } catch(err) {
        console.error('🏠 UserDashboard: Error fetching addresses:', err)
      } finally {
        setAddressLoading(false)
      }
    }

    fetchAddresses()
  }, [user])

  // Calculate order statistics
  const totalOrders = orders.length
  const totalSpent = orders.reduce((sum, order) => sum + parseFloat(order.total_amount || 0), 0)

  // Calculate address statistics
  const totalAddresses = addresses.length

  // Redirect to home if not authenticated
  if(!user) {
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
    switch(activeTab) {
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
              <div style={{marginBottom: '32px'}}>
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
                <div style={{display: 'flex', alignItems: 'center'}}>
                  <div style={{flexShrink: 0}}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      background: '#eef2ff',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <span style={{fontSize: '24px'}}>👤</span>
                    </div>
                  </div>
                  <div style={{marginLeft: '16px'}}>
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
                  <div style={{display: 'flex', alignItems: 'center'}}>
                    <div style={{flexShrink: 0}}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        background: '#dbeafe',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{fontSize: '16px'}}>📦</span>
                      </div>
                    </div>
                    <div style={{marginLeft: '16px'}}>
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
                      }}>{loading ? '...' : totalOrders}</p>
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
                  <div style={{display: 'flex', alignItems: 'center'}}>
                    <div style={{flexShrink: 0}}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        background: '#dcfce7',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{fontSize: '16px'}}>💰</span>
                      </div>
                    </div>
                    <div style={{marginLeft: '16px'}}>
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
                      }}>${loading ? '...' : totalSpent.toFixed(2)}</p>
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
                  <div style={{display: 'flex', alignItems: 'center'}}>
                    <div style={{flexShrink: 0}}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        background: '#f3e8ff',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{fontSize: '16px'}}>📍</span>
                      </div>
                    </div>
                    <div style={{marginLeft: '16px'}}>
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
                      }}>{addressLoading ? '...' : totalAddresses}</p>
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
                    <span style={{marginRight: '8px', fontSize: '16px'}}>👤</span>
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
                    <span style={{marginRight: '8px', fontSize: '16px'}}>📍</span>
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
                    <span style={{marginRight: '8px', fontSize: '16px'}}>📦</span>
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
                <div style={{padding: '24px'}}>
                  {loading ? (
                    <div style={{textAlign: 'center', padding: '48px 0'}}>
                      <span style={{fontSize: '48px', color: '#9ca3af'}}>⏳</span>
                      <h3 style={{
                        marginTop: '8px',
                        fontSize: '14px',
                        fontWeight: '500',
                        color: '#111827',
                        margin: '8px 0 4px 0'
                      }}>Loading orders...</h3>
                    </div>
                  ) : error ? (
                    <div style={{textAlign: 'center', padding: '48px 0'}}>
                      <span style={{fontSize: '48px', color: '#ef4444'}}>⚠️</span>
                      <h3 style={{
                        marginTop: '8px',
                        fontSize: '14px',
                        fontWeight: '500',
                        color: '#111827',
                        margin: '8px 0 4px 0'
                      }}>Error loading orders</h3>
                      <p style={{
                        fontSize: '14px',
                        color: '#6b7280',
                        margin: '0'
                      }}>
                        {error}
                      </p>
                    </div>
                  ) : orders.length === 0 ? (
                    <div style={{textAlign: 'center', padding: '48px 0'}}>
                      <span style={{fontSize: '48px', color: '#9ca3af'}}>📦</span>
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
                  ) : (
                    <div>
                      {orders.slice(0, 3).map((order) => (
                        <div key={order.id} style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '16px 0',
                          borderBottom: '1px solid #f3f4f6'
                        }}>
                          <div>
                            <h4 style={{
                              fontSize: '16px',
                              fontWeight: '500',
                              color: '#111827',
                              margin: '0 0 4px 0'
                            }}>Order #{order.order_number}</h4>
                            <p style={{
                              fontSize: '14px',
                              color: '#6b7280',
                              margin: '0 0 4px 0'
                            }}>
                              {new Date(order.created_at).toLocaleDateString()}
                            </p>
                            <p style={{
                              fontSize: '14px',
                              color: '#6b7280',
                              margin: '0'
                            }}>
                              {order.items?.length || 0} item(s)
                            </p>
                          </div>
                          <div style={{textAlign: 'right'}}>
                            <p style={{
                              fontSize: '16px',
                              fontWeight: '600',
                              color: '#111827',
                              margin: '0 0 4px 0'
                            }}>${parseFloat(order.total_amount).toFixed(2)}</p>
                            <span style={{
                              display: 'inline-block',
                              padding: '4px 8px',
                              borderRadius: '4px',
                              fontSize: '12px',
                              fontWeight: '500',
                              textTransform: 'capitalize',
                              backgroundColor: order.status === 'delivered' ? '#dcfce7' :
                                order.status === 'pending' ? '#fef3c7' : '#dbeafe',
                              color: order.status === 'delivered' ? '#166534' :
                                order.status === 'pending' ? '#92400e' : '#1e40af'
                            }}>
                              {order.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
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
                <div style={{padding: '24px'}}>
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
                      <div style={{fontSize: '14px', color: '#6b7280'}}>
                        <p style={{margin: '0 0 4px 0'}}>{user?.full_name || user?.username}</p>
                        <p style={{margin: '0 0 4px 0'}}>{user?.email}</p>
                        {user?.phone && <p style={{margin: '0'}}>{user.phone}</p>}
                      </div>
                    </div>
                    <div>
                      <h4 style={{
                        fontSize: '14px',
                        fontWeight: '500',
                        color: '#111827',
                        margin: '0 0 8px 0'
                      }}>Marketing Preferences</h4>
                      <div style={{fontSize: '14px', color: '#6b7280'}}>
                        <div style={{display: 'flex', alignItems: 'center'}}>
                          <span style={{marginRight: '8px', fontSize: '16px'}}>❌</span>
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
              <div style={{marginBottom: '32px'}}>
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
                <div style={{padding: '24px'}}>
                  {loading ? (
                    <div style={{textAlign: 'center', padding: '48px 0'}}>
                      <span style={{fontSize: '48px', color: '#9ca3af'}}>⏳</span>
                      <h3 style={{
                        marginTop: '8px',
                        fontSize: '14px',
                        fontWeight: '500',
                        color: '#111827',
                        margin: '8px 0 4px 0'
                      }}>Loading orders...</h3>
                    </div>
                  ) : error ? (
                    <div style={{textAlign: 'center', padding: '48px 0'}}>
                      <span style={{fontSize: '48px', color: '#ef4444'}}>⚠️</span>
                      <h3 style={{
                        marginTop: '8px',
                        fontSize: '14px',
                        fontWeight: '500',
                        color: '#111827',
                        margin: '8px 0 4px 0'
                      }}>Error loading orders</h3>
                      <p style={{
                        fontSize: '14px',
                        color: '#6b7280',
                        margin: '0'
                      }}>
                        {error}
                      </p>
                    </div>
                  ) : orders.length === 0 ? (
                    <div style={{textAlign: 'center', padding: '48px 0'}}>
                      <span style={{fontSize: '48px', color: '#9ca3af'}}>📦</span>
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
                      <button
                        onClick={() => window.location.href = '/'}
                        style={{
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
                        }}
                      >
                        Start Shopping
                      </button>
                    </div>
                  ) : (
                    <div>
                      {/* Table Header */}
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr 1fr',
                        gap: '16px',
                        padding: '16px 20px',
                        backgroundColor: '#f9fafb',
                        borderBottom: '2px solid #e5e7eb',
                        borderRadius: '8px 8px 0 0',
                        fontWeight: '600',
                        fontSize: '14px',
                        color: '#374151'
                      }}>
                        <div>Product</div>
                        <div>Order ID</div>
                        <div>Invoice ID</div>
                        <div>Status</div>
                        <div>Amount</div>
                        <div>Date</div>
                      </div>

                      {/* Order Items List */}
                      {orders.map((order) => (
                        <div key={order.id}>
                          {order.items?.map((item, itemIndex) => (
                            <div key={`${order.id}-${itemIndex}`} style={{
                              display: 'grid',
                              gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr 1fr',
                              gap: '16px',
                              padding: '20px',
                              borderBottom: '1px solid #e5e7eb',
                              backgroundColor: 'white',
                              alignItems: 'center'
                            }}>
                              {/* Product Column */}
                              <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                                <div style={{
                                  width: '60px',
                                  height: '60px',
                                  backgroundColor: '#f3f4f6',
                                  borderRadius: '8px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  overflow: 'hidden',
                                  border: '1px solid #e5e7eb'
                                }}>
                                  {(() => {
                                    console.log('🖼️ Order item product data:', item.product);
                                    console.log('🖼️ Primary image data:', item.product?.primary_image);

                                    // Try multiple image sources
                                    const imageUrl = item.product?.primary_image?.image_url ||
                                      item.product?.primary_image?.image ||
                                      item.product?.image_url ||
                                      item.product?.image;

                                    console.log('🖼️ Found image URL:', imageUrl);

                                    if(imageUrl) {
                                      // Handle relative URLs
                                      const fullImageUrl = imageUrl.startsWith('http') ?
                                        imageUrl :
                                        `http://127.0.0.1:8000${imageUrl}`;

                                      console.log('🖼️ Full image URL:', fullImageUrl);

                                      return (
                                        <img
                                          src={fullImageUrl}
                                          alt={item.product_name}
                                          style={{
                                            width: '100%',
                                            height: '100%',
                                            objectFit: 'cover'
                                          }}
                                          onError={(e) => {
                                            console.log('🖼️ Image failed to load:', fullImageUrl);
                                            e.target.style.display = 'none';
                                            e.target.nextSibling.style.display = 'flex';
                                          }}
                                          onLoad={() => {
                                            console.log('🖼️ Image loaded successfully:', fullImageUrl);
                                          }}
                                        />
                                      );
                                    }

                                    console.log('🖼️ No image URL found, showing fallback');
                                    return (
                                      <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        width: '100%',
                                        height: '100%'
                                      }}>
                                        <span style={{fontSize: '24px', color: '#9ca3af'}}>📦</span>
                                      </div>
                                    );
                                  })()}
                                </div>
                                <div>
                                  <h4 style={{
                                    fontSize: '16px',
                                    fontWeight: '500',
                                    color: '#111827',
                                    margin: '0 0 4px 0'
                                  }}>{item.product_name}</h4>
                                  {item.variant_title && (
                                    <p style={{
                                      fontSize: '12px',
                                      color: '#6b7280',
                                      margin: '0 0 2px 0'
                                    }}>{item.variant_title}</p>
                                  )}
                                  <p style={{
                                    fontSize: '12px',
                                    color: '#6b7280',
                                    margin: '0'
                                  }}>Qty: {item.quantity}</p>
                                </div>
                              </div>

                              {/* Order ID Column */}
                              <div>
                                <p style={{
                                  fontSize: '14px',
                                  fontWeight: '500',
                                  color: '#111827',
                                  margin: '0'
                                }}>#{order.order_number}</p>
                              </div>

                              {/* Invoice ID Column */}
                              <div>
                                <p style={{
                                  fontSize: '14px',
                                  color: '#6b7280',
                                  margin: '0'
                                }}>#{order.id}</p>
                              </div>

                              {/* Status Column */}
                              <div>
                                <span style={{
                                  display: 'inline-block',
                                  padding: '6px 12px',
                                  borderRadius: '6px',
                                  fontSize: '12px',
                                  fontWeight: '500',
                                  textTransform: 'capitalize',
                                  backgroundColor: order.status === 'delivered' ? '#dcfce7' :
                                    order.status === 'pending' ? '#fef3c7' :
                                      order.status === 'processing' ? '#dbeafe' :
                                        order.status === 'shipped' ? '#e0e7ff' : '#f3f4f6',
                                  color: order.status === 'delivered' ? '#166534' :
                                    order.status === 'pending' ? '#92400e' :
                                      order.status === 'processing' ? '#1e40af' :
                                        order.status === 'shipped' ? '#3730a3' : '#374151'
                                }}>
                                  {order.status}
                                </span>
                              </div>

                              {/* Amount Column */}
                              <div>
                                <p style={{
                                  fontSize: '16px',
                                  fontWeight: '600',
                                  color: '#111827',
                                  margin: '0'
                                }}>${parseFloat(item.total_price).toFixed(2)}</p>
                                <p style={{
                                  fontSize: '12px',
                                  color: '#6b7280',
                                  margin: '0'
                                }}>${parseFloat(item.unit_price).toFixed(2)} each</p>
                              </div>

                              {/* Date Column */}
                              <div>
                                <p style={{
                                  fontSize: '14px',
                                  color: '#6b7280',
                                  margin: '0'
                                }}>
                                  {new Date(order.created_at).toLocaleDateString()}
                                </p>
                                <p style={{
                                  fontSize: '12px',
                                  color: '#9ca3af',
                                  margin: '0'
                                }}>
                                  {new Date(order.created_at).toLocaleTimeString()}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
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
              <div style={{marginBottom: '32px'}}>
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
                <div style={{padding: '24px'}}>
                  <div style={{textAlign: 'center', padding: '48px 0'}}>
                    <span style={{fontSize: '48px', color: '#9ca3af'}}>📍</span>
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
    <div style={{minHeight: '100vh', background: '#f9fafb', paddingTop: '20px'}}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        minHeight: 'calc(100vh - 20px)',
        padding: '0 20px'
      }}>
        <UserSidebar activeTab={activeTab} onTabChange={setActiveTab} />
        <div style={{flex: 1, overflow: 'hidden'}}>
          {renderContent()}
        </div>
      </div>
    </div>
  )
})

export default UserDashboard
