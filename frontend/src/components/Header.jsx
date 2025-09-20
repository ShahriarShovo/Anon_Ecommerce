import React, {useState, useEffect} from 'react'
import {useAuth} from '../contexts/AuthContext'
import {useCategories} from '../contexts/CategoriesContext'
import apiService from '../services/api'

const Header = ({onAuthClick}) => {
  const {user, isAuthenticated, logout} = useAuth()
  const {categories, subcategories, loading, getSubCategoriesForCategory} = useCategories()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [cartCount, setCartCount] = useState(0)

  // Check if we're on admin dashboard
  const isAdminDashboard = window.location.pathname === '/admin-dashboard' || window.location.pathname.startsWith('/admin-dashboard/')

  // Fetch cart count
  const fetchCartCount = async () => {
    try {
      // Check if cart was cleared or order completed (sessionStorage count is 0)
      const storedCount = sessionStorage.getItem('cartCount')
      if(storedCount && parseInt(storedCount) === 0) {
        console.log('🛒 Header: Cart was cleared or order completed, skipping API call to prevent new cart creation')
        setCartCount(0)
        return
      }

      console.log('🛒 Header: Fetching cart count...')
      const response = await apiService.getCart()
      console.log('🛒 Header: Cart API response:', response)

      if(response.success && response.cart) {
        console.log('🛒 Header: Full cart response:', JSON.stringify(response.cart, null, 2))

        // Always calculate count from items as primary method
        const items = response.cart.items || []
        const calculatedCount = items.length  // Count unique items, not total quantity
        const apiCount = response.cart.total_items || 0

        console.log('🛒 Header: API total_items:', apiCount)
        console.log('🛒 Header: Calculated unique items count:', calculatedCount)
        console.log('🛒 Header: Cart ID:', response.cart.id)
        console.log('🛒 Header: Cart items:', items.length)
        console.log('🛒 Header: Cart subtotal:', response.cart.subtotal)

        // Use calculated count as primary, API count as fallback
        const finalCount = calculatedCount > 0 ? calculatedCount : apiCount
        console.log('🛒 Header: Setting cart count to:', finalCount)

        // Debug: Check if we're using calculated or API count
        if(calculatedCount > 0 && apiCount === 0) {
          console.log('🛒 Header: Using calculated unique items count because API total_items is 0')
        } else if(apiCount > 0) {
          console.log('🛒 Header: Using API count')
        } else {
          console.log('🛒 Header: Both counts are 0, cart is empty')
        }

        // If both counts are 0 but sessionStorage has a count, use sessionStorage
        if(finalCount === 0) {
          const storedCount = sessionStorage.getItem('cartCount')
          if(storedCount && parseInt(storedCount) > 0) {
            console.log('🛒 Header: Using sessionStorage count as fallback:', storedCount)
            setCartCount(parseInt(storedCount))
            return
          }
        }

        // If calculated count is 0 but sessionStorage has count, use sessionStorage
        if(calculatedCount === 0 && apiCount === 0) {
          const storedCount = sessionStorage.getItem('cartCount')
          if(storedCount && parseInt(storedCount) > 0) {
            console.log('🛒 Header: Session mismatch detected, using sessionStorage count:', storedCount)
            setCartCount(parseInt(storedCount))
            return
          }
        }

        // If both counts are 0 but sessionStorage has count, use sessionStorage
        if(finalCount === 0) {
          const storedCount = sessionStorage.getItem('cartCount')
          if(storedCount && parseInt(storedCount) > 0) {
            console.log('🛒 Header: Using sessionStorage count as fallback:', storedCount)
            setCartCount(parseInt(storedCount))
            return
          }
        }

        // Debug: Log the full cart response structure
        console.log('🛒 Header: Full cart response structure:', {
          id: response.cart.id,
          total_items: response.cart.total_items,
          subtotal: response.cart.subtotal,
          items_count: response.cart.items?.length || 0,
          items: response.cart.items?.map(item => ({
            id: item.id,
            quantity: item.quantity,
            product_title: item.product?.title
          })) || []
        })

        // Debug: Check if we're using calculated or API count
        if(calculatedCount > 0 && apiCount === 0) {
          console.log('🛒 Header: Using calculated unique items count because API total_items is 0')
        } else if(apiCount > 0) {
          console.log('🛒 Header: Using API count')
        } else {
          console.log('🛒 Header: Both counts are 0, cart is empty')
        }

        // Store cart count in sessionStorage as backup
        sessionStorage.setItem('cartCount', finalCount.toString())
        setCartCount(finalCount)
      } else {
        console.log('🛒 Header: Cart API failed or no cart data')
        // Try to get from sessionStorage
        const storedCount = sessionStorage.getItem('cartCount')
        if(storedCount) {
          console.log('🛒 Header: Using stored cart count:', storedCount)
          setCartCount(parseInt(storedCount))
        } else {
          setCartCount(0)
        }
      }
    } catch(error) {
      console.error('🛒 Header: Error fetching cart count:', error)
      // Try to get from sessionStorage
      const storedCount = sessionStorage.getItem('cartCount')
      if(storedCount) {
        console.log('🛒 Header: Using stored cart count on error:', storedCount)
        setCartCount(parseInt(storedCount))
      } else {
        setCartCount(0)
      }
    }
  }

  // Load cart count on component mount
  useEffect(() => {
    // First try to get from sessionStorage
    const storedCount = sessionStorage.getItem('cartCount')
    if(storedCount) {
      console.log('🛒 Header: Using stored cart count on mount:', storedCount)
      setCartCount(parseInt(storedCount))
    }

    // Then fetch from API
    fetchCartCount()
  }, [])

  // Add a function to sync sessionStorage with cart count
  const syncCartCount = () => {
    const storedCount = sessionStorage.getItem('cartCount')
    if(storedCount) {
      console.log('🛒 Header: Syncing cart count from sessionStorage:', storedCount)
      setCartCount(parseInt(storedCount))
    }
  }

  // Add a function to force sync from sessionStorage
  const forceSyncFromSessionStorage = () => {
    const storedCount = sessionStorage.getItem('cartCount')
    if(storedCount && parseInt(storedCount) > 0) {
      console.log('🛒 Header: Force syncing from sessionStorage:', storedCount)
      setCartCount(parseInt(storedCount))
    }
  }

  // Listen for cart updates (custom event)
  useEffect(() => {
    const handleCartUpdate = () => {
      console.log('🛒 Header: cartUpdated event received!')

      // Check if cart was cleared or order completed (sessionStorage count is 0)
      const storedCount = sessionStorage.getItem('cartCount')
      if(storedCount && parseInt(storedCount) === 0) {
        console.log('🛒 Header: Cart was cleared or order completed, skipping API call to prevent new cart creation')
        setCartCount(0)
        return
      }

      // Add small delay to ensure backend has processed the update
      setTimeout(() => {
        fetchCartCount()
      }, 200)
    }

    // Add a function to check if we should skip API call
    const shouldSkipApiCall = () => {
      const storedCount = sessionStorage.getItem('cartCount')
      return storedCount && parseInt(storedCount) > 0
    }

    // Also listen for sessionStorage changes
    const handleStorageChange = (e) => {
      if(e.key === 'cartCount') {
        console.log('🛒 Header: sessionStorage cartCount changed to:', e.newValue)
        if(e.newValue) {
          setCartCount(parseInt(e.newValue))
        }
      }
    }

    window.addEventListener('storage', handleStorageChange)

    // Also listen for custom cart sync events
    const handleCartSync = () => {
      console.log('🛒 Header: Cart sync event received!')
      syncCartCount()
    }

    window.addEventListener('cartSync', handleCartSync)

    // Also listen for force sync events
    const handleForceSync = () => {
      console.log('🛒 Header: Force sync event received!')
      forceSyncFromSessionStorage()
    }

    window.addEventListener('forceCartSync', handleForceSync)

    // Listen for cart updates from any component
    window.addEventListener('cartUpdated', handleCartUpdate)
    console.log('🛒 Header: Added cartUpdated event listener')

    // Also listen for cart updates when cart modal is open/closed
    const handleCartModalChange = () => {
      console.log('🛒 Header: Cart modal change event received!')
      // Small delay to ensure cart data is updated
      setTimeout(() => {
        // Skip API call if we have sessionStorage count
        if(shouldSkipApiCall()) {
          console.log('🛒 Header: Skipping API call on modal change, using sessionStorage count')
          const storedCount = sessionStorage.getItem('cartCount')
          if(storedCount) {
            setCartCount(parseInt(storedCount))
          }
          return
        }

        fetchCartCount()
      }, 100)
    }

    window.addEventListener('cartModalOpened', handleCartModalChange)
    window.addEventListener('cartModalClosed', handleCartModalChange)

    // Poll cart count every 30 seconds as backup (reduced frequency)
    const pollInterval = setInterval(() => {
      console.log('🛒 Header: Polling cart count...')

      // Skip API call if we have sessionStorage count
      if(shouldSkipApiCall()) {
        console.log('🛒 Header: Skipping API call, using sessionStorage count')
        const storedCount = sessionStorage.getItem('cartCount')
        if(storedCount) {
          setCartCount(parseInt(storedCount))
        }
        return
      }

      fetchCartCount()
    }, 30000)

    return () => {
      window.removeEventListener('cartUpdated', handleCartUpdate)
      window.removeEventListener('cartModalOpened', handleCartModalChange)
      window.removeEventListener('cartModalClosed', handleCartModalChange)
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('cartSync', handleCartSync)
      window.removeEventListener('forceCartSync', handleForceSync)
      clearInterval(pollInterval)
      console.log('🛒 Header: Removed event listeners and polling')
    }
  }, [])

  // Handle cart button click
  const handleCartClick = () => {
    console.log('🛒 Header: Cart button clicked!')
    console.log('🛒 Header: Current URL:', window.location.href)
    console.log('🛒 Header: Current path:', window.location.pathname)

    // Navigate to cart page
    window.location.replace('/cart')
    console.log('🛒 Header: Navigation called')
  }


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
                      if(user?.is_staff || user?.is_superuser) {
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
                  <span className="user-name">{user?.full_name || user?.email}</span>
                </div>
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

                <button className="action-btn" onClick={handleCartClick}>
                  <ion-icon name="bag-handle-outline"></ion-icon>
                  <span className="count">{cartCount}</span>
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
                    <div style={{padding: '20px', textAlign: 'center'}}>
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
                              <a href={`/category/${category.slug}`} style={{fontWeight: 'bold', color: '#6366f1'}}>
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

          <button className="action-btn" onClick={handleCartClick}>
            <ion-icon name="bag-handle-outline"></ion-icon>
            <span className="count">{cartCount}</span>
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
              <div style={{padding: '20px', textAlign: 'center'}}>
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
                        <span className="submenu-title" style={{color: '#9ca3af'}}>
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