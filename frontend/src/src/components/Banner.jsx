import React, { useState, useEffect } from 'react'

const Banner = () => {
  const [currentSlide, setCurrentSlide] = useState(0)

  const banners = [
    {
      id: 1,
      image: "/assets/images/banner-1.jpg",
      subtitle: "Trending item",
      title: "Women's latest fashion sale",
      text: "Starting at $29.99",
      buttonText: "Shop now"
    },
    {
      id: 2,
      image: "/assets/images/banner-2.jpg",
      subtitle: "Trending accessories",
      title: "Modern sunglasses",
      text: "See all collection",
      buttonText: "Shop now"
    },
    {
      id: 3,
      image: "/assets/images/banner-3.jpg",
      subtitle: "Sale Offer",
      title: "New fashion summer sale",
      text: "Starting at $39.99",
      buttonText: "Shop now"
    }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % banners.length)
    }, 5000)

    return () => clearInterval(interval)
  }, [banners.length])

  return (
    <div className="banner">
      <div className="container">
        <div className="slider-container">
          {banners.map((banner, index) => (
            <div 
              key={banner.id}
              className="slider-item"
              style={{ 
                transform: `translateX(-${currentSlide * 100}%)`,
                minWidth: '100%'
              }}
            >
              <img 
                src={banner.image} 
                alt={banner.title} 
                className="banner-img"
              />
              <div className="banner-content">
                <p className="banner-subtitle">{banner.subtitle}</p>
                <h2 className="banner-title">{banner.title}</h2>
                <p className="banner-text">
                  {banner.text}
                </p>
                <a href="#" className="banner-btn">{banner.buttonText}</a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Banner
