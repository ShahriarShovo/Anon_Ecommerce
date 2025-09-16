import React from 'react'

const ProductFeatured = () => {
  const featuredProduct = {
    id: 1,
    image: "/assets/images/products/watch-2.jpg",
    rating: 4.5,
    title: "Smart Watch",
    description: "Smart watch with advanced features and modern design",
    price: "$299.00",
    oldPrice: "$399.00",
    status: "Limited Stock",
    stockPercentage: 40,
    countdown: {
      days: 2,
      hours: 5,
      minutes: 30,
      seconds: 45
    }
  }

  return (
    <div className="product-showcase">
      <h2 className="title">Featured Products</h2>
      <div className="showcase-wrapper">
        <div className="showcase-container">
          <div className="showcase">
            <div className="showcase-img-box">
              <img 
                src={featuredProduct.image} 
                alt={featuredProduct.title} 
                className="showcase-img"
              />
            </div>
            <div className="showcase-content">
              <div className="showcase-rating">
                <ion-icon name="star"></ion-icon>
                <ion-icon name="star"></ion-icon>
                <ion-icon name="star"></ion-icon>
                <ion-icon name="star"></ion-icon>
                <ion-icon name="star-half"></ion-icon>
              </div>
              <h3 className="showcase-title">{featuredProduct.title}</h3>
              <p className="showcase-desc">{featuredProduct.description}</p>
              <div className="price-box">
                <p className="price">{featuredProduct.price}</p>
                <del>{featuredProduct.oldPrice}</del>
              </div>
              <button className="add-cart-btn">Add to Cart</button>
              <div className="showcase-status">
                <div className="wrapper">
                  <p>Already Sold: <b>20</b></p>
                  <p>Available: <b>40</b></p>
                </div>
                <div className="showcase-status-bar">
                  <div className="showcase-status-bar-fill" style={{width: `${featuredProduct.stockPercentage}%`}}></div>
                </div>
              </div>
              <div className="countdown-desc">Hurry Up! Offer ends in:</div>
              <div className="countdown">
                <div className="countdown-content">
                  <p className="display-number">{featuredProduct.countdown.days}</p>
                  <p className="display-text">Days</p>
                </div>
                <div className="countdown-content">
                  <p className="display-number">{featuredProduct.countdown.hours}</p>
                  <p className="display-text">Hours</p>
                </div>
                <div className="countdown-content">
                  <p className="display-number">{featuredProduct.countdown.minutes}</p>
                  <p className="display-text">Mins</p>
                </div>
                <div className="countdown-content">
                  <p className="display-number">{featuredProduct.countdown.seconds}</p>
                  <p className="display-text">Secs</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProductFeatured
