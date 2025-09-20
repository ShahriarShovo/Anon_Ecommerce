import React, {useState, useEffect} from 'react'
import apiService from '../services/api'
import SuccessNotification from './SuccessNotification'
import ErrorNotification from './ErrorNotification'
import {useAuth} from '../contexts/AuthContext'
import {LoginModal} from './authentication'

const SingleProduct = () => {
  // Get slug from URL path
  const currentPath = window.location.pathname
  const slug = currentPath.split('/product/')[1]

  // Get authentication context
  const {user, isAuthenticated} = useAuth()

  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedImage, setSelectedImage] = useState(0)
  const [selectedVariant, setSelectedVariant] = useState(null)
  const [reviews, setReviews] = useState([])
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [addingToCart, setAddingToCart] = useState(false)
  const [quantity, setQuantity] = useState(1)
  const [showSuccessNotification, setShowSuccessNotification] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [showErrorNotification, setShowErrorNotification] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    title: '',
    comment: '',
    user_name: '',
    user_email: ''
  })

  useEffect(() => {
    if(slug) {
      fetchProduct()
      fetchReviews()
    }
  }, [slug])

  // Pre-fill review form with user data when authenticated
  useEffect(() => {
    if(isAuthenticated && user) {
      setReviewForm(prev => ({
        ...prev,
        user_name: user.full_name || user.email || '',
        user_email: user.email || ''
      }))

      // If user just logged in and auth modal was open, open review form
      if(showAuthModal) {
        setShowAuthModal(false)
        setShowReviewForm(true)
      }
    }
  }, [isAuthenticated, user, showAuthModal])

  const fetchProduct = async () => {
    try {
      setLoading(true)
      const response = await apiService.getSingleProduct(slug)

      if(response.success) {
        console.log('🌟 Product data received:', response.product)
        console.log('🌟 Product average_rating:', response.product.average_rating)
        setProduct(response.product)
        // Set first variant as default if available
        if(response.product.variants && response.product.variants.length > 0) {
          setSelectedVariant(response.product.variants[0])
        }
      } else {
        throw new Error(response.error || 'Failed to fetch product')
      }
    } catch(error) {
      console.error('Error fetching product:', error)
      setError('Failed to load product')
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (price) => {
    if(typeof price === 'string') return price
    return `$${parseFloat(price).toFixed(2)}`
  }

  const fetchReviews = async () => {
    try {
      const response = await apiService.getProductReviews(slug)
      if(response.success) {
        console.log('🌟 Reviews API response:', response)
        setReviews(response.reviews)
        // Update product with rating from reviews API
        if(response.average_rating !== undefined) {
          setProduct(prev => prev ? {...prev, average_rating: response.average_rating} : null)
        }
      }
    } catch(error) {
      console.error('Error fetching reviews:', error)
    }
  }

  const handleVariantChange = (variant) => {
    setSelectedVariant(variant)
  }

  const handleQuantityIncrease = () => {
    setQuantity(prev => {
      const maxQuantity = selectedVariant?.quantity || product?.quantity || 100
      const newQuantity = Math.min(prev + 1, maxQuantity)
      console.log('🛒 SingleProduct: Quantity increased to:', newQuantity, '(max:', maxQuantity, ')')
      return newQuantity
    })
  }

  const handleQuantityDecrease = () => {
    setQuantity(prev => {
      const newQuantity = Math.max(1, prev - 1)
      console.log('🛒 SingleProduct: Quantity decreased to:', newQuantity)
      return newQuantity
    })
  }

  const handleQuantityChange = (e) => {
    const value = parseInt(e.target.value) || 1
    const maxQuantity = selectedVariant?.quantity || product?.quantity || 100
    const newQuantity = Math.max(1, Math.min(value, maxQuantity))
    console.log('🛒 SingleProduct: Quantity changed to:', newQuantity, '(max:', maxQuantity, ')')
    setQuantity(newQuantity)
  }

  const handleReviewSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await apiService.createProductReview(slug, reviewForm)
      if(response.success) {
        setShowReviewForm(false)
        setReviewForm({
          rating: 5,
          title: '',
          comment: '',
          user_name: isAuthenticated ? (user?.full_name || user?.email || '') : '',
          user_email: isAuthenticated ? (user?.email || '') : ''
        })
        fetchReviews() // Refresh reviews
        alert('Review submitted successfully!')
      }
    } catch(error) {
      console.error('Error submitting review:', error)
      alert('Failed to submit review. Please try again.')
    }
  }

  const handleReviewInputChange = (e) => {
    const {name, value} = e.target
    setReviewForm(prev => ({
      ...prev,
      [name]: value
    }))
  }

  // Add to cart function
  const handleAddToCart = async () => {
    if(!product) return

    try {
      setAddingToCart(true)

      // Debug: Log the data being sent
      console.log('🛒 SingleProduct: Adding to cart with data:', {
        product_id: product.id,
        quantity: quantity,
        variant_id: selectedVariant ? selectedVariant.id : null,
        product_title: product.title
      })

      const response = await apiService.addToCart(
        product.id,
        quantity,
        selectedVariant ? selectedVariant.id : null
      )

      console.log('🛒 SingleProduct: Add to cart API response:', response)

      if(response.success) {
        // Update sessionStorage
        const currentCount = parseInt(sessionStorage.getItem('cartCount') || '0')
        sessionStorage.setItem('cartCount', (currentCount + quantity).toString())
        console.log('🛒 SingleProduct: Updated sessionStorage cart count to:', currentCount + quantity)

        setSuccessMessage(`${product.title} added to cart successfully!`)
        setShowSuccessNotification(true)

        // Dispatch cart update event to update header counter
        window.dispatchEvent(new CustomEvent('cartUpdated'))

        // Also dispatch cart sync event
        console.log('🛒 SingleProduct: Dispatching cartSync event...')
        window.dispatchEvent(new CustomEvent('cartSync'))

        // Also dispatch force sync event
        console.log('🛒 SingleProduct: Dispatching forceCartSync event...')
        window.dispatchEvent(new CustomEvent('forceCartSync'))

        console.log('Item added to cart:', response.cart_item)
      } else {
        throw new Error(response.error || 'Failed to add to cart')
      }
    } catch(error) {
      console.error('Error adding to cart:', error)
      console.error('Error details:', {
        message: error.message,
        response: error.response,
        data: error.response?.data,
        status: error.response?.status
      })

      // Log the full error response for debugging
      if(error.response?.data) {
        console.log('Full error response data:', error.response.data)
        if(error.response.data.details) {
          console.log('Validation details:', error.response.data.details)
        }
      }

      // Better error message handling
      let errorMessage = 'Failed to add to cart'
      if(error.response?.data?.details) {
        // Handle validation errors
        const details = error.response.data.details
        if(details.quantity) {
          errorMessage = details.quantity[0] // Get first quantity error
        } else if(details.product_id) {
          errorMessage = details.product_id[0] // Get first product error
        } else if(details.variant_id) {
          errorMessage = details.variant_id[0] // Get first variant error
        } else {
          errorMessage = JSON.stringify(details)
        }
      } else if(error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if(error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if(error.message) {
        errorMessage = error.message
      }

      setErrorMessage(`Failed to add ${product.title} to cart: ${errorMessage}`)
      setShowErrorNotification(true)
    } finally {
      setAddingToCart(false)
    }
  }

  const renderStars = (rating, interactive = false, onChange = null) => {
    const numRating = parseFloat(rating) || 0
    console.log('🌟 renderStars called with rating:', rating, 'parsed:', numRating)
    return (
      <div className="star-rating">
        {[1, 2, 3, 4, 5].map((star) => {
          let starClass = 'star'
          if(star <= Math.floor(numRating)) {
            starClass += ' filled'
          } else if(star === Math.ceil(numRating) && numRating % 1 !== 0) {
            starClass += ' half-filled'
          }

          return (
            <button
              key={star}
              type={interactive ? "button" : undefined}
              className={starClass}
              onClick={interactive ? () => onChange && onChange(star) : undefined}
              disabled={!interactive}
            >
              <ion-icon name="star"></ion-icon>
              <span style={{display: 'block', position: 'absolute', top: 0, left: 0}}>★</span>
            </button>
          )
        })}
      </div>
    )
  }

  if(loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '400px',
        fontSize: '18px',
        color: '#666'
      }}>
        Loading product...
      </div>
    )
  }

  if(error || !product) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '400px',
        fontSize: '18px',
        color: '#dc2626'
      }}>
        {error || 'Product not found'}
      </div>
    )
  }

  const basePrice = selectedVariant ? selectedVariant.price : product.price
  const baseOldPrice = selectedVariant ? selectedVariant.old_price : product.old_price
  const currentPrice = basePrice * quantity
  const currentOldPrice = baseOldPrice ? baseOldPrice * quantity : null

  return (
    <div className="single-product">
      {/* Auth Modal */}
      <LoginModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />

      <div className="container">
        <div className="product-detail">
          <div className="product-gallery">
            {/* Main Image */}
            <div className="main-image">
              {product.images && product.images.length > 0 ? (
                <img
                  src={product.images[selectedImage]?.image_url}
                  alt={product.images[selectedImage]?.alt_text || product.title}
                  className="product-main-img"
                />
              ) : (
                <img
                  src="/assets/images/products/1.jpg"
                  alt={product.title}
                  className="product-main-img"
                />
              )}
            </div>

            {/* Thumbnail Images */}
            {product.images && product.images.length > 1 && (
              <div className="thumbnail-images">
                {product.images.map((image, index) => (
                  <img
                    key={image.id}
                    src={image.image_url}
                    alt={image.alt_text || product.title}
                    className={`thumbnail ${selectedImage === index ? 'active' : ''}`}
                    onClick={() => setSelectedImage(index)}
                  />
                ))}
              </div>
            )}
          </div>

          <div className="product-info">

            {/* Product Title */}
            <h1 className="product-title">{product.title}</h1>

            {/* Rating */}
            <div className="product-rating">
              {renderStars(product.average_rating || 0)}
              <span className="rating-text">({product.average_rating || 0}) {reviews.length} Reviews</span>
            </div>

            {/* Price */}
            <div className="product-price">
              <div className="price-row">
                <span className="price-label">Unit Price:</span>
                <span className="unit-price">{formatPrice(basePrice)}</span>
              </div>
              <div className="price-row">
                <span className="price-label">Total Price:</span>
                <span className="current-price">{formatPrice(currentPrice)}</span>
              </div>
              {currentOldPrice && (
                <div className="price-row">
                  <span className="price-label">Total Old Price:</span>
                  <span className="old-price">{formatPrice(currentOldPrice)}</span>
                </div>
              )}
            </div>

            {/* Product Details */}
            <div className="product-details">
              <div className="detail-item">
                <strong>SKU:</strong> {selectedVariant?.sku || 'N/A'}
              </div>
              <div className="detail-item">
                <strong>Category:</strong> {product.category?.name || 'N/A'}
              </div>
              <div className="detail-item">
                <strong>Stock:</strong> {selectedVariant?.quantity || product.quantity} available
              </div>
            </div>

            {/* Description */}
            {product.description && (
              <div className="product-description">
                <p>{product.description}</p>
              </div>
            )}

            {/* Variants */}
            {product.variants && product.variants.length > 0 && (
              <div className="product-variants">
                <h3>Options:</h3>
                <div className="variant-options">
                  {product.variants.map((variant) => (
                    <button
                      key={variant.id}
                      className={`variant-option ${selectedVariant?.id === variant.id ? 'selected' : ''}`}
                      onClick={() => handleVariantChange(variant)}
                    >
                      {variant.title}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Quantity and Add to Cart */}
            <div className="product-actions">
              <div className="qty-container">
                <button
                  className="qty-btn-minus btn-light"
                  type="button"
                  onClick={handleQuantityDecrease}
                  disabled={quantity <= 1}
                >
                  −
                </button>
                <input
                  type="number"
                  name="qty"
                  value={quantity}
                  className="input-qty"
                  min="1"
                  max={selectedVariant?.quantity || product?.quantity || 100}
                  onChange={handleQuantityChange}
                />
                <button
                  className="qty-btn-plus btn-light"
                  type="button"
                  onClick={handleQuantityIncrease}
                  disabled={quantity >= (selectedVariant?.quantity || product?.quantity || 100)}
                >
                  +
                </button>
              </div>

              <button
                className="add-to-cart-btn"
                onClick={handleAddToCart}
                disabled={addingToCart}
              >
                <ion-icon name={addingToCart ? "hourglass-outline" : "bag-add-outline"}></ion-icon>
                {addingToCart ? "Adding..." : "Add to Cart"}
              </button>

              <button className="wishlist-btn">
                <ion-icon name="heart-outline"></ion-icon>
              </button>
            </div>

          </div>
        </div>

        {/* Customer Reviews Section */}
        <div className="reviews-section">
          <div className="container">
            <div className="reviews-header">
              <h2>Customer Reviews</h2>
              {isAuthenticated ? (
                <button
                  className="write-review-btn"
                  onClick={() => setShowReviewForm(!showReviewForm)}
                >
                  Write a Review
                </button>
              ) : (
                <button
                  className="write-review-btn"
                  onClick={() => setShowAuthModal(true)}
                >
                  Login to Review
                </button>
              )}
            </div>

            {/* Review Form */}
            {showReviewForm && (
              <div className="review-form-container">
                <form className="review-form" onSubmit={handleReviewSubmit}>
                  <h3>Write Your Review</h3>

                  <div className="form-group">
                    <label>Rating *</label>
                    {renderStars(reviewForm.rating, true, (rating) =>
                      setReviewForm(prev => ({...prev, rating}))
                    )}
                  </div>

                  {!isAuthenticated && (
                    <>
                      <div className="form-group">
                        <label>Your Name *</label>
                        <input
                          type="text"
                          name="user_name"
                          value={reviewForm.user_name}
                          onChange={handleReviewInputChange}
                          required
                          placeholder="Enter your name"
                        />
                      </div>

                      <div className="form-group">
                        <label>Email</label>
                        <input
                          type="email"
                          name="user_email"
                          value={reviewForm.user_email}
                          onChange={handleReviewInputChange}
                          placeholder="Enter your email (optional)"
                        />
                      </div>
                    </>
                  )}

                  {isAuthenticated && (
                    <div className="form-group">
                      <label>Reviewing as:</label>
                      <div className="user-info">
                        <strong>{user?.full_name || user?.email}</strong>
                        <span className="verified-badge">✓ Verified Customer</span>
                      </div>
                    </div>
                  )}

                  <div className="form-group">
                    <label>Review Title</label>
                    <input
                      type="text"
                      name="title"
                      value={reviewForm.title}
                      onChange={handleReviewInputChange}
                      placeholder="Summarize your review"
                    />
                  </div>

                  <div className="form-group">
                    <label>Your Review *</label>
                    <textarea
                      name="comment"
                      value={reviewForm.comment}
                      onChange={handleReviewInputChange}
                      required
                      rows="4"
                      placeholder="Tell us about your experience with this product"
                    ></textarea>
                  </div>

                  <div className="form-actions">
                    <button type="button" onClick={() => setShowReviewForm(false)}>
                      Cancel
                    </button>
                    <button type="submit">Submit Review</button>
                  </div>
                </form>
              </div>
            )}

            {/* Reviews List */}
            <div className="reviews-list">
              {reviews.length > 0 ? (
                reviews.map((review) => (
                  <div key={review.id} className="review-item">
                    <div className="review-header">
                      <div className="reviewer-info">
                        <div className="reviewer-avatar">
                          {review.user_name.charAt(0).toUpperCase()}
                        </div>
                        <div className="reviewer-details">
                          <h4>{review.user_name}</h4>
                          <span className="review-date">
                            {new Date(review.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <div className="review-rating">
                        {renderStars(review.rating)}
                      </div>
                    </div>

                    {review.title && (
                      <h5 className="review-title">{review.title}</h5>
                    )}

                    <p className="review-comment">{review.comment}</p>

                    {review.is_verified_purchase && (
                      <span className="verified-badge">
                        <ion-icon name="checkmark-circle"></ion-icon>
                        Verified Purchase
                      </span>
                    )}
                  </div>
                ))
              ) : (
                <div className="no-reviews">
                  <p>No reviews yet. Be the first to review this product!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Success Notification */}
      <SuccessNotification
        message={successMessage}
        isVisible={showSuccessNotification}
        onClose={() => setShowSuccessNotification(false)}
      />

      {/* Error Notification */}
      <ErrorNotification
        message={errorMessage}
        isVisible={showErrorNotification}
        onClose={() => setShowErrorNotification(false)}
      />
    </div>
  )
}

export default SingleProduct
