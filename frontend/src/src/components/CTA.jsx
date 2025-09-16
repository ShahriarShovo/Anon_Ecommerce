import React from 'react'

const CTA = () => {
  return (
    <div className="cta-container">
      <img 
        src="/assets/images/cta-banner.jpg" 
        alt="summer collection" 
        className="cta-banner"
      />
      <div className="cta-content">
        <p className="discount">25% Discount</p>
        <h2 className="cta-title">Summer Collection</h2>
        <p className="cta-text">Starting @ $10</p>
        <a href="#" className="cta-btn">Shop Now</a>
      </div>
    </div>
  )
}

export default CTA
