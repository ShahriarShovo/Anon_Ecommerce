import React, { useState, useEffect } from 'react'
import apiService from '../services/api'

const ProductGrid = () => {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [addingToCart, setAddingToCart] = useState({}) // Track which product is being added

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      const response = await apiService.getHomepageProducts()
      
      if (response.success) {
        setProducts(response.products)
      } else {
        throw new Error(response.error || 'Failed to fetch products')
      }
    } catch (error) {
      console.error('Error fetching products:', error)
      setError('Failed to load products')
      // Fallback to static products if API fails
      setProducts(getStaticProducts())
    } finally {
      setLoading(false)
    }
  }

  // Add to cart function
  const handleAddToCart = async (productId, productTitle) => {
    try {
      console.log('🛒 ProductGrid: Adding to cart - Product ID:', productId, 'Title:', productTitle)
      setAddingToCart(prev => ({ ...prev, [productId]: true }))
      
      const response = await apiService.addToCart(productId, 1)
      console.log('🛒 ProductGrid: Add to cart API response:', response)
      
      if (response.success) {
        // Update sessionStorage
        const currentCount = parseInt(sessionStorage.getItem('cartCount') || '0')
        sessionStorage.setItem('cartCount', (currentCount + 1).toString())
        console.log('🛒 ProductGrid: Updated sessionStorage cart count to:', currentCount + 1)
        
        // Show success message
        alert(`${productTitle} added to cart successfully!`)
        
        // Dispatch cart update event to update header counter
        console.log('🛒 ProductGrid: Dispatching cartUpdated event...')
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        
        // Also dispatch cart sync event
        console.log('🛒 ProductGrid: Dispatching cartSync event...')
        window.dispatchEvent(new CustomEvent('cartSync'))
        
        // Also dispatch force sync event
        console.log('🛒 ProductGrid: Dispatching forceCartSync event...')
        window.dispatchEvent(new CustomEvent('forceCartSync'))
        
        console.log('🛒 ProductGrid: Item added to cart:', response.cart_item)
      } else {
        throw new Error(response.error || 'Failed to add to cart')
      }
    } catch (error) {
      console.error('🛒 ProductGrid: Error adding to cart:', error)
      alert(`Failed to add ${productTitle} to cart: ${error.message}`)
    } finally {
      setAddingToCart(prev => ({ ...prev, [productId]: false }))
    }
  }

  const getStaticProducts = () => [
    {
      id: 1,
      image: "/assets/images/products/jacket-3.jpg",
      hoverImage: "/assets/images/products/jacket-4.jpg",
      badge: "Sale",
      badgeType: "angle",
      category: "Men's",
      title: "Mens Winter Leathers Jackets",
      rating: 4.5,
      price: "$48.00",
      oldPrice: "$75.00"
    },
    {
      id: 2,
      image: "/assets/images/products/shirt-1.jpg",
      hoverImage: "/assets/images/products/shirt-2.jpg",
      badge: "New",
      badgeType: "pink",
      category: "Men's",
      title: "Pure Garment Dyed Cotton Shirt",
      rating: 4.0,
      price: "$45.00",
      oldPrice: "$56.00"
    },
    {
      id: 3,
      image: "/assets/images/products/jacket-5.jpg",
      hoverImage: "/assets/images/products/jacket-6.jpg",
      badge: "Sale",
      badgeType: "black",
      category: "Men's",
      title: "MEN Yarn Fleece Full-Zip Jacket",
      rating: 4.5,
      price: "$58.00",
      oldPrice: "$65.00"
    },
    {
      id: 4,
      image: "/assets/images/products/clothes-3.jpg",
      hoverImage: "/assets/images/products/clothes-4.jpg",
      badge: "New",
      badgeType: "pink",
      category: "Women's",
      title: "Black Floral Wrap Midi Skirt",
      rating: 4.0,
      price: "$24.00",
      oldPrice: "$35.00"
    },
    {
      id: 5,
      image: "/assets/images/products/shoe-2.jpg",
      hoverImage: "/assets/images/products/shoe-2_1.jpg",
      badge: "Sale",
      badgeType: "angle",
      category: "Men's",
      title: "Casual Men's Brown shoes",
      rating: 4.5,
      price: "$99.00",
      oldPrice: "$120.00"
    },
    {
      id: 6,
      image: "/assets/images/products/watch-3.jpg",
      hoverImage: "/assets/images/products/watch-4.jpg",
      badge: "New",
      badgeType: "pink",
      category: "Electronics",
      title: "Pocket Watch Leather Pouch",
      rating: 4.0,
      price: "$150.00",
      oldPrice: "$170.00"
    },
    {
      id: 7,
      image: "/assets/images/products/watch-1.jpg",
      hoverImage: "/assets/images/products/watch-2.jpg",
      badge: "Sale",
      badgeType: "black",
      category: "Electronics",
      title: "Smart watche Vital Plus",
      rating: 4.5,
      price: "$100.00",
      oldPrice: "$120.00"
    },
    {
      id: 8,
      image: "/assets/images/products/party-wear-1.jpg",
      hoverImage: "/assets/images/products/party-wear-2.jpg",
      badge: "New",
      badgeType: "pink",
      category: "Women's",
      title: "Womens Party Wear Shoes",
      rating: 4.0,
      price: "$25.00",
      oldPrice: "$35.00"
    }
  ]

  const getProductImage = (product) => {
    console.log('Getting image for product:', product.title)
    console.log('Product data:', product)
    
    // Check if product has image_url from homepage API
    if (product.image_url) {
      console.log('Using image_url:', product.image_url)
      return product.image_url
    }
    
    // Check if product has primary_image
    if (product.primary_image && product.primary_image.image_url) {
      console.log('Using primary_image.image_url:', product.primary_image.image_url)
      return product.primary_image.image_url
    }
    
    // Check if product has image field
    if (product.primary_image && product.primary_image.image) {
      const fullUrl = `http://127.0.0.1:8000${product.primary_image.image}`
      console.log('Using primary_image.image with full URL:', fullUrl)
      return fullUrl
    }
    
    // Fallback to static image
    console.log('Using fallback static image for:', product.title)
    return "/assets/images/products/1.jpg"
  }

  const getProductHoverImage = (product) => {
    // For now, use the same image as hover
    // You can implement hover image logic later
    return getProductImage(product)
  }

  const formatPrice = (price) => {
    if (typeof price === 'string') return price
    return `$${parseFloat(price).toFixed(2)}`
  }

  const renderStars = (rating) => {
    const stars = []
    const fullStars = Math.floor(rating)
    const hasHalfStar = rating % 1 !== 0
    
    // Full stars
    for (let i = 0; i < fullStars; i++) {
      stars.push(<ion-icon key={i} name="star"></ion-icon>)
    }
    
    // Half star
    if (hasHalfStar) {
      stars.push(<ion-icon key="half" name="star-half"></ion-icon>)
    }
    
    // Empty stars
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0)
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<ion-icon key={`empty-${i}`} name="star-outline"></ion-icon>)
    }
    
    return stars
  }

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px',
        fontSize: '18px',
        color: '#666'
      }}>
        Loading products...
      </div>
    )
  }

  if (error && products.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px',
        fontSize: '18px',
        color: '#dc2626'
      }}>
        {error}
      </div>
    )
  }

  return (
    <div className="product-grid">
      {products.map((product) => (
        <div key={product.id} className="showcase">
          <div className="showcase-banner">
            <img 
              src={getProductImage(product)} 
              alt={product.image_alt || product.title} 
              width="300" 
              className="product-img default"
              onError={(e) => {
                e.target.src = "/assets/images/products/1.jpg"
              }}
            />
            <img 
              src={getProductHoverImage(product)} 
              alt={product.image_alt || product.title} 
              width="300" 
              className="product-img hover"
              onError={(e) => {
                e.target.src = "/assets/images/products/1.jpg"
              }}
            />
            
            <div className={`showcase-badge ${product.badgeType || 'angle'}`}>
              {product.badge || 'New'}
            </div>

            <div className="showcase-actions">
              <button className="btn-action">
                <ion-icon name="heart-outline"></ion-icon>
              </button>
              <button className="btn-action">
                <ion-icon name="eye-outline"></ion-icon>
              </button>
              <button className="btn-action">
                <ion-icon name="repeat-outline"></ion-icon>
              </button>
              <button 
                className="btn-action"
                onClick={() => handleAddToCart(product.id, product.title)}
                disabled={addingToCart[product.id]}
                title="Add to Cart"
              >
                <ion-icon name={addingToCart[product.id] ? "hourglass-outline" : "bag-add-outline"}></ion-icon>
              </button>
            </div>
          </div>

          <div className="showcase-content">
            <a href="#" className="showcase-category">
              {product.category_name || product.category || 'General'}
            </a>
            <h3>
              <a href={`/product/${product.slug}`} className="showcase-title">
                {product.title}
              </a>
            </h3>
            <div className="showcase-rating">
              {renderStars(product.average_rating || 0)}
              {product.review_count > 0 && (
                <span className="rating-text">({product.review_count})</span>
              )}
            </div>
            <div className="price-box">
              <p className="price">
                {formatPrice(product.price)}
              </p>
              {product.old_price && (
                <del>{formatPrice(product.old_price)}</del>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default ProductGrid