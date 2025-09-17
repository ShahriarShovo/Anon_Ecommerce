import React, { useState, useEffect } from "react"
import apiService from "../services/api"

const CartPage = ({ isOpen, onClose }) => {
  const [cart, setCart] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [updatingItems, setUpdatingItems] = useState({})

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

  // Handle quantity increase
  const handleIncreaseQuantity = async (itemId) => {
    try {
      setUpdatingItems(prev => ({ ...prev, [itemId]: true }))
      const response = await apiService.increaseCartItemQuantity(itemId)
      if (response.success) {
        setCart(response.cart)
        // Update sessionStorage
        sessionStorage.setItem('cartCount', response.cart.total_items.toString())
        // Dispatch cart updated event
        window.dispatchEvent(new CustomEvent('cartUpdated'))
      } else {
        alert('Failed to update quantity')
      }
    } catch (error) {
      console.error('Error increasing quantity:', error)
      alert('Failed to update quantity')
    } finally {
      setUpdatingItems(prev => ({ ...prev, [itemId]: false }))
    }
  }

  // Handle quantity decrease
  const handleDecreaseQuantity = async (itemId) => {
    try {
      setUpdatingItems(prev => ({ ...prev, [itemId]: true }))
      const response = await apiService.decreaseCartItemQuantity(itemId)
      if (response.success) {
        setCart(response.cart)
        // Update sessionStorage
        sessionStorage.setItem('cartCount', response.cart.total_items.toString())
        // Dispatch cart updated event
        window.dispatchEvent(new CustomEvent('cartUpdated'))
      } else {
        alert('Failed to update quantity')
      }
    } catch (error) {
      console.error('Error decreasing quantity:', error)
      alert('Failed to update quantity')
    } finally {
      setUpdatingItems(prev => ({ ...prev, [itemId]: false }))
    }
  }

  // Handle remove item
  const handleRemoveItem = async (itemId) => {
    if (!window.confirm('Are you sure you want to remove this item?')) return
    
    try {
      setUpdatingItems(prev => ({ ...prev, [itemId]: true }))
      const response = await apiService.removeCartItem(itemId)
      if (response.success) {
        setCart(response.cart)
        // Update sessionStorage
        sessionStorage.setItem('cartCount', response.cart.total_items.toString())
        // Dispatch cart updated event
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        alert('Item removed successfully!')
      } else {
        alert('Failed to remove item')
      }
    } catch (error) {
      console.error('Error removing item:', error)
      alert('Failed to remove item')
    } finally {
      setUpdatingItems(prev => ({ ...prev, [itemId]: false }))
    }
  }

  // Handle clear cart
  const handleClearCart = async () => {
    if (!window.confirm('Are you sure you want to clear your entire cart?')) return
    
    try {
      setLoading(true)
      const response = await apiService.clearCart()
      if (response.success) {
        setCart({ ...cart, items: [], total_items: 0, subtotal: 0 })
        // Update sessionStorage
        sessionStorage.setItem('cartCount', '0')
        // Dispatch cart updated event
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        alert('Cart cleared successfully!')
      } else {
        alert('Failed to clear cart')
      }
    } catch (error) {
      console.error('Error clearing cart:', error)
      alert('Failed to clear cart')
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
                          onClick={() => handleRemoveItem(item.id)}
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
                <div style={{ marginTop: '20px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                  {cart?.items && cart.items.length > 0 && (
                    <button 
                      className="clear-cart-btn"
                      onClick={handleClearCart}
                      disabled={loading}
                      style={{ flex: 1, marginTop: 0 }}
                    >
                      {loading ? 'Clearing...' : 'Clear Cart'}
                    </button>
                  )}
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
                <div className="cart-summary">
                  <div><span>Subtotal:</span><span>{formatPrice(cart?.subtotal)}</span></div>
                  <div><span>Delivery:</span><span>{formatPrice(0)}</span></div>
                  <div className="total"><span>Total:</span><span>{formatPrice(cart?.subtotal)}</span></div>
                </div>

                {/* City */}
                <div className="form-group">
                  <label>City</label>
                  <input type="text" placeholder="Dhaka" />
                </div>

                {/* Address */}
                <div className="form-group">
                  <label>Address</label>
                  <input type="text" placeholder="Your Address" />
                </div>

                {/* Phone */}
                <div className="form-group">
                  <label>Phone Number</label>
                  <input type="text" placeholder="+8801XXXXXXXXX" />
                </div>

                {/* Payment Section */}
                <div className="payment-options">
                  <label><input type="radio" name="payment" /> Cash on delivery</label>
                  <label><input type="radio" name="payment" defaultChecked /> Bkash Payment</label>
                  

                  
                </div>

                {/* Actions */}
                <div className="actions">
                  <button className="btn cancel" onClick={onClose}>Cancel</button>
                  <button className="btn order">Order</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default CartPage
