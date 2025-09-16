import React from 'react'

const ProductGrid = () => {
  const products = [
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

  return (
    <div className="product-grid">
      {products.map((product) => (
        <div key={product.id} className="showcase">
          <div className="showcase-banner">
            <img 
              src={product.image} 
              alt={product.title} 
              width="300" 
              className="product-img default"
            />
            <img 
              src={product.hoverImage} 
              alt={product.title} 
              width="300" 
              className="product-img hover"
            />
            
            <div className={`showcase-badge ${product.badgeType}`}>
              {product.badge}
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
              <button className="btn-action">
                <ion-icon name="bag-add-outline"></ion-icon>
              </button>
            </div>
          </div>

          <div className="showcase-content">
            <a href="#" className="showcase-category">{product.category}</a>
            <h3>
              <a href="#" className="showcase-title">{product.title}</a>
            </h3>
            <div className="showcase-rating">
              <ion-icon name="star"></ion-icon>
              <ion-icon name="star"></ion-icon>
              <ion-icon name="star"></ion-icon>
              <ion-icon name="star"></ion-icon>
              <ion-icon name="star-half"></ion-icon>
            </div>
            <div className="price-box">
              <p className="price">{product.price}</p>
              <del>{product.oldPrice}</del>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default ProductGrid
