import React, { useState, useEffect, useRef, useCallback } from "react"
import apiService from "../services/api"
import InvoiceModal from "./InvoiceModal"

const CartPage = ({ isOpen, onClose }) => {
  const [cart, setCart] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [updatingItems, setUpdatingItems] = useState({})
  const [showClearConfirm, setShowClearConfirm] = useState(false)
  
  // Order form state
  const [orderForm, setOrderForm] = useState({
    fullName: '',
    phoneNumber: '',
    city: '',
    address: '',
    paymentMethod: 'cash_on_delivery'
  })
  const [isPlacingOrder, setIsPlacingOrder] = useState(false)
  const [showInvoice, setShowInvoice] = useState(false)
  const [orderData, setOrderData] = useState(null)
  
  // Debouncing refs
  const debounceTimeouts = useRef({})
  const pendingOperations = useRef({})

  // Fetch cart
  useEffect(() => {
    if (isOpen) {
      const fetchCart = async () => {
        setLoading(true)
        try {
          const response = await apiService.getCart()
          if (response.success) {
            setCart(response.cart)
          } else {
            setError("Failed to load cart")
          }
        } catch (err) {
          setError("Failed to load cart")
        } finally {
          setLoading(false)
        }
      }
      fetchCart()
    }
  }, [isOpen])

  // Cleanup debounce timeouts on unmount
  useEffect(() => {
    return () => {
      // Clear all pending timeouts
      Object.values(debounceTimeouts.current).forEach(timeout => {
        if (timeout) clearTimeout(timeout)
      })
    }
  }, [])

  // Handle order form input changes
  const handleOrderFormChange = (field, value) => {
    setOrderForm(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // Place order function
  const handlePlaceOrder = async () => {
    if (!cart || !cart.items || cart.items.length === 0) {
      setError("Cart is empty")
      return
    }

    // Validate form
    if (!orderForm.fullName || !orderForm.phoneNumber || !orderForm.city || !orderForm.address) {
      setError("Please fill in all required fields")
      return
    }

    setIsPlacingOrder(true)
    setError(null)

    try {
      const orderData = {
        address: {
          full_name: orderForm.fullName,
          phone_number: orderForm.phoneNumber,
          city: orderForm.city,
          address_line_1: orderForm.address,
          country: 'Bangladesh'
        },
        payment_method: orderForm.paymentMethod,
        notes: ''
      }

      const response = await apiService.placeOrder(orderData)
      
      if (response.success) {
        // Order placed successfully
        setOrderData(response.order)
        setShowInvoice(true) // Show invoice modal
        // Optionally clear the cart or refresh it
        const cartResponse = await apiService.getCart()
        if (cartResponse.success) {
          setCart(cartResponse.cart)
        }
      } else {
        setError(response.message || "Failed to place order")
      }
    } catch (err) {
      setError("Failed to place order. Please try again.")
      console.error("Order placement error:", err)
    } finally {
      setIsPlacingOrder(false)
    }
  }

  // Optimistic update function
  const optimisticUpdateQuantity = useCallback((itemId, change) => {
    setCart(prevCart => {
      if (!prevCart) return prevCart
      
      const updatedItems = prevCart.items.map(item => {
        if (item.id === itemId) {
          const newQuantity = Math.max(1, item.quantity + change)
          return { ...item, quantity: newQuantity }
        }
        return item
      })
      
      const totalItems = updatedItems.reduce((sum, item) => sum + item.quantity, 0)
      const subtotal = updatedItems.reduce((sum, item) => sum + (item.product.price * item.quantity), 0)
      
      return {
        ...prevCart,
        items: updatedItems,
        total_items: totalItems,
        subtotal: subtotal
      }
    })
  }, [])

  // Debounced API call function
  const debouncedApiCall = useCallback(async (itemId, operation) => {
    console.log(`🛒 Frontend: Debounced API call for item ${itemId}, operation: ${operation}`)
    
    try {
      let response
      if (operation === 'increase') {
        response = await apiService.increaseCartItemQuantity(itemId)
      } else if (operation === 'decrease') {
        response = await apiService.decreaseCartItemQuantity(itemId)
      }
      
      if (response && response.success) {
        console.log(`🛒 Frontend: API call successful for item ${itemId}`)
        setCart(response.cart)
        sessionStorage.setItem('cartCount', response.cart.total_items.toString())
        window.dispatchEvent(new CustomEvent('cartUpdated'))
      } else {
        console.error(`🛒 Frontend: API call failed for item ${itemId}`)
        // Rollback optimistic update
        const fetchCart = async () => {
          try {
            const cartResponse = await apiService.getCart()
            if (cartResponse.success) {
              setCart(cartResponse.cart)
            }
          } catch (err) {
            console.error('Failed to rollback cart state:', err)
          }
        }
        fetchCart()
      }
    } catch (error) {
      console.error(`🛒 Frontend: API call error for item ${itemId}:`, error)
      // Rollback optimistic update
      const fetchCart = async () => {
        try {
          const cartResponse = await apiService.getCart()
          if (cartResponse.success) {
            setCart(cartResponse.cart)
          }
        } catch (err) {
          console.error('Failed to rollback cart state:', err)
        }
      }
      fetchCart()
    } finally {
      setUpdatingItems(prev => ({ ...prev, [itemId]: false }))
      delete pendingOperations.current[itemId]
    }
  }, [])

  // Handle quantity increase with debouncing
  const handleIncreaseQuantity = useCallback((itemId) => {
    console.log(`🛒 Frontend: Increase quantity clicked for item ${itemId}`)
    
    // Optimistic update
    optimisticUpdateQuantity(itemId, 1)
    setUpdatingItems(prev => ({ ...prev, [itemId]: true }))
    
    // Clear existing timeout
    if (debounceTimeouts.current[itemId]) {
      clearTimeout(debounceTimeouts.current[itemId])
    }
    
    // Set new timeout
    debounceTimeouts.current[itemId] = setTimeout(() => {
      pendingOperations.current[itemId] = 'increase'
      debouncedApiCall(itemId, 'increase')
    }, 300) // 300ms debounce
  }, [optimisticUpdateQuantity, debouncedApiCall])

  // Handle quantity decrease with debouncing
  const handleDecreaseQuantity = useCallback((itemId) => {
    console.log(`🛒 Frontend: Decrease quantity clicked for item ${itemId}`)
    
    // Check if quantity is 1, if so, don't decrease
    const currentItem = cart?.items?.find(item => item.id === itemId)
    if (currentItem && currentItem.quantity <= 1) {
      console.log(`🛒 Frontend: Cannot decrease quantity below 1 for item ${itemId}`)
      return
    }
    
    // Optimistic update
    optimisticUpdateQuantity(itemId, -1)
    setUpdatingItems(prev => ({ ...prev, [itemId]: true }))
    
    // Clear existing timeout
    if (debounceTimeouts.current[itemId]) {
      clearTimeout(debounceTimeouts.current[itemId])
    }
    
    // Set new timeout
    debounceTimeouts.current[itemId] = setTimeout(() => {
      pendingOperations.current[itemId] = 'decrease'
      debouncedApiCall(itemId, 'decrease')
    }, 300) // 300ms debounce
  }, [cart, optimisticUpdateQuantity, debouncedApiCall])

  // Handle remove item with optimistic update
  const handleRemoveItem = useCallback(async (itemId) => {
    console.log('🛒 Frontend: handleRemoveItem called with ID:', itemId)
    
    // Store original cart state for rollback
    const originalCart = cart
    
    // Optimistic update - remove item immediately
    setCart(prevCart => {
      if (!prevCart) return prevCart
      
      const updatedItems = prevCart.items.filter(item => item.id !== itemId)
      const totalItems = updatedItems.reduce((sum, item) => sum + item.quantity, 0)
      const subtotal = updatedItems.reduce((sum, item) => sum + (item.product.price * item.quantity), 0)
      
      return {
        ...prevCart,
        items: updatedItems,
        total_items: totalItems,
        subtotal: subtotal
      }
    })
    
    // Update sessionStorage optimistically
    const newTotalItems = cart?.items?.filter(item => item.id !== itemId).reduce((sum, item) => sum + item.quantity, 0) || 0
    sessionStorage.setItem('cartCount', newTotalItems.toString())
    window.dispatchEvent(new CustomEvent('cartUpdated'))
    
    // If cart becomes empty, dispatch force sync
    if (newTotalItems === 0) {
      window.dispatchEvent(new CustomEvent('forceCartSync'))
      console.log('🛒 Frontend: Dispatched forceCartSync event (cart empty)')
    }
    
    try {
      console.log('🛒 Frontend: Removing cart item ID:', itemId)
      const response = await apiService.removeCartItem(itemId)
      console.log('🛒 Frontend: Remove API response:', response)
      
      if (response.success) {
        console.log('🛒 Frontend: Remove successful, updating cart state')
        setCart(response.cart)
        sessionStorage.setItem('cartCount', response.cart.total_items.toString())
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        
        if (response.cart.total_items === 0) {
          window.dispatchEvent(new CustomEvent('forceCartSync'))
        }
      } else {
        console.error('🛒 Frontend: Remove failed, rolling back:', response.error)
        // Rollback optimistic update
        setCart(originalCart)
        sessionStorage.setItem('cartCount', originalCart?.total_items?.toString() || '0')
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        alert('Failed to remove item from cart')
      }
    } catch (error) {
      console.error('🛒 Frontend: Remove error, rolling back:', error)
      // Rollback optimistic update
      setCart(originalCart)
      sessionStorage.setItem('cartCount', originalCart?.total_items?.toString() || '0')
      window.dispatchEvent(new CustomEvent('cartUpdated'))
      alert('Failed to remove item from cart')
    }
  }, [cart])

  // Handle clear cart
  const handleClearCart = async () => {
    console.log('🛒 Frontend: Clear cart button clicked')
    setShowClearConfirm(true)
  }

  // Confirm clear cart
  const confirmClearCart = async () => {
    console.log('🛒 Frontend: User confirmed clear cart operation')
    setShowClearConfirm(false)
    
    try {
      setLoading(true)
      console.log('🛒 Frontend: Calling clear cart API...')
      
      const response = await apiService.clearCart()
      console.log('🛒 Frontend: Clear cart API response:', response)
      
      if (response.success) {
        console.log('🛒 Frontend: Clear cart successful, updating state')
        
        // Update cart state with API response
        setCart(response.cart)
        
        // Update sessionStorage
        sessionStorage.setItem('cartCount', response.cart.total_items.toString())
        console.log('🛒 Frontend: Updated sessionStorage cartCount to:', response.cart.total_items)
        
        // Dispatch cart updated event
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        console.log('🛒 Frontend: Dispatched cartUpdated event')
        
        // Force sync for header
        window.dispatchEvent(new CustomEvent('forceCartSync'))
        console.log('🛒 Frontend: Dispatched forceCartSync event')
        
        alert('Cart cleared successfully!')
      } else {
        console.error('🛒 Frontend: Clear cart failed:', response.error)
        alert('Failed to clear cart: ' + (response.error || 'Unknown error'))
      }
    } catch (error) {
      console.error('🛒 Frontend: Error clearing cart:', error)
      alert('Failed to clear cart: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Get product image
  const getProductImage = (item) => {
    if (item.product && item.product.primary_image) {
      const primaryImage = item.product.primary_image
      if (primaryImage.image_url) {
        if (primaryImage.image_url.startsWith('http')) {
          return primaryImage.image_url
        }
        return `http://127.0.0.1:8000${primaryImage.image_url}`
      }
      if (primaryImage.image) {
        if (primaryImage.image.startsWith('http')) {
          return primaryImage.image
        }
        return `http://127.0.0.1:8000${primaryImage.image}`
      }
    }
    return "/assets/images/products/1.jpg"
  }

  // Format price in BDT
  const formatPrice = (amount) => {
    const safeAmount = Number(amount || 0)
    try {
      return new Intl.NumberFormat('en-BD', { style: 'currency', currency: 'BDT', minimumFractionDigits: 0 }).format(safeAmount)
    } catch (e) {
      return `৳${safeAmount.toLocaleString('en-BD')}`
    }
  }

  if (!isOpen) return null

  return (
    <>
      {/* Custom Clear Cart Confirmation Modal */}
      {showClearConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 2000
        }}>
          <div style={{
            background: '#fff',
            padding: '30px',
            borderRadius: '12px',
            maxWidth: '400px',
            width: '90%',
            textAlign: 'center',
            boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
          }}>
            <div style={{
              fontSize: '48px',
              marginBottom: '20px'
            }}>
              ⚠️
            </div>
            <h3 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#1f2937',
              marginBottom: '15px',
              margin: '0 0 15px 0'
            }}>
              Clear Cart?
            </h3>
            <p style={{
              fontSize: '16px',
              color: '#6b7280',
              marginBottom: '30px',
              lineHeight: '1.5',
              margin: '0 0 30px 0'
            }}>
              Are you sure you want to clear your entire cart?<br/>
              This action cannot be undone.
            </p>
            <div style={{
              display: 'flex',
              gap: '15px',
              justifyContent: 'center'
            }}>
              <button
                onClick={() => {
                  console.log('🛒 Frontend: User canceled clear cart operation')
                  setShowClearConfirm(false)
                }}
                style={{
                  background: '#f3f4f6',
                  color: '#374151',
                  padding: '12px 24px',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => e.target.style.background = '#e5e7eb'}
                onMouseLeave={(e) => e.target.style.background = '#f3f4f6'}
              >
                Cancel
              </button>
              <button
                onClick={confirmClearCart}
                style={{
                  background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                  color: '#fff',
                  padding: '12px 24px',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  boxShadow: '0 4px 15px rgba(239, 68, 68, 0.3)',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)'
                  e.target.style.transform = 'translateY(-2px)'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
                  e.target.style.transform = 'translateY(0)'
                }}
              >
                🗑️ Clear Cart
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CSS */}
      <style>
        {`
          * { margin: 0; padding: 0; box-sizing: border-box; }
          .checkout-container {
            background: #fff;
            border-radius: 12px;
            padding: 10px;
            width: 100%;
            max-width: 1200px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 60px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
          }
          h2 { font-size: 20px; margin-bottom: 20px; }
          .order-item {
            display: flex; align-items: center; gap: 15px;
            padding: 15px 0; border-bottom: 1px solid #eee;
          }
          .order-item img {
            width: 80px; height: 80px; object-fit: cover;
            border-radius: 8px; background: #f3f4f6;
          }
          .item-info { flex: 1; }
          .item-info h4 { font-size: 15px; font-weight: bold; margin-bottom: 5px; }
          .item-actions { margin-top: 8px; }
          .remove-btn { 
            background: none; 
            border: none; 
            color: #ef4444; 
            font-size: 12px; 
            cursor: pointer; 
            text-decoration: underline;
            padding: 0;
          }
          .remove-btn:hover { color: #dc2626; }
          .clear-cart-btn { 
            background: #ef4444; 
            color: #fff; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 6px; 
            font-size: 12px; 
            cursor: pointer; 
            margin-top: 10px;
            font-weight: 500;
            height: 36px;
          }
          .clear-cart-btn:hover { background: #dc2626; }
          .clear-cart-btn:disabled { background: #9ca3af; cursor: not-allowed; }
          .continue-shopping-btn { 
            background: #6366f1; 
            color: #fff; 
            padding: 12px 20px; 
            border-radius: 30px; 
            font-size: 14px; 
            border: none; 
            cursor: pointer; 
            width: 100%;
            margin-top: 5px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          .continue-shopping-btn:hover { background: #4f46e5; }
          .order-price { font-weight: bold; color: #2563eb; font-size: 14px; margin-bottom: 10px; }
          .qty-control { display: flex; align-items: center; border: 1px solid #ddd; border-radius: 6px; overflow: hidden; }
          .qty-control button { background: #f9fafb; border: none; padding: 4px 10px; cursor: pointer; }
          .qty-control span { padding: 4px 12px; border-left: 1px solid #ddd; border-right: 1px solid #ddd; font-size: 14px; }
          .coupon { margin-top: 10px; display: flex; justify-content: center; }
          .coupon button { background: #0f172a; color: #fff; padding: 12px 20px; border-radius: 30px; font-size: 14px; border: none; cursor: pointer; width: 100%; }
          .cart-summary { border: 1px solid #eee; border-radius: 8px; padding: 20px; font-size: 14px; }
          .cart-summary div { display: flex; justify-content: space-between; margin-bottom: 8px; }
          .cart-summary .total { font-weight: bold; margin-top: 10px; font-size: 16px; }
          .form-group { margin: 15px 0; }
          .form-group label { font-size: 13px; display: block; margin-bottom: 6px; }
          .form-group input { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #ddd; font-size: 14px; }
          
.payment-options {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  margin: 15px 0;
  background: #fff;
}

.payment-options label {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 14px;
  cursor: pointer;
  color: #333;
}

.payment-options input[type="radio"] {
  accent-color: #6366f1; /* Nice purple color */
  width: 16px;
  height: 16px;
}
.payment-options .add-card {
  margin-top: 10px;
  color: #2563eb;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
}

          .actions { display: flex; justify-content: flex-end; gap: 15px; margin-top: 20px; }
          .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 14px; }
          .btn.cancel { background: #f3f4f6; color: #374151; }
          .btn.order { background: #6366f1; color: #fff; }
          .btn.order:hover { background: #4f46e5; }
        `}
      </style>

      {/* Modal Background */}
      <div
        style={{
          position: "fixed",
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: "rgba(0,0,0,0.5)",
          display: "flex", justifyContent: "center", alignItems: "center",
          zIndex: 1000, padding: "5px"
        }}
        onClick={onClose}
      >
        {/* Modal Content */}
        <div
          onClick={(e) => e.stopPropagation()}
          style={{
            background: "#f9fafb",
            padding: "5px",
            borderRadius: "12px",
            maxHeight: "120vh",
            overflow: "auto",
            width: "100%",
            maxWidth: "1200px"
          }}
        >
          {loading ? (
            <p>Loading cart...</p>
          ) : error ? (
            <p>{error}</p>
          ) : (
            <div className="checkout-container">
              {/* Left Column */}
              <div>
                <h2>Order Summary</h2>
                {/* Empty Cart State */}
                {(!cart || !cart.items || cart.items.length === 0) && (
                  <div style={{
                    padding: '60px 20px',
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
                    borderRadius: '12px',
                    border: '2px dashed #cbd5e1',
                    margin: '20px 0'
                  }}>
                    {/* Empty Cart Icon */}
                    <div style={{
                      fontSize: '48px',
                      marginBottom: '20px',
                      color: '#94a3b8'
                    }}>
                      🛒
                    </div>
                    
                    {/* Empty Cart Title */}
                    <h3 style={{
                      fontSize: '24px',
                      fontWeight: '600',
                      color: '#334155',
                      marginBottom: '12px',
                      margin: '0 0 12px 0'
                    }}>
                      Your cart is empty
                    </h3>
                    
                    {/* Empty Cart Description */}
                    <p style={{
                      fontSize: '16px',
                      color: '#64748b',
                      marginBottom: '30px',
                      margin: '0 0 30px 0',
                      lineHeight: '1.5'
                    }}>
                      Looks like you haven't added any items to your cart yet.<br/>
                      Start shopping to fill it up!
                    </p>
                    
                    {/* Continue Shopping Button */}
                    <button 
                      className="continue-shopping-btn"
                      onClick={onClose}
                      style={{ 
                        maxWidth: '280px', 
                        margin: '0 auto',
                        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        color: '#fff',
                        padding: '14px 28px',
                        border: 'none',
                        borderRadius: '30px',
                        fontSize: '16px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)',
                        transition: 'all 0.3s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)'
                        e.target.style.transform = 'translateY(-2px)'
                        e.target.style.boxShadow = '0 6px 20px rgba(99, 102, 241, 0.4)'
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'
                        e.target.style.transform = 'translateY(0)'
                        e.target.style.boxShadow = '0 4px 15px rgba(99, 102, 241, 0.3)'
                      }}
                    >
                      🛍️ Start Shopping →
                    </button>
                  </div>
                )}
                {cart?.items?.map((item) => (
                  <div key={item.id} className="order-item">
                    <img 
                      src={getProductImage(item)} 
                      alt={item.product?.title || 'Product'} 
                      onError={(e) => { e.target.src = "/assets/images/products/1.jpg" }}
                    />
                    <div className="item-info">
                      <h4>{item.product?.title || 'Product'}</h4>
                      {item.variant && <p>{item.variant.title}</p>}
                      <div className="item-actions">
                        <button 
                          className="remove-btn"
                          onClick={() => {
                            console.log('🛒 Frontend: Remove button clicked for item ID:', item.id);
                            handleRemoveItem(item.id);
                          }}
                          disabled={updatingItems[item.id]}
                        >
                          {updatingItems[item.id] ? 'Removing...' : 'Remove'}
                        </button>
                      </div>
                    </div>
                    <div>
                      <div className="order-price">{formatPrice(item.unit_price)}</div>
                      <div className="qty-control">
                        <button 
                          onClick={() => handleDecreaseQuantity(item.id)}
                          disabled={updatingItems[item.id] || item.quantity <= 1}
                        >-</button>
                        <span>{updatingItems[item.id] ? '...' : item.quantity}</span>
                        <button 
                          onClick={() => handleIncreaseQuantity(item.id)}
                          disabled={updatingItems[item.id] || !item.can_increase}
                        >+</button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Clear Cart and Add Coupon Buttons */}
                {cart?.items && cart.items.length > 0 && (
                  <div style={{ marginTop: '20px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <button 
                      className="clear-cart-btn"
                      onClick={() => {
                        console.log('🛒 Frontend: Clear cart button clicked!');
                        handleClearCart();
                      }}
                      disabled={loading}
                      style={{ 
                        flex: 1, 
                        marginTop: 0,
                        background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                        color: '#fff',
                        padding: '12px 20px',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        boxShadow: '0 4px 15px rgba(239, 68, 68, 0.3)',
                        transition: 'all 0.3s ease',
                        opacity: loading ? 0.7 : 1
                      }}
                      onMouseEnter={(e) => {
                        if (!loading) {
                          e.target.style.background = 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)'
                          e.target.style.transform = 'translateY(-2px)'
                          e.target.style.boxShadow = '0 6px 20px rgba(239, 68, 68, 0.4)'
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!loading) {
                          e.target.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
                          e.target.style.transform = 'translateY(0)'
                          e.target.style.boxShadow = '0 4px 15px rgba(239, 68, 68, 0.3)'
                        }
                      }}
                    >
                      {loading ? '🗑️ Clearing...' : '🗑️ Clear Cart'}
                    </button>
                    <button 
                      style={{ 
                        flex: 1,
                        background: '#0f172a',
                        color: '#fff',
                        padding: '8px 16px',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '12px',
                        cursor: 'pointer',
                        fontWeight: '500',
                        height: '36px',
                        marginTop: 0
                      }}
                    >
                      Add Coupon Code →
                    </button>
                  </div>
                )}
                
                {/* Continue Shopping Button */}
                <div className="coupon">
                  <button 
                    className="continue-shopping-btn" 
                    onClick={onClose}
                    style={{
                      background: '#6366f1',
                      color: '#fff',
                      padding: '12px 20px',
                      border: 'none',
                      borderRadius: '30px',
                      fontSize: '14px',
                      cursor: 'pointer',
                      width: '100%',
                      marginTop: '5px',
                      textAlign: 'center',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                    onMouseEnter={(e) => e.target.style.background = '#4f46e5'}
                    onMouseLeave={(e) => e.target.style.background = '#6366f1'}
                  >
                    Continue Shopping →
                  </button>
                </div>
              </div>

              {/* Right Column */}
              <div>
                <h2>
                  Shopping Cart{" "}
                  <span style={{ color: "#6366f1", fontSize: "14px" }}>
                    {cart?.total_items || 0} Items
                  </span>
                </h2>

                {/* Cart Summary */}
                {cart?.items && cart.items.length > 0 ? (
                  <div className="cart-summary">
                    <div><span>Subtotal:</span><span>{formatPrice(cart?.subtotal)}</span></div>
                    <div><span>Delivery:</span><span>{formatPrice(0)}</span></div>
                    <div className="total"><span>Total:</span><span>{formatPrice(cart?.subtotal)}</span></div>
                  </div>
                ) : (
                  <div className="cart-summary" style={{ textAlign: 'center', color: '#6b7280' }}>
                    No items in cart
                  </div>
                )}

                {/* Full Name */}
                <div className="form-group">
                  <label>Full Name *</label>
                  <input 
                    type="text" 
                    placeholder="Your Full Name"
                    value={orderForm.fullName}
                    onChange={(e) => handleOrderFormChange('fullName', e.target.value)}
                    required
                  />
                </div>

                {/* Phone */}
                <div className="form-group">
                  <label>Phone Number *</label>
                  <input 
                    type="text" 
                    placeholder="+8801XXXXXXXXX"
                    value={orderForm.phoneNumber}
                    onChange={(e) => handleOrderFormChange('phoneNumber', e.target.value)}
                    required
                  />
                </div>

                {/* City */}
                <div className="form-group">
                  <label>City *</label>
                  <input 
                    type="text" 
                    placeholder="Dhaka"
                    value={orderForm.city}
                    onChange={(e) => handleOrderFormChange('city', e.target.value)}
                    required
                  />
                </div>

                {/* Address */}
                <div className="form-group">
                  <label>Address *</label>
                  <input 
                    type="text" 
                    placeholder="Your Address"
                    value={orderForm.address}
                    onChange={(e) => handleOrderFormChange('address', e.target.value)}
                    required
                  />
                </div>

                {/* Payment Section */}
                <div className="payment-options">
                  <label>
                    <input 
                      type="radio" 
                      name="payment" 
                      value="cash_on_delivery"
                      checked={orderForm.paymentMethod === 'cash_on_delivery'}
                      onChange={(e) => handleOrderFormChange('paymentMethod', e.target.value)}
                    /> 
                    Cash on delivery
                  </label>
                  <label>
                    <input 
                      type="radio" 
                      name="payment" 
                      value="bkash"
                      checked={orderForm.paymentMethod === 'bkash'}
                      onChange={(e) => handleOrderFormChange('paymentMethod', e.target.value)}
                    /> 
                    Bkash Payment
                  </label>
                </div>

                {/* Error Display */}
                {error && (
                  <div style={{ 
                    color: '#ef4444', 
                    backgroundColor: '#fef2f2', 
                    padding: '12px', 
                    borderRadius: '8px', 
                    marginBottom: '16px',
                    border: '1px solid #fecaca'
                  }}>
                    {error}
                  </div>
                )}

                {/* Actions */}
                <div className="actions">
                  <button className="btn cancel" onClick={onClose}>Cancel</button>
                  <button 
                    className="btn order" 
                    onClick={handlePlaceOrder}
                    disabled={
                      !cart || 
                      !cart.items || 
                      cart.items.length === 0 || 
                      isPlacingOrder ||
                      !orderForm.fullName ||
                      !orderForm.phoneNumber ||
                      !orderForm.city ||
                      !orderForm.address
                    }
                  >
                    {isPlacingOrder ? 'Placing Order...' : 'Place Order'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Invoice Modal */}
      <InvoiceModal 
        isOpen={showInvoice}
        onClose={() => {
          setShowInvoice(false)
          setOrderData(null)
          onClose() // Close cart modal after invoice
        }}
        orderData={orderData}
      />
    </>
  )
}

export default CartPage
