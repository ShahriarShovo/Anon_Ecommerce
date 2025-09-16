import React, { useState, useEffect } from 'react'
import apiService from '../services/api'

const CartPage = ({ isOpen, onClose }) => {
  const [cart, setCart] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [updatingItems, setUpdatingItems] = useState({})
  const [pendingUpdates, setPendingUpdates] = useState({})

  // Fetch cart data
  const fetchCart = async () => {
    try {
      console.log('🛒 CartPage: Fetching cart data...')
      setLoading(true)
      const response = await apiService.getCart()
      console.log('🛒 CartPage: Cart API response:', response)
      
      if (response.success) {
        console.log('🛒 CartPage: Setting cart data:', response.cart)
        console.log('🛒 CartPage: Cart items:', response.cart?.items?.length || 0)
        console.log('🛒 CartPage: Cart total_items:', response.cart?.total_items)
        console.log('🛒 CartPage: Cart subtotal:', response.cart?.subtotal)
        
        // Check if cart has items
        if (response.cart?.items && response.cart.items.length > 0) {
          console.log('🛒 CartPage: Cart has items:', response.cart.items)
        } else {
          console.log('🛒 CartPage: Cart is empty')
          
          // Check if sessionStorage has cart count
          const storedCount = sessionStorage.getItem('cartCount')
          if (storedCount && parseInt(storedCount) > 0) {
            console.log('🛒 CartPage: SessionStorage has count but API shows empty cart')
            console.log('🛒 CartPage: This indicates session mismatch between frontend and backend')
            
            // Create a mock cart with items from sessionStorage
            const mockCart = {
              id: response.cart?.id || 'mock',
              total_items: parseInt(storedCount),
              subtotal: 0,
              items: []
            }
            
            console.log('🛒 CartPage: Using mock cart with count:', mockCart.total_items)
            console.log('🛒 CartPage: Session mismatch - frontend has items but backend cart is empty')
            console.log('🛒 CartPage: This is a temporary solution until session sync is fixed')
            setCart(mockCart)
            return
          }
        }
        
        setCart(response.cart)
      } else {
        throw new Error(response.error || 'Failed to fetch cart')
      }
    } catch (error) {
      console.error('🛒 CartPage: Error fetching cart:', error)
      setError('Failed to load cart')
    } finally {
      setLoading(false)
    }
  }

  // Load cart when component opens
  useEffect(() => {
    if (isOpen) {
      console.log('🛒 CartPage: Cart modal opened, fetching cart...')
      
      // First check sessionStorage
      const storedCount = sessionStorage.getItem('cartCount')
      if (storedCount && parseInt(storedCount) > 0) {
        console.log('🛒 CartPage: SessionStorage has cart count:', storedCount)
      }
      
      fetchCart()
    }
  }, [isOpen])

  // Handle quantity increase (optimized with debouncing)
  const handleIncreaseQuantity = (itemId) => {
    console.log('🛒 CartPage: Increasing quantity for item:', itemId)
    
    // Optimistically update UI
    setCart(prevCart => {
      if (!prevCart || !prevCart.items) return prevCart
      
      const updatedItems = prevCart.items.map(item => {
        if (item.id === itemId) {
          return { ...item, quantity: item.quantity + 1 }
        }
        return item
      })
      
      return {
        ...prevCart,
        items: updatedItems,
        total_items: updatedItems.reduce((sum, item) => sum + item.quantity, 0)
      }
    })
    
    // Debounced API call
    debouncedUpdate(itemId, 'increase')
  }

  // Handle quantity decrease (optimized with debouncing)
  const handleDecreaseQuantity = (itemId) => {
    console.log('🛒 CartPage: Decreasing quantity for item:', itemId)
    
    // Optimistically update UI
    setCart(prevCart => {
      if (!prevCart || !prevCart.items) return prevCart
      
      const updatedItems = prevCart.items.map(item => {
        if (item.id === itemId && item.quantity > 1) {
          return { ...item, quantity: item.quantity - 1 }
        }
        return item
      })
      
      return {
        ...prevCart,
        items: updatedItems,
        total_items: updatedItems.reduce((sum, item) => sum + item.quantity, 0)
      }
    })
    
    // Debounced API call
    debouncedUpdate(itemId, 'decrease')
  }

  // Debounced update function
  const debouncedUpdate = (itemId, action) => {
    // Clear existing timeout for this item
    if (pendingUpdates[itemId]) {
      clearTimeout(pendingUpdates[itemId])
    }

    // Set new timeout
    const timeoutId = setTimeout(async () => {
      setUpdatingItems(prev => ({ ...prev, [itemId]: true }))
      try {
        let response
        if (action === 'increase') {
          response = await apiService.increaseCartItemQuantity(itemId)
        } else if (action === 'decrease') {
          response = await apiService.decreaseCartItemQuantity(itemId)
        }
        
        if (response.success) {
          setCart(response.cart)
          
          // Update sessionStorage
          const newCount = response.cart?.total_items || 0
          sessionStorage.setItem('cartCount', newCount.toString())
          console.log('🛒 CartPage: Updated sessionStorage cart count to:', newCount)
          
          // Dispatch cart update event to update header counter
          window.dispatchEvent(new CustomEvent('cartUpdated'))
          
          // Also dispatch cart sync event
          console.log('🛒 CartPage: Dispatching cartSync event...')
          window.dispatchEvent(new CustomEvent('cartSync'))
          
          // Also dispatch force sync event
          console.log('🛒 CartPage: Dispatching forceCartSync event...')
          window.dispatchEvent(new CustomEvent('forceCartSync'))
        } else {
          throw new Error(response.error || 'Failed to update quantity')
        }
      } catch (error) {
        console.error(`Error ${action}ing quantity:`, error)
        alert(`Failed to update quantity: ${error.message}`)
        // Refresh cart to get correct state
        fetchCart()
      } finally {
        setUpdatingItems(prev => ({ ...prev, [itemId]: false }))
        setPendingUpdates(prev => {
          const newPending = { ...prev }
          delete newPending[itemId]
          return newPending
        })
      }
    }, 500) // 500ms debounce delay

    setPendingUpdates(prev => ({ ...prev, [itemId]: timeoutId }))
  }

  // Handle remove item (set quantity to 0)
  const handleRemoveItem = async (itemId) => {
    if (!window.confirm('Are you sure you want to remove this item from your cart?')) {
      return
    }

    try {
      setUpdatingItems(prev => ({ ...prev, [itemId]: true }))
      
      // Call decrease quantity until quantity reaches 0
      const response = await apiService.decreaseCartItemQuantity(itemId)
      
      if (response.success) {
        setCart(response.cart)
        
        // Update sessionStorage
        const newCount = response.cart?.total_items || 0
        sessionStorage.setItem('cartCount', newCount.toString())
        console.log('🛒 CartPage: Updated sessionStorage cart count to:', newCount)
        
        // Dispatch cart update event
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        window.dispatchEvent(new CustomEvent('cartSync'))
        window.dispatchEvent(new CustomEvent('forceCartSync'))
        
        alert('Item removed from cart successfully!')
      } else {
        throw new Error(response.error || 'Failed to remove item')
      }
    } catch (error) {
      console.error('Error removing item:', error)
      alert(`Failed to remove item: ${error.message}`)
    } finally {
      setUpdatingItems(prev => ({ ...prev, [itemId]: false }))
    }
  }

  // Handle clear cart
  const handleClearCart = async () => {
    if (!window.confirm('Are you sure you want to clear your cart?')) {
      return
    }

    try {
      setLoading(true)
      const response = await apiService.clearCart()
      
      if (response.success) {
        setCart(null)
        
        // Update sessionStorage
        sessionStorage.setItem('cartCount', '0')
        console.log('🛒 CartPage: Cleared sessionStorage cart count')
        
        // Dispatch cart update event to update header counter
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        
        // Also dispatch cart sync event
        console.log('🛒 CartPage: Dispatching cartSync event...')
        window.dispatchEvent(new CustomEvent('cartSync'))
        
        // Also dispatch force sync event
        console.log('🛒 CartPage: Dispatching forceCartSync event...')
        window.dispatchEvent(new CustomEvent('forceCartSync'))
        alert('Cart cleared successfully!')
      } else {
        throw new Error(response.error || 'Failed to clear cart')
      }
    } catch (error) {
      console.error('Error clearing cart:', error)
      alert(`Failed to clear cart: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  // Handle checkout
  const handleCheckout = () => {
    alert('Checkout functionality will be implemented soon!')
  }

  // Format price
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price)
  }

  // Get product image
  const getProductImage = (item) => {
    // Check if product has primary_image from ProductListSerializer
    if (item.product && item.product.primary_image) {
      const primaryImage = item.product.primary_image
      if (primaryImage.image_url) {
        // If it's already a full URL, return as is
        if (primaryImage.image_url.startsWith('http')) {
          return primaryImage.image_url
        }
        // If it's a relative path, make it full URL
        return `http://127.0.0.1:8000${primaryImage.image_url}`
      }
      // Fallback to image field if image_url is not available
      if (primaryImage.image) {
        if (primaryImage.image.startsWith('http')) {
          return primaryImage.image
        }
        return `http://127.0.0.1:8000${primaryImage.image}`
      }
    }
    
    // Fallback to static image
    return "/assets/images/products/1.jpg"
  }

  if (!isOpen) return null

  return (
    <div className={`cart-overlay ${isOpen ? 'active' : ''}`} onClick={onClose}>
      <div className="cart-popup" onClick={(e) => e.stopPropagation()}>
        {/* Modern Cart Header */}
        <div className="cart-header">
          <div className="cart-header-left">
            <div className="cart-icon">
              <ion-icon name="bag-handle-outline"></ion-icon>
            </div>
            <div className="cart-title-section">
              <h2 className="cart-title">Shopping Cart</h2>
              {cart && cart.total_items > 0 && (
                <p className="cart-subtitle">{cart.total_items} {cart.total_items === 1 ? 'item' : 'items'}</p>
              )}
            </div>
          </div>
          <button className="cart-close" onClick={onClose}>
            <ion-icon name="close-outline"></ion-icon>
          </button>
        </div>

        {/* Cart Content */}
        {loading ? (
          <div className="cart-loading">
            <div className="loading-spinner"></div>
            <p>Loading your cart...</p>
          </div>
        ) : error ? (
          <div className="cart-error">
            <div className="error-icon">
              <ion-icon name="alert-circle-outline"></ion-icon>
            </div>
            <h3>Oops! Something went wrong</h3>
            <p>{error}</p>
            <button className="retry-btn" onClick={fetchCart}>
              <ion-icon name="refresh-outline"></ion-icon>
              Try Again
            </button>
          </div>
        ) : !cart || (!cart.items || cart.items.length === 0) && cart.total_items === 0 ? (
          <div className="cart-empty">
            <div className="empty-icon">
              <ion-icon name="bag-outline"></ion-icon>
            </div>
            <h3>Your cart is empty</h3>
            <p>Looks like you haven't added any items to your cart yet.</p>
            <button className="continue-shopping-btn" onClick={onClose}>
              <ion-icon name="arrow-back-outline"></ion-icon>
              Continue Shopping
            </button>
          </div>
        ) : (
          <div className="cart-content">
            {/* Session Mismatch Notice */}
            {cart.total_items > 0 && (!cart.items || cart.items.length === 0) && (
              <div className="session-mismatch-notice">
                <div className="notice-icon">
                  <ion-icon name="warning-outline"></ion-icon>
                </div>
                <div className="notice-content">
                  <h4>Session Mismatch Detected</h4>
                  <p>Cart count: {cart.total_items} items</p>
                  <p>Please refresh the page to sync with server.</p>
                </div>
              </div>
            )}
            
            {/* Cart Items */}
            <div className="cart-items">
              {cart.items && cart.items.length > 0 ? cart.items.map((item) => (
                <div key={item.id} className="cart-item">
                  <div className="item-image">
                    <img 
                      src={getProductImage(item)} 
                      alt={item.product?.title || 'Product'} 
                      onError={(e) => { e.target.src = "/assets/images/products/1.jpg" }}
                    />
                  </div>
                  
                  <div className="item-info">
                    <div className="item-details">
                      <h4 className="item-title">
                        {item.product?.title || 'Product'}
                      </h4>
                      {item.variant && (
                        <p className="item-variant">
                          {item.variant.title}
                        </p>
                      )}
                      <p className="item-price">
                        {formatPrice(item.unit_price)}
                      </p>
                    </div>
                    
                    <div className="item-controls">
                      <div className="quantity-controls">
                        <button 
                          className="qty-btn decrease"
                          onClick={() => handleDecreaseQuantity(item.id)}
                          disabled={updatingItems[item.id] || item.quantity <= 1}
                          title="Decrease quantity"
                        >
                          <ion-icon name="remove-outline"></ion-icon>
                        </button>
                        
                        <span className="qty-value">
                          {updatingItems[item.id] ? (
                            <div className="mini-spinner"></div>
                          ) : (
                            item.quantity
                          )}
                        </span>
                        
                        <button 
                          className="qty-btn increase"
                          onClick={() => handleIncreaseQuantity(item.id)}
                          disabled={updatingItems[item.id] || !item.can_increase}
                          title={!item.can_increase ? "Not enough stock available" : "Increase quantity"}
                        >
                          <ion-icon name="add-outline"></ion-icon>
                        </button>
                      </div>
                      
                      <div className="item-total">
                        {formatPrice(item.total_price)}
                      </div>
                    </div>
                  </div>
                </div>
              )) : (
                <div className="no-items-message">
                  <div className="no-items-icon">
                    <ion-icon name="bag-outline"></ion-icon>
                  </div>
                  <p>No items to display due to session mismatch.</p>
                  <p>Cart count: {cart.total_items}</p>
                </div>
              )}
            </div>

            {/* Cart Summary */}
            <div className="cart-summary">
              <div className="summary-header">
                <h3>Order Summary</h3>
              </div>
              
              <div className="summary-details">
                <div className="summary-row">
                  <span>Subtotal</span>
                  <span>{formatPrice(cart?.subtotal || 0)}</span>
                </div>
                <div className="summary-row">
                  <span>Shipping</span>
                  <span>Calculated at checkout</span>
                </div>
                <div className="summary-row total">
                  <span>Total</span>
                  <span>{formatPrice(cart?.subtotal || 0)}</span>
                </div>
              </div>
              
              <div className="cart-actions">
                <button className="btn btn-outline" onClick={onClose}>
                  <ion-icon name="arrow-back-outline"></ion-icon>
                  Continue Shopping
                </button>
                <button className="btn btn-primary" onClick={handleCheckout}>
                  <ion-icon name="card-outline"></ion-icon>
                  Proceed to Checkout
                </button>
              </div>
              
              <button 
                className="btn btn-danger" 
                onClick={handleClearCart}
                disabled={loading}
              >
                <ion-icon name="trash-outline"></ion-icon>
                Clear Cart
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CartPage