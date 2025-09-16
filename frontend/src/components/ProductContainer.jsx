import React, { useState } from 'react'
import Sidebar from './Sidebar'
import ProductMinimal from './ProductMinimal'
import ProductFeatured from './ProductFeatured'
import ProductGrid from './ProductGrid'

const ProductContainer = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  return (
    <div className="product-container">
      <div className="container">
        <div className="product-box">
          <div className="product-main">
            <ProductGrid />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProductContainer
