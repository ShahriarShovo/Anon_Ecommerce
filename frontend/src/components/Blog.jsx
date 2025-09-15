import React from 'react'

const Blog = () => {
  const blogPosts = [
    {
      id: 1,
      image: "/assets/images/blog-1.jpg",
      category: "Fashion",
      title: "Clothes Retail KPIs 2021 Guide for Clothes Executives",
      author: "Mr. Admin",
      date: "April 06, 2022"
    },
    {
      id: 2,
      image: "/assets/images/blog-2.jpg",
      category: "Clothes",
      title: "Curbside fashion Trends: How to Win the Pickup Battle.",
      author: "Mr. Robin",
      date: "January 18, 2022"
    },
    {
      id: 3,
      image: "/assets/images/blog-3.jpg",
      category: "Shoes",
      title: "EBT vendors: Claim Your Share of SNAP Online Revenue.",
      author: "Mr. Selsa",
      date: "February 10, 2022"
    },
    {
      id: 4,
      image: "/assets/images/blog-4.jpg",
      category: "Electronics",
      title: "Curbside fashion Trends: How to Win the Pickup Battle.",
      author: "Mr. Pawar",
      date: "March 15, 2022"
    }
  ]

  return (
    <div className="blog">
      <div className="container">
        <h2 className="title">Latest Blog</h2>
        <div className="blog-container">
          {blogPosts.map((post) => (
            <div key={post.id} className="blog-card">
              <img 
                src={post.image} 
                alt={post.title} 
                className="blog-banner" 
                width="300"
              />
              <div className="blog-content">
                <a href="#" className="blog-category">{post.category}</a>
                <h3>
                  <a href="#" className="blog-title">{post.title}</a>
                </h3>
                <p className="blog-meta">
                  By <cite>{post.author}</cite> / <time>{post.date}</time>
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Blog
