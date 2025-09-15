import React, { memo } from 'react'
import { useAuth } from '../../../contexts/AuthContext'

const UserSidebar = memo(({ activeTab, onTabChange }) => {
  const { user, logout } = useAuth()

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: '📊'
    },
    {
      id: 'profile',
      label: 'Profile',
      icon: '👤'
    },
    {
      id: 'addresses',
      label: 'Addresses',
      icon: '📍'
    },
    {
      id: 'orders',
      label: 'Orders',
      icon: '📦'
    }
  ]

  const handleLogout = () => {
    logout()
    window.location.href = '/'
  }

  return (
    <aside style={{
      width: '256px',
      borderRight: '1px solid #e5e7eb',
      backgroundColor: 'white',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
    }}>
      <div style={{ padding: '24px', flex: 1 }}>
        {/* Customer Navigation */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <h3 style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b7280',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: '16px'
          }}>My Account</h3>
          
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '10px 12px',
                fontSize: '14px',
                fontWeight: '500',
                borderRadius: '8px',
                width: '100%',
                textAlign: 'left',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s',
                backgroundColor: activeTab === item.id ? '#eef2ff' : 'transparent',
                color: activeTab === item.id ? '#4338ca' : '#374151',
                borderRight: activeTab === item.id ? '2px solid #6366f1' : 'none',
                boxShadow: activeTab === item.id ? '0 1px 2px rgba(0, 0, 0, 0.05)' : 'none'
              }}
              onMouseEnter={(e) => {
                if (activeTab !== item.id) {
                  e.target.style.backgroundColor = '#f9fafb'
                }
              }}
              onMouseLeave={(e) => {
                if (activeTab !== item.id) {
                  e.target.style.backgroundColor = 'transparent'
                }
              }}
            >
              <span style={{ marginRight: '12px', fontSize: '18px' }}>
                {item.icon}
              </span>
              {item.label}
            </button>
          ))}
        </nav>
      </div>
      
      {/* Logout Button */}
      <div style={{ padding: '24px', borderTop: '1px solid #e5e7eb' }}>
        <button 
          onClick={handleLogout}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '10px 12px',
            fontSize: '14px',
            fontWeight: '500',
            color: '#dc2626',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            transition: 'all 0.2s',
            backgroundColor: 'transparent'
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = '#fef2f2'
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'transparent'
          }}
        >
          <span style={{ marginRight: '12px', fontSize: '18px' }}>🚪</span>
          Logout
        </button>
      </div>
    </aside>
  )
})

export default UserSidebar
