import React from 'react'

const Testimonials = () => {
  const testimonials = [
    {
      id: 1,
      image: "/assets/images/testimonial-1.jpg",
      name: "Alan Doe",
      title: "CEO, ABC Company",
      description: "I love this platform! The products are amazing and the service is excellent. Highly recommended!"
    },
    {
      id: 2,
      image: "/assets/images/testimonial-2.jpg",
      name: "Sarah Smith",
      title: "Fashion Designer",
      description: "Great quality products and fast delivery. The customer service team is very helpful and responsive."
    },
    {
      id: 3,
      image: "/assets/images/testimonial-3.jpg",
      name: "John Wilson",
      title: "Business Owner",
      description: "Excellent shopping experience! The website is easy to navigate and the products are exactly as described."
    }
  ]

  return (
    <div className="testimonials-box">
      <div className="container">
        {testimonials.map((testimonial) => (
          <div key={testimonial.id} className="testimonial-card">
            <img 
              src={testimonial.image} 
              alt={testimonial.name} 
              className="testimonial-banner" 
              width="80" 
              height="80"
            />
            <h3 className="testimonial-name">{testimonial.name}</h3>
            <p className="testimonial-title">{testimonial.title}</p>
            <img 
              src="/assets/images/icons/quote.svg" 
              alt="quotation" 
              className="quotation-img" 
              width="20"
            />
            <p className="testimonial-desc">{testimonial.description}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Testimonials
