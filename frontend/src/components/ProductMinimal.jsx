import React from 'react'

const ProductMinimal = () => {
  const products = [
    {
      id: 1,
      image: "/assets/images/products/watch-1.jpg",
      title: "Smart Watch",
      category: "Electronics",
      price: "$299.00",
      oldPrice: "$399.00"
    },
    {
      id: 2,
      image: "/assets/images/products/jacket-1.jpg",
      title: "Men's Jacket",
      category: "Men's",
      price: "$89.00",
      oldPrice: "$120.00"
    },
    {
      id: 3,
      image: "/assets/images/products/shoe-1.jpg",
      title: "Formal Shoes",
      category: "Men's",
      price: "$79.00",
      oldPrice: "$99.00"
    }
  ]

  return (
    <div className="product-showcase">
      <h2 className="title">Deal of the day</h2>
      <div className="showcase-wrapper">
        {products.map((product) => (
          <div key={product.id} className="showcase-container">
            <div className="showcase">
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
                <a href="#" className="showcase-category">{product.category}</a>
                <h3 className="showcase-title">
                  <a href="#" className="showcase-link">{product.title}</a>
                </h3>
                <div className="price-box">
                  <p className="price">{product.price}</p>
                  <del>{product.oldPrice}</del>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ProductMinimal
