import React from 'react'

const Category = () => {
  const categories = [
    {
      id: 1,
      image: "/assets/images/categories/electronics.jpg",
      title: "Electronics",
      amount: "3",
      link: "#"
    },
    {
      id: 2,
      image: "/assets/images/categories/mens.jpg",
      title: "Men's",
      amount: "2",
      link: "#"
    },
    {
      id: 3,
      image: "/assets/images/categories/womens.jpg",
      title: "Women's",
      amount: "5",
      link: "#"
    },
    {
      id: 4,
      image: "/assets/images/categories/jewelry.jpg",
      title: "Jewelry",
      amount: "10",
      link: "#"
    },
    {
      id: 5,
      image: "/assets/images/categories/perfume.jpg",
      title: "Perfume",
      amount: "5",
      link: "#"
    }
  ]

  return (
    <div className="category">
      <div className="container">
        <div className="category-item-container">
          {categories.map((category) => (
            <div key={category.id} className="category-item">
              <div className="category-img-box">
                <img 
                  src={category.image} 
                  alt={category.title} 
                  width="30" 
                  height="30" 
                />
              </div>
              <div className="category-content-box">
                <div className="category-content-flex">
                  <h3 className="category-item-title">{category.title}</h3>
                  <p className="category-item-amount">({category.amount})</p>
                </div>
                <a href={category.link} className="category-btn">Show All</a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Category
