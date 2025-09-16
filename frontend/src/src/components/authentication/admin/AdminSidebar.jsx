import React, { memo } from 'react'
import { useAuth } from '../../../contexts/AuthContext'

const AdminSidebar = memo(({ activeTab, onTabChange }) => {
  const { user, logout } = useAuth()

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: '📊',
      description: 'Overview & Analytics'
    },
    {
      id: 'products',
      label: 'Products',
      icon: '📦',
      description: 'Manage Products'
    },
    {
      id: 'categories',
      label: 'Categories',
      icon: '📂',
      description: 'Product Categories'
    },
    {
      id: 'subcategories',
      label: 'SubCategories',
      icon: '📁',
      description: 'Product SubCategories'
    },
    {
      id: 'orders',
      label: 'Orders',
      icon: '📋',
      description: 'Order Management'
    },
    {
      id: 'customers',
      label: 'Customers',
      icon: '👥',
      description: 'Customer Management'
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: '📈',
      description: 'Sales Reports'
    },
    {
      id: 'inventory',
      label: 'Inventory',
      icon: '📊',
      description: 'Stock Management'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: '⚙️',
      description: 'Store Settings'
    }
  ]

  const handleLogout = () => {
    logout()
    window.location.href = '/'
  }

  return (
    <aside style={{
      width: '300px',
      borderRight: '1px solid #e1e3e5',
      backgroundColor: '#f6f7f9', // Match dashboard background
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      boxShadow: '2px 0 8px rgba(0, 0, 0, 0.1)',
      position: 'relative' // Change from fixed to relative
    }}>
      <div style={{ padding: '24px', flex: 1, overflow: 'auto' }}>
        {/* Admin Header - Enhanced Shopify Style */}
        <div style={{ marginBottom: '32px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            padding: '20px',
            background: 'linear-gradient(135deg, #5c6ac4 0%, #7c3aed 100%)',
            borderRadius: '12px',
            color: 'white',
            boxShadow: '0 4px 12px rgba(92, 106, 196, 0.3)'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '16px'
            }}>
              <span style={{ fontSize: '20px' }}>👑</span>
            </div>
            <div>
              <p style={{
                fontSize: '12px',
                fontWeight: '600',
                color: 'rgba(255, 255, 255, 0.8)',
                margin: '0 0 4px 0',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Admin Panel</p>
              <p style={{
                fontSize: '16px',
                fontWeight: '600',
                color: 'white',
                margin: '0 0 2px 0'
              }}>{user?.full_name || user?.username}</p>
              <p style={{
                fontSize: '12px',
                color: 'rgba(255, 255, 255, 0.7)',
                margin: '0'
              }}>Store Administrator</p>
            </div>
          </div>
        </div>

        {/* Admin Navigation - Enhanced Shopify Style */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <h3 style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#637381',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: '16px',
            paddingLeft: '4px'
          }}>Store Management</h3>
          
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '16px',
                fontSize: '14px',
                fontWeight: '500',
                borderRadius: '8px',
                width: '100%',
                textAlign: 'left',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s',
                backgroundColor: activeTab === item.id ? '#5c6ac4' : 'transparent',
                color: activeTab === item.id ? 'white' : '#212b36',
                boxShadow: activeTab === item.id ? '0 2px 8px rgba(92, 106, 196, 0.3)' : 'none',
                marginBottom: '2px'
              }}
              onMouseEnter={(e) => {
                if (activeTab !== item.id) {
                  e.target.style.backgroundColor = 'rgba(92, 106, 196, 0.1)'
                  e.target.style.transform = 'translateX(4px)'
                }
              }}
              onMouseLeave={(e) => {
                if (activeTab !== item.id) {
                  e.target.style.backgroundColor = 'transparent'
                  e.target.style.transform = 'translateX(0)'
                }
              }}
            >
              <div style={{
                width: '32px',
                height: '32px',
                background: activeTab === item.id ? 'rgba(255, 255, 255, 0.2)' : 'rgba(92, 106, 196, 0.1)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '12px'
              }}>
                <span style={{ fontSize: '16px' }}>
                  {item.icon}
                </span>
              </div>
              <div>
                <p style={{ 
                  margin: '0 0 2px 0', 
                  fontSize: '14px', 
                  fontWeight: '600' 
                }}>
                  {item.label}
                </p>
                <p style={{ 
                  margin: '0', 
                  fontSize: '11px', 
                  opacity: 0.7 
                }}>
                  {item.description}
                </p>
              </div>
            </button>
          ))}
        </nav>
      </div>
      
      {/* Logout Button - Enhanced Shopify Style */}
      <div style={{ padding: '24px', borderTop: '1px solid #e1e3e5' }}>
        <button 
          onClick={handleLogout}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '16px',
            fontSize: '14px',
            fontWeight: '600',
            color: '#dc2626',
            borderRadius: '8px',
            border: '1px solid #fecaca',
            cursor: 'pointer',
            transition: 'all 0.2s',
            backgroundColor: 'transparent'
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = '#fef2f2'
            e.target.style.borderColor = '#dc2626'
            e.target.style.transform = 'translateY(-1px)'
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'transparent'
            e.target.style.borderColor = '#fecaca'
            e.target.style.transform = 'translateY(0)'
          }}
        >
          <div style={{
            width: '32px',
            height: '32px',
            background: '#fef2f2',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginRight: '12px'
          }}>
            <span style={{ fontSize: '16px' }}>🚪</span>
          </div>
          Logout
        </button>
      </div>
    </aside>
  )
})

export default AdminSidebar
