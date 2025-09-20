import React, {useState, useEffect, useRef, useCallback} from "react"
import apiService from "../services/api"
import InvoiceModal from "./InvoiceModal"

const CartPageFull = () => {
    console.log('🛒 CartPageFull: Component rendered!')
    const [cart, setCart] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [updatingItems, setUpdatingItems] = useState({})
    const [showClearConfirm, setShowClearConfirm] = useState(false)

    // Order form state
    const [orderForm, setOrderForm] = useState({
        paymentMethod: 'cash_on_delivery'
    })
    const [isPlacingOrder, setIsPlacingOrder] = useState(false)
    const [showInvoice, setShowInvoice] = useState(false)
    const [orderData, setOrderData] = useState(null)

    // Address system state
    const [addresses, setAddresses] = useState([])
    const [selectedAddressId, setSelectedAddressId] = useState(null)
    const [showNewAddressForm, setShowNewAddressForm] = useState(false)
    const [isAddressSectionExpanded, setIsAddressSectionExpanded] = useState(true)
    const [newAddressForm, setNewAddressForm] = useState({
        full_name: '',
        phone_number: '',
        city: '',
        address_line_1: '',
        address_line_2: '',
        postal_code: '',
        country: 'Bangladesh',
        address_type: 'home',
        is_default: false
    })
    const [isSubmittingAddress, setIsSubmittingAddress] = useState(false)
    const [isAddressesLoading, setIsAddressesLoading] = useState(false)
    const [hasLoadedAddresses, setHasLoadedAddresses] = useState(false) // Track if addresses have been loaded

    // Debouncing refs
    const debounceTimeouts = useRef({})
    const pendingOperations = useRef({})
    const addressLoadTimestamp = useRef(0) // Track when addresses were last loaded

    // Load addresses
    const loadAddresses = useCallback(async () => {
        // Prevent multiple simultaneous calls
        if(isAddressesLoading) {
            console.log('🛒 CartPage: Address loading already in progress, skipping...')
            return
        }

        // Prevent loading too frequently (within 1 second)
        const now = Date.now()
        if(now - addressLoadTimestamp.current < 1000) {
            console.log('🛒 CartPage: Address loading too frequent, skipping...')
            return
        }

        try {
            setIsAddressesLoading(true)
            addressLoadTimestamp.current = now
            console.log('🛒 CartPage: Loading addresses...')
            const response = await apiService.getAddresses()
            console.log('🛒 CartPage: Address API response:', response)
            console.log('🛒 CartPage: Address API response type:', typeof response)
            console.log('🛒 CartPage: Address API response length:', Array.isArray(response) ? response.length : 'Not an array')

            if(Array.isArray(response)) {
                // Debug: Check for duplicate IDs
                const ids = response.map(addr => addr.id)
                const uniqueIds = [...new Set(ids)]
                console.log('🛒 CartPage: Address IDs:', ids)
                console.log('🛒 CartPage: Unique Address IDs:', uniqueIds)
                console.log('🛒 CartPage: Duplicate IDs found:', ids.length !== uniqueIds.length)

                // Remove duplicates if any (defensive programming)
                const uniqueAddresses = response.filter((addr, index, self) =>
                    index === self.findIndex(a => a.id === addr.id)
                )

                // Additional check: remove addresses with duplicate content
                const contentFilteredAddresses = uniqueAddresses.filter((addr, index, self) => {
                    const firstIndex = self.findIndex(a =>
                        a.full_name === addr.full_name &&
                        a.phone_number === addr.phone_number &&
                        a.address_line_1 === addr.address_line_1 &&
                        a.city === addr.city
                    );
                    return firstIndex === index;
                });

                console.log('🛒 CartPage: After content deduplication:', contentFilteredAddresses.length, 'addresses');

                // Only update if addresses have actually changed
                const currentAddressIds = addresses.map(a => a.id).sort()
                const newAddressIds = contentFilteredAddresses.map(a => a.id).sort()

                if(JSON.stringify(currentAddressIds) !== JSON.stringify(newAddressIds)) {
                    console.log('🛒 CartPage: Addresses changed, updating state')
                    setAddresses(contentFilteredAddresses)
                    // Auto-select default address if available and none selected
                    if(!selectedAddressId) {
                        const defaultAddr = contentFilteredAddresses.find(addr => addr.is_default)
                        if(defaultAddr) {
                            setSelectedAddressId(defaultAddr.id)
                        }
                    }
                } else {
                    console.log('🛒 CartPage: Addresses unchanged, skipping state update')
                }
            } else {
                setAddresses([])
            }
            setHasLoadedAddresses(true)
        } catch(error) {
            console.error('❌ CartPage: Error loading addresses:', error)
            setAddresses([])
        } finally {
            setIsAddressesLoading(false)
        }
    }, [isAddressesLoading, addresses, selectedAddressId])

    // Fetch cart and addresses
    useEffect(() => {
        const fetchCart = async () => {
            // Check if cart was cleared (sessionStorage count is 0)
            const storedCount = sessionStorage.getItem('cartCount')
            if(storedCount && parseInt(storedCount) === 0) {
                console.log('🛒 CartPageFull: Cart was cleared, skipping API call to prevent new cart creation')
                setCart(null)
                setLoading(false)
                return
            }

            setLoading(true)
            try {
                const response = await apiService.getCart()
                if(response.success) {
                    setCart(response.cart)
                } else {
                    setError("Failed to load cart")
                }
            } catch(err) {
                setError("Failed to load cart")
            } finally {
                setLoading(false)
            }
        }
        fetchCart()

        // Only load addresses if not already loaded
        if(!hasLoadedAddresses) {
            console.log('🛒 CartPage: Loading addresses for the first time')
            loadAddresses()
        } else {
            console.log('🛒 CartPage: Addresses already loaded, skipping initial load')
        }
    }, [loadAddresses, hasLoadedAddresses])

    // Listen for cart updates to refresh addresses
    useEffect(() => {
        const handleCartUpdate = () => {
            console.log('🛒 CartPage: Received cartUpdated event')
            // Small delay to ensure backend has processed the update
            setTimeout(() => {
                // Only reload if not already loading and not too frequent
                const now = Date.now()
                if(!isAddressesLoading && (now - addressLoadTimestamp.current > 2000)) {
                    console.log('🛒 CartPage: Reloading addresses due to cart update')
                    loadAddresses()
                } else {
                    console.log('🛒 CartPage: Skipping address reload due to cart update - too frequent or already loading')
                }
            }, 300)
        }

        window.addEventListener('cartUpdated', handleCartUpdate)
        return () => {
            window.removeEventListener('cartUpdated', handleCartUpdate)
        }
    }, [loadAddresses, isAddressesLoading])

    // Cleanup debounce timeouts on unmount
    useEffect(() => {
        return () => {
            // Clear all pending timeouts
            Object.values(debounceTimeouts.current).forEach(timeout => {
                if(timeout) clearTimeout(timeout)
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

    // Address handling functions
    const handleAddressSelect = useCallback((addressId) => {
        setSelectedAddressId(addressId)
        setShowNewAddressForm(false)
    }, [])

    const handleNewAddressSubmit = useCallback(async (e) => {
        e.preventDefault()

        if(isSubmittingAddress) {
            return
        }

        setIsSubmittingAddress(true)

        try {
            console.log('🛒 CartPage: Creating new address:', newAddressForm)
            const response = await apiService.createAddress(newAddressForm)
            console.log('🛒 CartPage: Address creation response:', response)

            if(response && response.id) {
                // Reload addresses and select the new one
                await loadAddresses()
                setSelectedAddressId(response.id)
                setShowNewAddressForm(false)
                setNewAddressForm({
                    full_name: '',
                    phone_number: '',
                    city: '',
                    address_line_1: '',
                    address_line_2: '',
                    postal_code: '',
                    country: 'Bangladesh',
                    address_type: 'home',
                    is_default: false
                })
            }
        } catch(error) {
            console.error('❌ CartPage: Address creation error:', error)
        } finally {
            setIsSubmittingAddress(false)
        }
    }, [newAddressForm, loadAddresses, isSubmittingAddress])

    const handleNewAddressInputChange = useCallback((e) => {
        setNewAddressForm(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }))
    }, [])

    // Place order function
    const handlePlaceOrder = async () => {
        if(!cart || !cart.items || cart.items.length === 0) {
            setError("Cart is empty")
            return
        }

        // Validate address selection
        if(!selectedAddressId) {
            setError("Please select a delivery address")
            return
        }

        setIsPlacingOrder(true)
        setError(null)

        try {
            // Get selected address
            const selectedAddress = addresses.find(addr => addr.id === selectedAddressId)
            if(!selectedAddress) {
                setError("Selected address not found")
                return
            }

            const orderData = {
                address: {
                    full_name: selectedAddress.full_name,
                    phone_number: selectedAddress.phone_number,
                    city: selectedAddress.city,
                    address_line_1: selectedAddress.address_line_1,
                    address_line_2: selectedAddress.address_line_2,
                    postal_code: selectedAddress.postal_code,
                    country: selectedAddress.country
                },
                payment_method: orderForm.paymentMethod,
                notes: ''
            }

            const response = await apiService.placeOrder(orderData)

            if(response.success) {
                // Order placed successfully
                setOrderData(response.order)
                setShowInvoice(true)
                // Clear cart
                setCart(null)
                sessionStorage.removeItem('cartCount')
                // Dispatch cart updated event
                window.dispatchEvent(new CustomEvent('cartUpdated'))
            } else {
                setError(response.message || "Failed to place order")
            }
        } catch(err) {
            console.error("Order placement error:", err)
            setError("Failed to place order. Please try again.")
        } finally {
            setIsPlacingOrder(false)
        }
    }

    // Clear cart function
    const handleClearCart = async () => {
        try {
            const response = await apiService.clearCart()
            if(response.success) {
                if(response.cart === null) {
                    // Cart was deleted (both guest and user carts)
                    setCart(null)
                    sessionStorage.setItem('cartCount', '0') // Set to 0 instead of removing
                    console.log('🛒 CartPageFull: Cart cleared, set sessionStorage to 0')
                } else {
                    // Cart still exists (this should not happen with our new logic)
                    setCart(response.cart)
                    sessionStorage.setItem('cartCount', response.cart.total_items || 0)
                }
                window.dispatchEvent(new CustomEvent('cartUpdated'))
                setShowClearConfirm(false)
            } else {
                setError("Failed to clear cart")
            }
        } catch(err) {
            console.error("Clear cart error:", err)
            setError("Failed to clear cart. Please try again.")
        }
    }

    // Format price in BDT
    const formatPrice = (amount) => {
        const safeAmount = Number(amount || 0)
        try {
            return new Intl.NumberFormat('en-BD', {style: 'currency', currency: 'BDT', minimumFractionDigits: 0}).format(safeAmount)
        } catch(e) {
            return `৳${safeAmount.toLocaleString('en-BD')}`
        }
    }

    const getProductImage = (item) => {
        if(item.product && item.product.primary_image) {
            const primaryImage = item.product.primary_image
            if(primaryImage.image_url) {
                if(primaryImage.image_url.startsWith('http')) {
                    return primaryImage.image_url
                }
                return `http://127.0.0.1:8000${primaryImage.image_url}`
            }
            if(primaryImage.image) {
                if(primaryImage.image.startsWith('http')) {
                    return primaryImage.image
                }
                return `http://127.0.0.1:8000${primaryImage.image}`
            }
        }
        return "/assets/images/products/1.jpg"
    }

    // Cart item management functions
    const handleRemoveItem = async (itemId) => {
        console.log('🛒 CartPage: Removing item with ID:', itemId);
        setUpdatingItems(prev => ({...prev, [itemId]: true}));

        try {
            const response = await apiService.removeCartItem(itemId);
            console.log('🛒 CartPage: Remove item response:', response);

            if(response.success) {
                if(response.cart === null) {
                    // Cart was deleted (both guest and user carts)
                    setCart(null);
                    sessionStorage.setItem('cartCount', '0'); // Set to 0 instead of removing
                    console.log('🛒 CartPageFull: Item removed, cart deleted, set sessionStorage to 0');
                } else {
                    // Cart still exists (authenticated user)
                    setCart(response.cart);
                    sessionStorage.setItem('cartCount', response.cart.total_items || 0);
                }
                // Dispatch cart updated event
                window.dispatchEvent(new CustomEvent('cartUpdated'));
            } else {
                setError("Failed to remove item from cart");
            }
        } catch(error) {
            console.error('❌ CartPage: Error removing item:', error);
            setError("Failed to remove item from cart. Please try again.");
        } finally {
            setUpdatingItems(prev => ({...prev, [itemId]: false}));
        }
    }

    const handleIncreaseQuantity = async (itemId) => {
        console.log('🛒 CartPage: Increasing quantity for item ID:', itemId);
        setUpdatingItems(prev => ({...prev, [itemId]: true}));

        try {
            const response = await apiService.increaseCartItemQuantity(itemId);
            console.log('🛒 CartPage: Increase quantity response:', response);

            if(response.success) {
                // Check if cart was deleted
                if(response.cart === null) {
                    // Cart was deleted (both guest and user carts)
                    setCart(null);
                    sessionStorage.setItem('cartCount', '0'); // Set to 0 instead of removing
                    console.log('🛒 CartPageFull: Quantity increased, cart deleted, set sessionStorage to 0');
                } else {
                    // Cart still exists, refresh cart data
                    setCart(response.cart);
                    sessionStorage.setItem('cartCount', response.cart.total_items || 0);
                }
                // Dispatch cart updated event
                window.dispatchEvent(new CustomEvent('cartUpdated'));
            } else {
                setError("Failed to update quantity");
            }
        } catch(error) {
            console.error('❌ CartPage: Error increasing quantity:', error);
            setError("Failed to update quantity. Please try again.");
        } finally {
            setUpdatingItems(prev => ({...prev, [itemId]: false}));
        }
    }

    const handleDecreaseQuantity = async (itemId) => {
        console.log('🛒 CartPage: Decreasing quantity for item ID:', itemId);
        setUpdatingItems(prev => ({...prev, [itemId]: true}));

        try {
            const response = await apiService.decreaseCartItemQuantity(itemId);
            console.log('🛒 CartPage: Decrease quantity response:', response);

            if(response.success) {
                if(response.cart === null) {
                    // Cart was deleted (both guest and user carts)
                    setCart(null);
                    sessionStorage.setItem('cartCount', '0'); // Set to 0 instead of removing
                    console.log('🛒 CartPageFull: Quantity decreased, cart deleted, set sessionStorage to 0');
                } else {
                    // Cart still exists (authenticated user)
                    setCart(response.cart);
                    sessionStorage.setItem('cartCount', response.cart.total_items || 0);
                }
                // Dispatch cart updated event
                window.dispatchEvent(new CustomEvent('cartUpdated'));
            } else {
                setError("Failed to update quantity");
            }
        } catch(error) {
            console.error('❌ CartPage: Error decreasing quantity:', error);
            setError("Failed to update quantity. Please try again.");
        } finally {
            setUpdatingItems(prev => ({...prev, [itemId]: false}));
        }
    }

    return (
        <div className="cart-page-full">
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
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 10000
                }}>
                    <div style={{
                        backgroundColor: 'white',
                        padding: '30px',
                        borderRadius: '12px',
                        maxWidth: '400px',
                        width: '90%',
                        textAlign: 'center',
                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                    }}>
                        <div style={{fontSize: '48px', marginBottom: '16px'}}>🗑️</div>
                        <h3 style={{marginBottom: '16px', color: '#374151'}}>Clear Cart?</h3>
                        <p style={{marginBottom: '24px', color: '#6b7280'}}>
                            Are you sure you want to remove all items from your cart? This action cannot be undone.
                        </p>
                        <div style={{display: 'flex', gap: '12px', justifyContent: 'center'}}>
                            <button
                                onClick={() => setShowClearConfirm(false)}
                                style={{
                                    padding: '10px 20px',
                                    border: '1px solid #d1d5db',
                                    borderRadius: '6px',
                                    background: '#fff',
                                    color: '#374151',
                                    cursor: 'pointer',
                                    fontSize: '14px',
                                    fontWeight: '500'
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleClearCart}
                                style={{
                                    padding: '10px 20px',
                                    border: 'none',
                                    borderRadius: '6px',
                                    background: '#ef4444',
                                    color: '#fff',
                                    cursor: 'pointer',
                                    fontSize: '14px',
                                    fontWeight: '500'
                                }}
                            >
                                Clear Cart
                            </button>
                        </div>
                    </div>
                </div>
            )}


            <div className="cart-page-content">
                <div className="container">
                    {loading ? (
                        <div className="loading">Loading cart...</div>
                    ) : error ? (
                        <div className="error">{error}</div>
                    ) : !cart || !cart.items || cart.items.length === 0 ? (
                        <div className="empty-cart">
                            <div className="empty-cart-content">
                                <div className="empty-cart-icon">🛒</div>
                                <h3>Your cart is empty</h3>
                                <p>Add some items to get started!</p>
                                <button
                                    className="continue-shopping-btn"
                                    onClick={() => window.location.href = '/'}
                                    style={{
                                        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                                        color: '#fff',
                                        border: 'none',
                                        padding: '12px 24px',
                                        borderRadius: '8px',
                                        fontSize: '16px',
                                        fontWeight: '600',
                                        cursor: 'pointer',
                                        boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)',
                                        transition: 'all 0.3s ease'
                                    }}
                                >
                                    🛍️ Start Shopping →
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="cart-layout">
                            {/* Left Column - Order Summary */}
                            <div className="cart-left-column">
                                <h2>Order Summary</h2>

                                {cart?.items && cart.items.length > 0 ? (
                                    <div className="order-items">
                                        {cart.items.map((item) => (
                                            <div key={item.id} className="order-item">
                                                <img
                                                    src={getProductImage(item)}
                                                    alt={item.product?.title || 'Product'}
                                                    onError={(e) => {e.target.src = "/assets/images/products/1.jpg"}}
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
                                                            onClick={() => {
                                                                handleDecreaseQuantity(item.id);
                                                            }}
                                                            disabled={updatingItems[item.id] || item.quantity <= 1}
                                                        >-</button>
                                                        <span>{updatingItems[item.id] ? '...' : item.quantity}</span>
                                                        <button
                                                            onClick={() => {
                                                                handleIncreaseQuantity(item.id);
                                                            }}
                                                            disabled={updatingItems[item.id] || !item.can_increase}
                                                        >+</button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}

                                        {/* Clear Cart Button */}
                                        <div style={{marginTop: '20px'}}>
                                            <button
                                                className="clear-cart-btn"
                                                onClick={() => setShowClearConfirm(true)}
                                                disabled={loading}
                                                style={{
                                                    width: '100%',
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
                                            >
                                                {loading ? '🗑️ Clearing...' : '🗑️ Clear Cart'}
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="cart-summary" style={{textAlign: 'center', color: '#6b7280'}}>
                                        No items in cart
                                    </div>
                                )}
                            </div>

                            {/* Right Column - Checkout */}
                            <div className="cart-right-column">
                                <h2>
                                    Shopping Cart{" "}
                                    <span style={{color: "#6366f1", fontSize: "14px"}}>
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
                                    <div className="cart-summary" style={{textAlign: 'center', color: '#6b7280'}}>
                                        No items in cart
                                    </div>
                                )}

                                {/* Address Section */}
                                <div className="address-section">
                                    <div className="address-section-header">
                                        <h3 style={{color: '#333', fontSize: '16px', fontWeight: '600', margin: 0}}>
                                            Delivery Address
                                        </h3>
                                        <button
                                            className="address-toggle-btn"
                                            onClick={() => setIsAddressSectionExpanded(!isAddressSectionExpanded)}
                                        >
                                            {isAddressSectionExpanded ? 'Hide' : 'Show'}
                                        </button>
                                    </div>

                                    {/* Address Content (collapsible) */}
                                    <div className={`address-content ${isAddressSectionExpanded ? 'expanded' : 'collapsed'}`}>
                                        {addresses.length > 0 ? (
                                            <div className="address-buttons">
                                                {(() => {
                                                    // Debug: Log all addresses before rendering
                                                    console.log('🛒 CartPage: Rendering addresses list:', addresses);
                                                    const uniqueAddresses = addresses.filter((addr, index, self) =>
                                                        index === self.findIndex(a => a.id === addr.id)
                                                    );
                                                    console.log('🛒 CartPage: Unique addresses for rendering:', uniqueAddresses);

                                                    return uniqueAddresses.map((address, index) => {
                                                        console.log('Rendering address:', address.id, address)
                                                        return (
                                                            <div
                                                                key={`${address.id}-${index}`}  // Added index to ensure unique key
                                                                className={`address-card ${selectedAddressId === address.id ? 'selected' : ''}`}
                                                                onClick={() => handleAddressSelect(address.id)}
                                                            >
                                                                <div className="address-card-header">
                                                                    <div className="address-icon">
                                                                        {address.address_type === 'home' ? '🏠' : '🏢'}
                                                                    </div>
                                                                    <div className="address-title">
                                                                        {address.address_type === 'home' ? 'Home Address' : 'Office Address'}
                                                                        {address.is_default && <span className="default-badge">Default</span>}
                                                                    </div>
                                                                    {selectedAddressId === address.id && (
                                                                        <div className="selected-indicator">✓</div>
                                                                    )}
                                                                </div>
                                                                <div className="address-card-body">
                                                                    <div className="address-name">{address.full_name}</div>
                                                                    <div className="address-location">
                                                                        {address.address_line_1}
                                                                        {address.address_line_2 && `, ${address.address_line_2}`}
                                                                        <br />
                                                                        {address.city}, {address.postal_code}
                                                                        <br />
                                                                        {address.country}
                                                                    </div>
                                                                    <div className="address-phone">📱 {address.phone_number}</div>
                                                                </div>
                                                            </div>
                                                        )
                                                    })
                                                })()}
                                            </div>
                                        ) : (
                                            <div className="no-addresses">
                                                <div className="no-addresses-icon">🏠</div>
                                                <p className="no-addresses-text">
                                                    No saved addresses found. Please add a delivery address.
                                                </p>
                                            </div>
                                        )}
                                    </div>

                                    {/* Add New Address Section (always visible) */}
                                    {addresses.length > 0 ? (
                                        <div className="add-address-card" style={{marginTop: '20px'}} onClick={() => setShowNewAddressForm(true)}>
                                            <div className="add-address-icon">➕</div>
                                            <div className="add-address-title">Add New Address</div>
                                            <div className="add-address-subtitle">Create a new delivery address</div>
                                            <button
                                                className="add-address-btn"
                                                onClick={(e) => {
                                                    e.stopPropagation()
                                                    setShowNewAddressForm(true)
                                                }}
                                            >
                                                ADD NEW
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="add-first-address-container" style={{textAlign: 'center', marginTop: '20px'}}>
                                            <button
                                                type="button"
                                                onClick={() => setShowNewAddressForm(true)}
                                                className="add-first-address-btn"
                                                style={{
                                                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                                                    color: 'white',
                                                    border: 'none',
                                                    padding: '12px 24px',
                                                    borderRadius: '8px',
                                                    fontSize: '14px',
                                                    fontWeight: '600',
                                                    cursor: 'pointer',
                                                    boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)',
                                                    transition: 'all 0.3s ease'
                                                }}
                                            >
                                                ➕ Add Your First Address
                                            </button>
                                        </div>
                                    )}
                                </div>

                                {/* New Address Form (always visible when showNewAddressForm is true) */}
                                {showNewAddressForm && (
                                    <div className="new-address-form" style={{
                                        marginTop: '20px',
                                        padding: '20px',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '8px',
                                        background: '#f9fafb',
                                        position: 'relative'
                                    }}>
                                        <button
                                            type="button"
                                            onClick={() => setShowNewAddressForm(false)}
                                            style={{
                                                position: 'absolute',
                                                top: '10px',
                                                right: '10px',
                                                background: 'none',
                                                border: 'none',
                                                fontSize: '20px',
                                                cursor: 'pointer',
                                                color: '#999'
                                            }}
                                        >
                                            ×
                                        </button>
                                        <h4 style={{marginBottom: '15px', color: '#333'}}>Add New Address</h4>
                                        <form onSubmit={handleNewAddressSubmit}>
                                            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px'}}>
                                                <div>
                                                    <label style={{display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500'}}>
                                                        Full Name *
                                                    </label>
                                                    <input
                                                        type="text"
                                                        name="full_name"
                                                        value={newAddressForm.full_name}
                                                        onChange={handleNewAddressInputChange}
                                                        required
                                                        style={{width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '6px'}}
                                                    />
                                                </div>
                                                <div>
                                                    <label style={{display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500'}}>
                                                        Phone Number *
                                                    </label>
                                                    <input
                                                        type="tel"
                                                        name="phone_number"
                                                        value={newAddressForm.phone_number}
                                                        onChange={handleNewAddressInputChange}
                                                        required
                                                        style={{width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '6px'}}
                                                    />
                                                </div>
                                            </div>

                                            <div style={{marginBottom: '15px'}}>
                                                <label style={{display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500'}}>
                                                    Address Line 1 *
                                                </label>
                                                <input
                                                    type="text"
                                                    name="address_line_1"
                                                    value={newAddressForm.address_line_1}
                                                    onChange={handleNewAddressInputChange}
                                                    required
                                                    style={{width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '6px'}}
                                                />
                                            </div>

                                            <div style={{marginBottom: '15px'}}>
                                                <label style={{display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500'}}>
                                                    Address Line 2
                                                </label>
                                                <input
                                                    type="text"
                                                    name="address_line_2"
                                                    value={newAddressForm.address_line_2}
                                                    onChange={handleNewAddressInputChange}
                                                    style={{width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '6px'}}
                                                />
                                            </div>

                                            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px', marginBottom: '15px'}}>
                                                <div>
                                                    <label style={{display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500'}}>
                                                        City *
                                                    </label>
                                                    <input
                                                        type="text"
                                                        name="city"
                                                        value={newAddressForm.city}
                                                        onChange={handleNewAddressInputChange}
                                                        required
                                                        style={{width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '6px'}}
                                                    />
                                                </div>
                                                <div>
                                                    <label style={{display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500'}}>
                                                        Postal Code *
                                                    </label>
                                                    <input
                                                        type="text"
                                                        name="postal_code"
                                                        value={newAddressForm.postal_code}
                                                        onChange={handleNewAddressInputChange}
                                                        required
                                                        style={{width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '6px'}}
                                                    />
                                                </div>
                                                <div>
                                                    <label style={{display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500'}}>
                                                        Country *
                                                    </label>
                                                    <select
                                                        name="country"
                                                        value={newAddressForm.country}
                                                        onChange={handleNewAddressInputChange}
                                                        required
                                                        style={{width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '6px'}}
                                                    >
                                                        <option value="Bangladesh">Bangladesh</option>
                                                    </select>
                                                </div>
                                            </div>

                                            <div style={{display: 'flex', gap: '10px', justifyContent: 'flex-end'}}>
                                                <button
                                                    type="button"
                                                    onClick={() => setShowNewAddressForm(false)}
                                                    style={{
                                                        padding: '10px 20px',
                                                        border: '1px solid #d1d5db',
                                                        borderRadius: '6px',
                                                        background: '#fff',
                                                        color: '#374151',
                                                        cursor: 'pointer'
                                                    }}
                                                >
                                                    Cancel
                                                </button>
                                                <button
                                                    type="submit"
                                                    disabled={isSubmittingAddress}
                                                    style={{
                                                        padding: '10px 20px',
                                                        border: 'none',
                                                        borderRadius: '6px',
                                                        background: isSubmittingAddress ? '#9ca3af' : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                                                        color: '#fff',
                                                        cursor: isSubmittingAddress ? 'not-allowed' : 'pointer'
                                                    }}
                                                >
                                                    {isSubmittingAddress ? 'Adding...' : 'Add Address'}
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                )}

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

                                {/* Actions */}
                                <div className="actions">
                                    <button className="btn cancel" onClick={() => window.location.href = '/'}>Continue Shopping</button>
                                    <button
                                        className="btn order"
                                        onClick={handlePlaceOrder}
                                        disabled={
                                            !cart ||
                                            !cart.items ||
                                            cart.items.length === 0 ||
                                            isPlacingOrder ||
                                            !selectedAddressId
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
            {showInvoice && orderData && (
                <InvoiceModal
                    order={orderData}
                    onClose={() => setShowInvoice(false)}
                />
            )}

            <style jsx>{`
        .cart-page-full {
          min-height: 100vh;
          background: #f9fafb;
        }

        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
        }

        .cart-page-header {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 40px 0;
          text-align: center;
        }

        .cart-page-title h1 {
          font-size: 2.5rem;
          margin: 0 0 10px 0;
          font-weight: 700;
        }

        .cart-page-title p {
          font-size: 1.1rem;
          margin: 0;
          opacity: 0.9;
        }

        .cart-page-content {
          padding: 40px 0;
        }

        .cart-layout {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 40px;
          align-items: start;
        }

        .cart-left-column,
        .cart-right-column {
          background: white;
          border-radius: 12px;
          padding: 30px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .cart-left-column h2,
        .cart-right-column h2 {
          margin: 0 0 20px 0;
          color: #374151;
          font-size: 1.5rem;
          font-weight: 600;
        }

        .order-items {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .order-item {
          display: flex;
          gap: 15px;
          padding: 15px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          background: #f9fafb;
        }

        .order-item img {
          width: 80px;
          height: 80px;
          object-fit: cover;
          border-radius: 6px;
        }

        .item-info {
          flex: 1;
        }

        .item-info h4 {
          margin: 0 0 5px 0;
          font-size: 1rem;
          font-weight: 600;
          color: #374151;
        }

        .item-info p {
          margin: 0 0 10px 0;
          font-size: 0.9rem;
          color: #6b7280;
        }

        .remove-btn {
          background: #ef4444;
          color: white;
          border: none;
          padding: 5px 10px;
          border-radius: 4px;
          font-size: 0.8rem;
          cursor: pointer;
        }

        .order-price {
          font-weight: 600;
          color: #374151;
          margin-bottom: 10px;
        }

        .qty-control {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .qty-control button {
          width: 30px;
          height: 30px;
          border: 1px solid #d1d5db;
          background: white;
          border-radius: 4px;
          cursor: pointer;
        }

        .cart-summary {
          background: #f9fafb;
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .cart-summary div {
          display: flex;
          justify-content: space-between;
          margin-bottom: 10px;
        }

        .cart-summary .total {
          font-weight: 600;
          font-size: 1.1rem;
          border-top: 1px solid #e5e7eb;
          padding-top: 10px;
          margin-top: 10px;
        }

        /* Address Section Styles */
        .address-section {
          border: 1px solid #eee;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
          background: #fff;
        }

        .address-section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }

        .address-toggle-btn {
          background: none;
          border: none;
          color: #6366f1;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          padding: 5px 10px;
          border-radius: 4px;
          transition: all 0.2s ease;
        }

        .address-toggle-btn:hover {
          background: #f0f0ff;
        }

        .address-content {
          transition: all 0.3s ease;
          overflow: hidden;
        }

        .address-content.collapsed {
          max-height: 0;
          opacity: 0;
          margin-bottom: 0;
        }

        .address-content.expanded {
          max-height: 1000px;
          opacity: 1;
        }

        /* Address Buttons Styles */
        .address-buttons {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
        }

        .address-card {
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          padding: 20px;
          background: #fff;
          cursor: pointer;
          transition: all 0.3s ease;
          position: relative;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .address-card:hover {
          border-color: #6366f1;
          box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2);
          transform: translateY(-2px);
        }

        .address-card.selected {
          border-color: #6366f1;
          background: linear-gradient(135deg, #f0f0ff 0%, #e0e7ff 100%);
          box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
        }

        .address-card-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 15px;
        }

        .address-icon {
          font-size: 24px;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f3f4f6;
          border-radius: 8px;
        }

        .address-card.selected .address-icon {
          background: #6366f1;
          color: white;
        }

        .address-title {
          flex: 1;
          font-weight: 600;
          font-size: 16px;
          color: #374151;
        }

        .default-badge {
          font-size: 12px;
          color: #6366f1;
          background: #f0f0ff;
          padding: 2px 8px;
          border-radius: 4px;
          margin-left: 8px;
          font-weight: 500;
        }

        .selected-indicator {
          color: #6366f1;
          font-size: 20px;
          font-weight: bold;
        }

        .address-card-body {
          margin-bottom: 15px;
        }

        .address-name {
          font-weight: 600;
          font-size: 16px;
          color: #111827;
          margin-bottom: 8px;
        }

        .address-location {
          font-size: 14px;
          color: #6b7280;
          line-height: 1.5;
          margin-bottom: 8px;
        }

        .address-phone {
          font-size: 14px;
          color: #6b7280;
          font-weight: 500;
        }

        .address-card-footer {
          display: flex;
          justify-content: center;
        }

        .select-btn {
          background: #f3f4f6;
          color: #374151;
          border: none;
          padding: 8px 20px;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .select-btn:hover {
          background: #e5e7eb;
        }

        .select-btn.selected {
          background: #6366f1;
          color: white;
        }

        /* Add Address Card */
        .add-address-card {
          border: 2px dashed #d1d5db;
          border-radius: 12px;
          padding: 30px 20px;
          background: #f9fafb;
          cursor: pointer;
          transition: all 0.3s ease;
          text-align: center;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
        }

        .add-address-card:hover {
          border-color: #6366f1;
          background: #f0f0ff;
          transform: translateY(-2px);
        }

        .add-address-icon {
          font-size: 32px;
          color: #6366f1;
        }

        .add-address-title {
          font-weight: 600;
          font-size: 16px;
          color: #374151;
        }

        .add-address-subtitle {
          font-size: 14px;
          color: #6b7280;
        }

        .add-address-btn {
          background: #6366f1;
          color: white;
          border: none;
          padding: 10px 24px;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .add-address-btn:hover {
          background: #4f46e5;
          transform: translateY(-1px);
        }

        .no-addresses {
          text-align: center;
          padding: 40px 20px;
          color: #666;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
        }

        .no-addresses-icon {
          font-size: 48px;
          opacity: 0.6;
        }

        .no-addresses-text {
          font-size: 16px;
          color: #6b7280;
          margin: 0;
        }

        .add-first-address-btn {
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }

        .add-first-address-btn:hover {
          background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        }

        .payment-options {
          border: 1px solid #eee;
          border-radius: 8px;
          padding: 15px;
          margin-bottom: 20px;
          background: #fff;
        }

        .payment-options label {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 10px;
          cursor: pointer;
          font-size: 14px;
          color: #333;
        }

        .payment-options input[type="radio"] {
          accent-color: #6366f1;
          width: 16px;
          height: 16px;
        }

        .actions {
          display: flex;
          justify-content: flex-end;
          gap: 15px;
          margin-top: 20px;
        }

        .btn {
          padding: 12px 20px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: bold;
          font-size: 14px;
        }

        .btn.cancel {
          background: #f3f4f6;
          color: #374151;
        }

        .btn.order {
          background: #6366f1;
          color: #fff;
        }

        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .empty-cart {
          text-align: center;
          padding: 60px 20px;
        }

        .empty-cart-content {
          max-width: 400px;
          margin: 0 auto;
        }

        .empty-cart-icon {
          font-size: 64px;
          margin-bottom: 20px;
        }

        .empty-cart h3 {
          font-size: 1.5rem;
          margin-bottom: 10px;
          color: #374151;
        }

        .empty-cart p {
          color: #6b7280;
          margin-bottom: 30px;
        }

        .loading {
          text-align: center;
          padding: 40px;
          color: #6b7280;
        }

        .error {
          text-align: center;
          padding: 40px;
          color: #ef4444;
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: 8px;
          margin: 20px 0;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .cart-layout {
            grid-template-columns: 1fr;
            gap: 20px;
          }

          .cart-left-column,
          .cart-right-column {
            padding: 20px;
          }

          .cart-page-title h1 {
            font-size: 2rem;
          }

          .address-buttons {
            grid-template-columns: 1fr;
            gap: 15px;
          }

          .address-card {
            padding: 15px;
          }

          .add-address-card {
            padding: 20px 15px;
          }

          .actions {
            flex-direction: column;
          }

          .btn {
            width: 100%;
          }
        }
      `}</style>
        </div>
    )
}

export default CartPageFull
