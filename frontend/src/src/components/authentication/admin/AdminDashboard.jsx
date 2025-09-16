import React, { useState, memo } from 'react'
import { useAuth } from '../../../contexts/AuthContext'
import AdminSidebar from './AdminSidebar'
import CategoryManagement from './CategoryManagement'
import SubCategoryManagement from './SubCategoryManagement'
import ProductManagement from './ProductManagement'

const AdminDashboard = memo(() => {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('dashboard')

  // Redirect to home if not admin
  if (!user || (!user.is_staff && !user.is_superuser)) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: '#f6f7f9', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        <div style={{
          background: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          border: '1px solid #e1e3e5',
          padding: '48px',
          textAlign: 'center',
          maxWidth: '400px'
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            background: '#fef2f2',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px'
          }}>
            <span style={{ fontSize: '24px' }}>🚫</span>
          </div>
          <h2 style={{ 
            fontSize: '24px', 
            fontWeight: '600', 
            color: '#dc2626',
            margin: '0 0 16px 0'
          }}>Access Denied</h2>
          <p style={{ 
            fontSize: '16px', 
            color: '#637381',
            margin: '0 0 24px 0'
          }}>You don't have admin privileges to access this page.</p>
          <button 
            onClick={() => window.location.href = '/'}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '500',
              color: 'white',
              background: '#5c6ac4',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = '#4c51bf'
            }}
            onMouseLeave={(e) => {
              e.target.style.background = '#5c6ac4'
            }}
          >
            Go to Home
          </button>
        </div>
      </div>
    )
  }

  // Sample data for charts (in real app, this would come from API)
  const sampleData = {
    salesData: [120, 190, 300, 500, 200, 300, 450, 600, 400, 350, 280, 320],
    orderData: [5, 8, 12, 15, 10, 18, 22, 25, 20, 16, 14, 19],
    customerData: [10, 15, 25, 35, 30, 45, 55, 65, 50, 40, 35, 42]
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div style={{ 
            background: 'transparent', 
            minHeight: 'calc(100vh - 20px)'
          }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
              
              {/* Page Header - Shopify Style */}
              <div style={{ marginBottom: '32px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <h1 style={{ 
                      fontSize: '32px', 
                      fontWeight: '600', 
                      color: '#212b36',
                      margin: '0 0 8px 0',
                      letterSpacing: '-0.025em'
                    }}>Dashboard</h1>
                    <p style={{ 
                      fontSize: '16px', 
                      color: '#637381',
                      margin: '0'
                    }}>
                      Welcome back, {user?.full_name || user?.username}. Here's what's happening with your store today.
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <button style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '10px 16px',
                      border: '1px solid #e1e3e5',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#212b36',
                      background: 'white',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = '#f6f7f9'
                      e.target.style.borderColor = '#5c6ac4'
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'white'
                      e.target.style.borderColor = '#e1e3e5'
                    }}
                    >
                      <span style={{ marginRight: '8px' }}>📊</span>
                      Export
                    </button>
                    <button style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '10px 16px',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: 'white',
                      background: '#5c6ac4',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = '#4c51bf'
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = '#5c6ac4'
                    }}
                    >
                      <span style={{ marginRight: '8px' }}>⚙️</span>
                      Settings
                    </button>
                  </div>
                </div>
              </div>

              {/* Statistics Cards - Enhanced Shopify Style */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '24px',
                marginBottom: '32px'
              }}>
                {/* Total Sales */}
                <div style={{
                  background: 'white',
                  borderRadius: '12px',
                  border: '1px solid #e1e3e5',
                  padding: '24px',
                  position: 'relative',
                  overflow: 'hidden',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: '0',
                    right: '0',
                    width: '120px',
                    height: '120px',
                    background: 'linear-gradient(135deg, #008060 0%, #00a86b 100%)',
                    borderRadius: '0 12px 0 120px',
                    opacity: '0.1'
                  }}></div>
                  <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #008060 0%, #00a86b 100%)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{ color: 'white', fontSize: '20px' }}>💰</span>
                      </div>
                      <div style={{
                        padding: '4px 8px',
                        background: '#f0fdf4',
                        borderRadius: '6px',
                        border: '1px solid #bbf7d0'
                      }}>
                        <span style={{ 
                          fontSize: '12px', 
                          color: '#008060',
                          fontWeight: '600'
                        }}>+12.5%</span>
                      </div>
                    </div>
                    <div>
                      <p style={{ 
                        fontSize: '14px', 
                        fontWeight: '500', 
                        color: '#637381',
                        margin: '0 0 4px 0'
                      }}>Total Sales</p>
                      <p style={{ 
                        fontSize: '28px', 
                        fontWeight: '700', 
                        color: '#212b36',
                        margin: '0 0 8px 0'
                      }}>$24,580</p>
                      <p style={{ 
                        fontSize: '12px', 
                        color: '#637381',
                        margin: '0'
                      }}>vs $21,840 last month</p>
                    </div>
                  </div>
                </div>

                {/* Total Orders */}
                <div style={{
                  background: 'white',
                  borderRadius: '12px',
                  border: '1px solid #e1e3e5',
                  padding: '24px',
                  position: 'relative',
                  overflow: 'hidden',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: '0',
                    right: '0',
                    width: '120px',
                    height: '120px',
                    background: 'linear-gradient(135deg, #5c6ac4 0%, #7c3aed 100%)',
                    borderRadius: '0 12px 0 120px',
                    opacity: '0.1'
                  }}></div>
                  <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #5c6ac4 0%, #7c3aed 100%)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{ color: 'white', fontSize: '20px' }}>📦</span>
                      </div>
                      <div style={{
                        padding: '4px 8px',
                        background: '#f0f4ff',
                        borderRadius: '6px',
                        border: '1px solid #c7d2fe'
                      }}>
                        <span style={{ 
                          fontSize: '12px', 
                          color: '#5c6ac4',
                          fontWeight: '600'
                        }}>+8.2%</span>
                      </div>
                    </div>
                    <div>
                      <p style={{ 
                        fontSize: '14px', 
                        fontWeight: '500', 
                        color: '#637381',
                        margin: '0 0 4px 0'
                      }}>Total Orders</p>
                      <p style={{ 
                        fontSize: '28px', 
                        fontWeight: '700', 
                        color: '#212b36',
                        margin: '0 0 8px 0'
                      }}>1,247</p>
                      <p style={{ 
                        fontSize: '12px', 
                        color: '#637381',
                        margin: '0'
                      }}>vs 1,152 last month</p>
                    </div>
                  </div>
                </div>

                {/* Total Customers */}
                <div style={{
                  background: 'white',
                  borderRadius: '12px',
                  border: '1px solid #e1e3e5',
                  padding: '24px',
                  position: 'relative',
                  overflow: 'hidden',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: '0',
                    right: '0',
                    width: '120px',
                    height: '120px',
                    background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                    borderRadius: '0 12px 0 120px',
                    opacity: '0.1'
                  }}></div>
                  <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{ color: 'white', fontSize: '20px' }}>👥</span>
                      </div>
                      <div style={{
                        padding: '4px 8px',
                        background: '#fffbeb',
                        borderRadius: '6px',
                        border: '1px solid #fed7aa'
                      }}>
                        <span style={{ 
                          fontSize: '12px', 
                          color: '#f59e0b',
                          fontWeight: '600'
                        }}>+15.3%</span>
                      </div>
                    </div>
                    <div>
                      <p style={{ 
                        fontSize: '14px', 
                        fontWeight: '500', 
                        color: '#637381',
                        margin: '0 0 4px 0'
                      }}>Total Customers</p>
                      <p style={{ 
                        fontSize: '28px', 
                        fontWeight: '700', 
                        color: '#212b36',
                        margin: '0 0 8px 0'
                      }}>3,842</p>
                      <p style={{ 
                        fontSize: '12px', 
                        color: '#637381',
                        margin: '0'
                      }}>vs 3,331 last month</p>
                    </div>
                  </div>
                </div>

                {/* Total Products */}
                <div style={{
                  background: 'white',
                  borderRadius: '12px',
                  border: '1px solid #e1e3e5',
                  padding: '24px',
                  position: 'relative',
                  overflow: 'hidden',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: '0',
                    right: '0',
                    width: '120px',
                    height: '120px',
                    background: 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
                    borderRadius: '0 12px 0 120px',
                    opacity: '0.1'
                  }}></div>
                  <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{ color: 'white', fontSize: '20px' }}>📋</span>
                      </div>
                      <div style={{
                        padding: '4px 8px',
                        background: '#fef2f2',
                        borderRadius: '6px',
                        border: '1px solid #fecaca'
                      }}>
                        <span style={{ 
                          fontSize: '12px', 
                          color: '#dc2626',
                          fontWeight: '600'
                        }}>+5.7%</span>
                      </div>
                    </div>
                    <div>
                      <p style={{ 
                        fontSize: '14px', 
                        fontWeight: '500', 
                        color: '#637381',
                        margin: '0 0 4px 0'
                      }}>Total Products</p>
                      <p style={{ 
                        fontSize: '28px', 
                        fontWeight: '700', 
                        color: '#212b36',
                        margin: '0 0 8px 0'
                      }}>156</p>
                      <p style={{ 
                        fontSize: '12px', 
                        color: '#637381',
                        margin: '0'
                      }}>vs 148 last month</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Charts Section */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '2fr 1fr',
                gap: '24px',
                marginBottom: '32px'
              }}>
                {/* Sales Chart */}
                <div style={{
                  background: 'white',
                  borderRadius: '12px',
                  border: '1px solid #e1e3e5',
                  overflow: 'hidden',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  <div style={{
                    padding: '24px',
                    borderBottom: '1px solid #e1e3e5',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}>
                    <div>
                      <h3 style={{ 
                        fontSize: '18px', 
                        fontWeight: '600', 
                        color: '#212b36',
                        margin: '0 0 4px 0'
                      }}>Sales Analytics</h3>
                      <p style={{ 
                        fontSize: '14px', 
                        color: '#637381',
                        margin: '0'
                      }}>Monthly sales performance</p>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button style={{
                        padding: '6px 12px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: '500',
                        color: '#212b36',
                        background: 'white',
                        cursor: 'pointer'
                      }}>7D</button>
                      <button style={{
                        padding: '6px 12px',
                        border: '1px solid #5c6ac4',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: '500',
                        color: 'white',
                        background: '#5c6ac4',
                        cursor: 'pointer'
                      }}>30D</button>
                      <button style={{
                        padding: '6px 12px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: '500',
                        color: '#212b36',
                        background: 'white',
                        cursor: 'pointer'
                      }}>90D</button>
                    </div>
                  </div>
                  <div style={{ padding: '24px', height: '300px' }}>
                    {/* Simple Chart Visualization */}
                    <div style={{ 
                      height: '100%', 
                      display: 'flex', 
                      alignItems: 'end', 
                      justifyContent: 'space-between',
                      padding: '20px 0'
                    }}>
                      {sampleData.salesData.map((value, index) => (
                        <div key={index} style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          flex: 1,
                          margin: '0 2px'
                        }}>
                          <div style={{
                            width: '100%',
                            height: `${(value / 600) * 200}px`,
                            background: 'linear-gradient(135deg, #5c6ac4 0%, #7c3aed 100%)',
                            borderRadius: '4px 4px 0 0',
                            marginBottom: '8px',
                            minHeight: '4px'
                          }}></div>
                          <span style={{
                            fontSize: '10px',
                            color: '#637381',
                            fontWeight: '500'
                          }}>{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][index]}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Quick Actions */}
                <div style={{
                  background: 'white',
                  borderRadius: '12px',
                  border: '1px solid #e1e3e5',
                  overflow: 'hidden',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  <div style={{
                    padding: '24px',
                    borderBottom: '1px solid #e1e3e5'
                  }}>
                    <h3 style={{ 
                      fontSize: '18px', 
                      fontWeight: '600', 
                      color: '#212b36',
                      margin: '0 0 4px 0'
                    }}>Quick Actions</h3>
                    <p style={{ 
                      fontSize: '14px', 
                      color: '#637381',
                      margin: '0'
                    }}>Manage your store</p>
                  </div>
                  <div style={{ padding: '24px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <button 
                        onClick={() => setActiveTab('products')}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          padding: '16px',
                          border: '1px solid #e1e3e5',
                          borderRadius: '8px',
                          fontSize: '14px',
                          fontWeight: '500',
                          color: '#212b36',
                          background: 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          textAlign: 'left'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.background = '#f6f7f9'
                          e.target.style.borderColor = '#5c6ac4'
                          e.target.style.transform = 'translateY(-1px)'
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.background = 'white'
                          e.target.style.borderColor = '#e1e3e5'
                          e.target.style.transform = 'translateY(0)'
                        }}
                      >
                        <div style={{
                          width: '40px',
                          height: '40px',
                          background: 'linear-gradient(135deg, #5c6ac4 0%, #7c3aed 100%)',
                          borderRadius: '8px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginRight: '12px'
                        }}>
                          <span style={{ color: 'white', fontSize: '16px' }}>📦</span>
                        </div>
                        <div>
                          <p style={{ margin: '0 0 2px 0', fontWeight: '600' }}>Add Product</p>
                          <p style={{ margin: '0', fontSize: '12px', color: '#637381' }}>Create new product</p>
                        </div>
                      </button>
                      <button 
                        onClick={() => setActiveTab('categories')}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          padding: '16px',
                          border: '1px solid #e1e3e5',
                          borderRadius: '8px',
                          fontSize: '14px',
                          fontWeight: '500',
                          color: '#212b36',
                          background: 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          textAlign: 'left'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.background = '#f6f7f9'
                          e.target.style.borderColor = '#5c6ac4'
                          e.target.style.transform = 'translateY(-1px)'
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.background = 'white'
                          e.target.style.borderColor = '#e1e3e5'
                          e.target.style.transform = 'translateY(0)'
                        }}
                      >
                        <div style={{
                          width: '40px',
                          height: '40px',
                          background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                          borderRadius: '8px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginRight: '12px'
                        }}>
                          <span style={{ color: 'white', fontSize: '16px' }}>📂</span>
                        </div>
                        <div>
                          <p style={{ margin: '0 0 2px 0', fontWeight: '600' }}>Manage Categories</p>
                          <p style={{ margin: '0', fontSize: '12px', color: '#637381' }}>Organize products</p>
                        </div>
                      </button>
                      <button 
                        onClick={() => setActiveTab('orders')}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          padding: '16px',
                          border: '1px solid #e1e3e5',
                          borderRadius: '8px',
                          fontSize: '14px',
                          fontWeight: '500',
                          color: '#212b36',
                          background: 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          textAlign: 'left'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.background = '#f6f7f9'
                          e.target.style.borderColor = '#5c6ac4'
                          e.target.style.transform = 'translateY(-1px)'
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.background = 'white'
                          e.target.style.borderColor = '#e1e3e5'
                          e.target.style.transform = 'translateY(0)'
                        }}
                      >
                        <div style={{
                          width: '40px',
                          height: '40px',
                          background: 'linear-gradient(135deg, #008060 0%, #00a86b 100%)',
                          borderRadius: '8px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginRight: '12px'
                        }}>
                          <span style={{ color: 'white', fontSize: '16px' }}>📋</span>
                        </div>
                        <div>
                          <p style={{ margin: '0 0 2px 0', fontWeight: '600' }}>View Orders</p>
                          <p style={{ margin: '0', fontSize: '12px', color: '#637381' }}>Manage orders</p>
                        </div>
                      </button>
                      <button 
                        onClick={() => window.open('http://127.0.0.1:8000/admin/', '_blank')}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          padding: '16px',
                          border: '1px solid #e1e3e5',
                          borderRadius: '8px',
                          fontSize: '14px',
                          fontWeight: '500',
                          color: '#212b36',
                          background: 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          textAlign: 'left'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.background = '#f6f7f9'
                          e.target.style.borderColor = '#5c6ac4'
                          e.target.style.transform = 'translateY(-1px)'
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.background = 'white'
                          e.target.style.borderColor = '#e1e3e5'
                          e.target.style.transform = 'translateY(0)'
                        }}
                      >
                        <div style={{
                          width: '40px',
                          height: '40px',
                          background: 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
                          borderRadius: '8px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginRight: '12px'
                        }}>
                          <span style={{ color: 'white', fontSize: '16px' }}>⚙️</span>
                        </div>
                        <div>
                          <p style={{ margin: '0 0 2px 0', fontWeight: '600' }}>Django Admin</p>
                          <p style={{ margin: '0', fontSize: '12px', color: '#637381' }}>Advanced settings</p>
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Orders & Analytics */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '24px',
                marginBottom: '32px'
              }}>
                {/* Recent Orders */}
                <div style={{
                  background: 'white',
                  borderRadius: '12px',
                  border: '1px solid #e1e3e5',
                  overflow: 'hidden',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  <div style={{
                    padding: '24px',
                    borderBottom: '1px solid #e1e3e5',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}>
                    <div>
                      <h3 style={{ 
                        fontSize: '18px', 
                        fontWeight: '600', 
                        color: '#212b36',
                        margin: '0 0 4px 0'
                      }}>Recent Orders</h3>
                      <p style={{ 
                        fontSize: '14px', 
                        color: '#637381',
                        margin: '0'
                      }}>Latest customer orders</p>
                    </div>
                    <button style={{
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#5c6ac4',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '8px 12px',
                      borderRadius: '6px'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = '#f6f7f9'
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'none'
                    }}
                    >
                      View all
                    </button>
                  </div>
                  <div style={{ padding: '24px' }}>
                    {/* Sample Orders */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {[
                        { id: '#1001', customer: 'John Doe', amount: '$89.99', status: 'Completed', time: '2 hours ago' },
                        { id: '#1002', customer: 'Jane Smith', amount: '$156.50', status: 'Processing', time: '4 hours ago' },
                        { id: '#1003', customer: 'Mike Johnson', amount: '$45.00', status: 'Shipped', time: '6 hours ago' },
                        { id: '#1004', customer: 'Sarah Wilson', amount: '$234.75', status: 'Pending', time: '8 hours ago' }
                      ].map((order, index) => (
                        <div key={index} style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '16px',
                          border: '1px solid #f3f4f6',
                          borderRadius: '8px',
                          background: '#fafbfc'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center' }}>
                            <div style={{
                              width: '40px',
                              height: '40px',
                              background: 'linear-gradient(135deg, #5c6ac4 0%, #7c3aed 100%)',
                              borderRadius: '8px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              marginRight: '12px'
                            }}>
                              <span style={{ color: 'white', fontSize: '14px', fontWeight: '600' }}>#{order.id.slice(1)}</span>
                            </div>
                            <div>
                              <p style={{ margin: '0 0 2px 0', fontSize: '14px', fontWeight: '600', color: '#212b36' }}>
                                {order.customer}
                              </p>
                              <p style={{ margin: '0', fontSize: '12px', color: '#637381' }}>
                                {order.time}
                              </p>
                            </div>
                          </div>
                          <div style={{ textAlign: 'right' }}>
                            <p style={{ margin: '0 0 2px 0', fontSize: '14px', fontWeight: '600', color: '#212b36' }}>
                              {order.amount}
                            </p>
                            <span style={{
                              padding: '2px 8px',
                              borderRadius: '4px',
                              fontSize: '10px',
                              fontWeight: '500',
                              background: order.status === 'Completed' ? '#f0fdf4' : 
                                         order.status === 'Processing' ? '#fef3c7' :
                                         order.status === 'Shipped' ? '#dbeafe' : '#f3f4f6',
                              color: order.status === 'Completed' ? '#008060' : 
                                     order.status === 'Processing' ? '#f59e0b' :
                                     order.status === 'Shipped' ? '#3b82f6' : '#6b7280'
                            }}>
                              {order.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Top Products */}
                <div style={{
                  background: 'white',
                  borderRadius: '12px',
                  border: '1px solid #e1e3e5',
                  overflow: 'hidden',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  <div style={{
                    padding: '24px',
                    borderBottom: '1px solid #e1e3e5'
                  }}>
                    <h3 style={{ 
                      fontSize: '18px', 
                      fontWeight: '600', 
                      color: '#212b36',
                      margin: '0 0 4px 0'
                    }}>Top Products</h3>
                    <p style={{ 
                      fontSize: '14px', 
                      color: '#637381',
                      margin: '0'
                    }}>Best selling items</p>
                  </div>
                  <div style={{ padding: '24px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {[
                        { name: 'Wireless Headphones', sales: 45, revenue: '$2,250' },
                        { name: 'Smart Watch', sales: 32, revenue: '$1,920' },
                        { name: 'Laptop Stand', sales: 28, revenue: '$420' },
                        { name: 'Phone Case', sales: 67, revenue: '$335' }
                      ].map((product, index) => (
                        <div key={index} style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '12px 16px',
                          border: '1px solid #f3f4f6',
                          borderRadius: '8px',
                          background: '#fafbfc'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center' }}>
                            <div style={{
                              width: '32px',
                              height: '32px',
                              background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                              borderRadius: '6px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              marginRight: '12px'
                            }}>
                              <span style={{ color: 'white', fontSize: '12px' }}>📦</span>
                            </div>
                            <div>
                              <p style={{ margin: '0 0 2px 0', fontSize: '14px', fontWeight: '500', color: '#212b36' }}>
                                {product.name}
                              </p>
                              <p style={{ margin: '0', fontSize: '12px', color: '#637381' }}>
                                {product.sales} sales
                              </p>
                            </div>
                          </div>
                          <div style={{ textAlign: 'right' }}>
                            <p style={{ margin: '0', fontSize: '14px', fontWeight: '600', color: '#212b36' }}>
                              {product.revenue}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        )
      case 'categories':
        return <CategoryManagement />
      case 'subcategories':
        return <SubCategoryManagement />
      case 'products':
        return <ProductManagement />
      case 'orders':
        return (
          <div style={{ 
            background: 'transparent', 
            minHeight: 'calc(100vh - 20px)'
          }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
              <h1 style={{ 
                fontSize: '32px', 
                fontWeight: '600', 
                color: '#212b36',
                margin: '0 0 32px 0'
              }}>Order Management</h1>
              <div style={{
                background: 'white',
                borderRadius: '12px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e1e3e5',
                padding: '48px',
                textAlign: 'center'
              }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'linear-gradient(135deg, #5c6ac4 0%, #7c3aed 100%)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 24px'
                }}>
                  <span style={{ fontSize: '32px', color: 'white' }}>📋</span>
                </div>
                <h2 style={{ 
                  fontSize: '24px', 
                  fontWeight: '600', 
                  color: '#212b36',
                  margin: '0 0 12px 0'
                }}>Order Management</h2>
                <p style={{ 
                  fontSize: '16px', 
                  color: '#637381',
                  margin: '0 0 24px 0'
                }}>Advanced order management interface coming soon...</p>
                <button style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '12px 24px',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: 'white',
                  background: '#5c6ac4',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = '#4c51bf'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = '#5c6ac4'
                }}
                >
                  <span style={{ marginRight: '8px' }}>📊</span>
                  View Analytics
                </button>
              </div>
            </div>
          </div>
        )
      case 'customers':
        return (
          <div style={{ 
            background: 'transparent', 
            minHeight: 'calc(100vh - 20px)'
          }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
              <h1 style={{ 
                fontSize: '32px', 
                fontWeight: '600', 
                color: '#212b36',
                margin: '0 0 32px 0'
              }}>Customer Management</h1>
              <div style={{
                background: 'white',
                borderRadius: '12px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e1e3e5',
                padding: '48px',
                textAlign: 'center'
              }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 24px'
                }}>
                  <span style={{ fontSize: '32px', color: 'white' }}>👥</span>
                </div>
                <h2 style={{ 
                  fontSize: '24px', 
                  fontWeight: '600', 
                  color: '#212b36',
                  margin: '0 0 12px 0'
                }}>Customer Management</h2>
                <p style={{ 
                  fontSize: '16px', 
                  color: '#637381',
                  margin: '0 0 24px 0'
                }}>Customer database and management interface coming soon...</p>
                <button style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '12px 24px',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: 'white',
                  background: '#f59e0b',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = '#d97706'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = '#f59e0b'
                }}
                >
                  <span style={{ marginRight: '8px' }}>👥</span>
                  View Customers
                </button>
              </div>
            </div>
          </div>
        )
      case 'analytics':
        return (
          <div style={{ 
            background: 'transparent', 
            minHeight: 'calc(100vh - 20px)'
          }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
              <h1 style={{ 
                fontSize: '32px', 
                fontWeight: '600', 
                color: '#212b36',
                margin: '0 0 32px 0'
              }}>Analytics & Reports</h1>
              <div style={{
                background: 'white',
                borderRadius: '12px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e1e3e5',
                padding: '48px',
                textAlign: 'center'
              }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'linear-gradient(135deg, #008060 0%, #00a86b 100%)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 24px'
                }}>
                  <span style={{ fontSize: '32px', color: 'white' }}>📈</span>
                </div>
                <h2 style={{ 
                  fontSize: '24px', 
                  fontWeight: '600', 
                  color: '#212b36',
                  margin: '0 0 12px 0'
                }}>Analytics Dashboard</h2>
                <p style={{ 
                  fontSize: '16px', 
                  color: '#637381',
                  margin: '0 0 24px 0'
                }}>Advanced analytics and reporting interface coming soon...</p>
                <button style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '12px 24px',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: 'white',
                  background: '#008060',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = '#006b4d'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = '#008060'
                }}
                >
                  <span style={{ marginRight: '8px' }}>📊</span>
                  Generate Report
                </button>
              </div>
            </div>
          </div>
        )
      case 'inventory':
        return (
          <div style={{ 
            background: 'transparent', 
            minHeight: 'calc(100vh - 20px)'
          }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
              <h1 style={{ 
                fontSize: '32px', 
                fontWeight: '600', 
                color: '#212b36',
                margin: '0 0 32px 0'
              }}>Inventory Management</h1>
              <div style={{
                background: 'white',
                borderRadius: '12px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e1e3e5',
                padding: '48px',
                textAlign: 'center'
              }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 24px'
                }}>
                  <span style={{ fontSize: '32px', color: 'white' }}>📊</span>
                </div>
                <h2 style={{ 
                  fontSize: '24px', 
                  fontWeight: '600', 
                  color: '#212b36',
                  margin: '0 0 12px 0'
                }}>Stock Management</h2>
                <p style={{ 
                  fontSize: '16px', 
                  color: '#637381',
                  margin: '0 0 24px 0'
                }}>Inventory tracking and stock management interface coming soon...</p>
                <button style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '12px 24px',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: 'white',
                  background: '#dc2626',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = '#b91c1c'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = '#dc2626'
                }}
                >
                  <span style={{ marginRight: '8px' }}>📦</span>
                  View Inventory
                </button>
              </div>
            </div>
          </div>
        )
      case 'settings':
        return (
          <div style={{ 
            background: 'transparent', 
            minHeight: 'calc(100vh - 20px)'
          }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
              <h1 style={{ 
                fontSize: '32px', 
                fontWeight: '600', 
                color: '#212b36',
                margin: '0 0 32px 0'
              }}>Store Settings</h1>
              <div style={{
                background: 'white',
                borderRadius: '12px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e1e3e5',
                padding: '48px',
                textAlign: 'center'
              }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'linear-gradient(135deg, #6b7280 0%, #9ca3af 100%)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 24px'
                }}>
                  <span style={{ fontSize: '32px', color: 'white' }}>⚙️</span>
                </div>
                <h2 style={{ 
                  fontSize: '24px', 
                  fontWeight: '600', 
                  color: '#212b36',
                  margin: '0 0 12px 0'
                }}>Store Configuration</h2>
                <p style={{ 
                  fontSize: '16px', 
                  color: '#637381',
                  margin: '0 0 24px 0'
                }}>Store settings and configuration interface coming soon...</p>
                <button style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '12px 24px',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: 'white',
                  background: '#6b7280',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = '#4b5563'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = '#6b7280'
                }}
                >
                  <span style={{ marginRight: '8px' }}>⚙️</span>
                  Configure Store
                </button>
              </div>
            </div>
          </div>
        )
      default:
        return renderContent()
    }
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: '#f6f7f9',
      display: 'flex',
      paddingTop: '20px' // Add padding for header gap
    }}>
      <AdminSidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <div style={{ 
        flex: 1, 
        padding: '32px',
        overflow: 'auto'
      }}>
        {renderContent()}
      </div>
    </div>
  )
})

export default AdminDashboard
