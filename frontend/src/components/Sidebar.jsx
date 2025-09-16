import React, { useState } from 'react'

const Sidebar = ({ isOpen, onClose }) => {
  const [activeAccordion, setActiveAccordion] = useState(null)

  const toggleAccordion = (index) => {
    setActiveAccordion(activeAccordion === index ? null : index)
  }

  const categories = [
    {
      title: "Electronics",
      subcategories: [
        { name: "Desktop", count: 4 },
        { name: "Laptop", count: 3 },
        { name: "Camera", count: 2 },
        { name: "Tablet", count: 1 },
        { name: "Headphone", count: 2 }
      ]
    },
    {
      title: "Men's",
      subcategories: [
        { name: "Shirt", count: 8 },
        { name: "Shorts & Jeans", count: 6 },
        { name: "Safety Shoes", count: 2 },
        { name: "Wallet", count: 4 }
      ]
    },
    {
      title: "Women's",
      subcategories: [
        { name: "Dress & Frock", count: 5 },
        { name: "Earrings", count: 3 },
        { name: "Perfume", count: 2 },
        { name: "Cosmetics", count: 4 }
      ]
    }
  ]

  const featuredProducts = [
    {
      id: 1,
      image: "/assets/images/products/watch-1.jpg",
      title: "Smart Watch",
      rating: 4.5,
      price: "$299.00",
      oldPrice: "$399.00"
    },
    {
      id: 2,
      image: "/assets/images/products/jacket-1.jpg",
      title: "Men's Jacket",
      rating: 4.0,
      price: "$89.00",
      oldPrice: "$120.00"
    }
  ]

  return (
    <div className={`sidebar ${isOpen ? 'active' : ''}`}>
      <div className="sidebar-category">
        <div className="sidebar-top">
          <h2 className="sidebar-title">Filters</h2>
          <button className="sidebar-close-btn" onClick={onClose}>
            <ion-icon name="close-outline"></ion-icon>
          </button>
        </div>

        {categories.map((category, index) => (
          <div key={index} className="sidebar-category">
            <button 
              className={`sidebar-accordion-menu ${activeAccordion === index ? 'active' : ''}`}
              onClick={() => toggleAccordion(index)}
            >
              <div className="menu-title-flex">
                <p className="menu-title">{category.title}</p>
              </div>
              <div>
                <ion-icon name="add-outline" className="add-icon"></ion-icon>
                <ion-icon name="remove-outline" className="remove-icon"></ion-icon>
              </div>
            </button>

            <div className={`sidebar-submenu-category-list ${activeAccordion === index ? 'active' : ''}`}>
              {category.subcategories.map((subcategory, subIndex) => (
                <div key={subIndex} className="sidebar-submenu-title">
                  <a href="#" className="product-name">{subcategory.name}</a>
                  <span>({subcategory.count})</span>
                </div>
              ))}
            </div>
          </div>
        ))}

        <div className="sidebar-category">
          <h2 className="showcase-heading">Featured Products</h2>
          {featuredProducts.map((product) => (
            <div key={product.id} className="showcase">
              <div className="showcase-img-box">
                <img 
                  src={product.image} 
                  alt={product.title} 
                  width="75" 
                  height="75" 
                  className="showcase-img"
                />
              </div>
              <div className="showcase-content">
                <h3 className="showcase-title">
                  <a href="#" className="showcase-link">{product.title}</a>
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
      </div>
    </div>
  )
}

export default Sidebar
