import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useCategories } from '../contexts/CategoriesContext'

const Header = ({ onAuthClick }) => {
  const { user, isAuthenticated, logout } = useAuth()
  const { categories, subcategories, loading, getSubCategoriesForCategory } = useCategories()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  
  // Check if we're on admin dashboard
  const isAdminDashboard = window.location.pathname === '/admin-dashboard' || window.location.pathname.startsWith('/admin-dashboard/')

  return (
    <header>
      {/* Header Top */}
      <div className="header-top">
        <div className="container">
          <ul className="header-social-container">
            <li>
              <a href="#" className="social-link">
                <ion-icon name="logo-facebook"></ion-icon>
              </a>
            </li>
            <li>
              <a href="#" className="social-link">
                <ion-icon name="logo-twitter"></ion-icon>
              </a>
            </li>
            <li>
              <a href="#" className="social-link">
                <ion-icon name="logo-instagram"></ion-icon>
              </a>
            </li>
            <li>
              <a href="#" className="social-link">
                <ion-icon name="logo-linkedin"></ion-icon>
              </a>
            </li>
          </ul>


        </div>
      </div>

      {/* Header Main */}
      <div className="header-main">
        <div className="container">
          <a href="/" className="header-logo">
            <span className="logo-text">Anon</span>
          </a>

          <div className="header-search-container">
            <input type="search" name="search" className="search-field" placeholder="Enter your product name..." />
            <button className="search-btn">
              <ion-icon name="search-outline"></ion-icon>
            </button>
          </div>

              <div className="header-user-actions">
                {isAuthenticated ? (
                  <div className="user-menu">
                    <div className="user-profile-section">
                      <button 
                        className="action-btn user-profile"
                        onClick={() => {
                          console.log('User type:', user?.is_staff, user?.is_superuser) // Debug log
                          // Check if user is admin/staff and redirect accordingly
                          if (user?.is_staff || user?.is_superuser) {
                            console.log('Navigating to admin dashboard') // Debug log
                            window.location.replace('/admin-dashboard')
                          } else {
                            console.log('Navigating to user dashboard') // Debug log
                            window.location.replace('/dashboard')
                          }
                        }}
                      >
                        <ion-icon name="person-outline"></ion-icon>
                      </button>
                      <span className="user-name">{user?.full_name || user?.username}</span>
                    </div>
                    
                    <button className="action-btn logout-btn" onClick={logout}>
                      <ion-icon name="log-out-outline"></ion-icon>
                    </button>
                  </div>
                ) : (
                  <button className="action-btn" onClick={onAuthClick}>
                    <ion-icon name="person-outline"></ion-icon>
                  </button>
                )}

                {/* Hide cart and wishlist on admin dashboard */}
                {!isAdminDashboard && (
                  <>
                    <button className="action-btn">
                      <ion-icon name="heart-outline"></ion-icon>
                      <span className="count">0</span>
                    </button>

                    <button className="action-btn">
                      <ion-icon name="bag-handle-outline"></ion-icon>
                      <span className="count">0</span>
                    </button>
                  </>
                )}
              </div>
        </div>
      </div>

      {/* Desktop Navigation - Hide on admin dashboard */}
      {!isAdminDashboard && (
        <nav className="desktop-navigation-menu">
        <div className="container">
          <ul className="desktop-menu-category-list">
            <li className="menu-category">
              <a href="#" className="menu-title">Home</a>
            </li>

            <li className="menu-category">
              <a href="#" className="menu-title">Categories</a>
              <div className="dropdown-panel">
                {loading ? (
                  <div style={{ padding: '20px', textAlign: 'center' }}>
                    <p>Loading categories...</p>
                  </div>
                ) : (
                  categories.map((category, index) => {
                    const categorySubcategories = getSubCategoriesForCategory(category.slug)
                    return (
                      <ul key={category.id} className="dropdown-panel-list">
                        <li className="menu-title">
                          <a href={`/category/${category.slug}`}>{category.name}</a>
                        </li>
                        {categorySubcategories.slice(0, 5).map((subcategory) => (
                          <li key={subcategory.id} className="panel-list-item">
                            <a href={`/subcategory/${subcategory.slug}`}>{subcategory.name}</a>
                          </li>
                        ))}
                        {categorySubcategories.length > 5 && (
                          <li className="panel-list-item">
                            <a href={`/category/${category.slug}`} style={{ fontWeight: 'bold', color: '#6366f1' }}>
                              View All ({categorySubcategories.length})
                            </a>
                          </li>
                        )}
                        {index === 0 && (
                          <li className="panel-list-item">
                            
                          </li>
                        )}
                      </ul>
                    )
                  })
                )}
              </div>
            </li>

            <li className="menu-category">
              <a href="#" className="menu-title">Men's</a>
              <div className="dropdown-list">
                <ul className="dropdown-list">
                  <li className="dropdown-item">
                    <a href="#">Shirt</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Shorts & Jeans</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Safety Shoes</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Wallet</a>
                  </li>
                </ul>
              </div>
            </li>

            <li className="menu-category">
              <a href="#" className="menu-title">Women's</a>
              <div className="dropdown-list">
                <ul className="dropdown-list">
                  <li className="dropdown-item">
                    <a href="#">Dress & Frock</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Earrings</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Perfume</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Cosmetics</a>
                  </li>
                </ul>
              </div>
            </li>

            <li className="menu-category">
              <a href="#" className="menu-title">Jewelry</a>
              <div className="dropdown-list">
                <ul className="dropdown-list">
                  <li className="dropdown-item">
                    <a href="#">Earrings</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Couple Rings</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Necklace</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Bracelets</a>
                  </li>
                </ul>
              </div>
            </li>

            <li className="menu-category">
              <a href="#" className="menu-title">Perfume</a>
              <div className="dropdown-list">
                <ul className="dropdown-list">
                  <li className="dropdown-item">
                    <a href="#">Clothes Perfume</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Deodorant</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Jacket</a>
                  </li>
                  <li className="dropdown-item">
                    <a href="#">Dress & Frock</a>
                  </li>
                </ul>
              </div>
            </li>

            <li className="menu-category">
              <a href="#" className="menu-title">Blog</a>
            </li>

            <li className="menu-category">
              <a href="#" className="menu-title">Hot Offers</a>
            </li>
          </ul>
        </div>
      </nav>
      )}

      {/* Mobile Bottom Navigation - Hide on admin dashboard */}
      {!isAdminDashboard && (
        <div className="mobile-bottom-navigation">
        <button className="action-btn" data-mobile-menu-open-btn>
          <ion-icon name="menu-outline"></ion-icon>
        </button>

        <button className="action-btn">
          <ion-icon name="home-outline"></ion-icon>
        </button>

        <button className="action-btn">
          <ion-icon name="grid-outline"></ion-icon>
        </button>

        <button className="action-btn">
          <ion-icon name="heart-outline"></ion-icon>
          <span className="count">0</span>
        </button>

        <button className="action-btn">
          <ion-icon name="bag-handle-outline"></ion-icon>
          <span className="count">0</span>
        </button>
      </div>
      )}

      {/* Mobile Navigation Menu */}
      <nav className="mobile-navigation-menu" data-mobile-menu>
        <div className="menu-top">
          <h2 className="menu-title">My Menu</h2>
          <button className="menu-close-btn" data-mobile-menu-close-btn>
            <ion-icon name="close-outline"></ion-icon>
          </button>
        </div>

        <ul className="mobile-menu-category-list">
          {loading ? (
            <li className="menu-category">
              <div style={{ padding: '20px', textAlign: 'center' }}>
                <p>Loading categories...</p>
              </div>
            </li>
          ) : (
            categories.map((category) => {
              const categorySubcategories = getSubCategoriesForCategory(category.slug)
              return (
                <li key={category.id} className="menu-category">
                  <button className="accordion-menu" data-accordion-btn>
                    <p className="menu-title">{category.name}</p>
                    <div>
                      <ion-icon name="add-outline" className="add-icon"></ion-icon>
                      <ion-icon name="remove-outline" className="remove-icon"></ion-icon>
                    </div>
                  </button>

                  <ul className="submenu-category-list" data-accordion>
                    {categorySubcategories.map((subcategory) => (
                      <li key={subcategory.id} className="submenu-category">
                        <a href={`/subcategory/${subcategory.slug}`} className="submenu-title">
                          {subcategory.name}
                        </a>
                      </li>
                    ))}
                    {categorySubcategories.length === 0 && (
                      <li className="submenu-category">
                        <span className="submenu-title" style={{ color: '#9ca3af' }}>
                          No subcategories available
                        </span>
                      </li>
                    )}
                  </ul>
                </li>
              )
            })
          )}
        </ul>

        <div className="menu-bottom">
          <ul className="menu-category-list">
            <li className="menu-category">
              <button className="accordion-menu" data-accordion-btn>
                <p className="menu-title">Language</p>
                <ion-icon name="caret-back" className="caret-back"></ion-icon>
              </button>

              <ul className="submenu-category-list" data-accordion>
                <li className="submenu-category">
                  <a href="#" className="submenu-title">English</a>
                </li>
                <li className="submenu-category">
                  <a href="#" className="submenu-title">Español</a>
                </li>
                <li className="submenu-category">
                  <a href="#" className="submenu-title">Français</a>
                </li>
              </ul>
            </li>

            <li className="menu-category">
              <button className="accordion-menu" data-accordion-btn>
                <p className="menu-title">Currency</p>
                <ion-icon name="caret-back" className="caret-back"></ion-icon>
              </button>

              <ul className="submenu-category-list" data-accordion>
                <li className="submenu-category">
                  <a href="#" className="submenu-title">USD &dollar;</a>
                </li>
                <li className="submenu-category">
                  <a href="#" className="submenu-title">EUR &euro;</a>
                </li>
              </ul>
            </li>
          </ul>

          <ul className="menu-social-container">
            <li>
              <a href="#" className="social-link">
                <ion-icon name="logo-facebook"></ion-icon>
              </a>
            </li>
            <li>
              <a href="#" className="social-link">
                <ion-icon name="logo-twitter"></ion-icon>
              </a>
            </li>
            <li>
              <a href="#" className="social-link">
                <ion-icon name="logo-instagram"></ion-icon>
              </a>
            </li>
            <li>
              <a href="#" className="social-link">
                <ion-icon name="logo-linkedin"></ion-icon>
              </a>
            </li>
          </ul>
        </div>
      </nav>
    </header>
  )
}

export default Header
