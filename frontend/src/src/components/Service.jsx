import React from 'react'

const Service = () => {
  const services = [
    {
      id: 1,
      icon: "boat-outline",
      title: "Worldwide Delivery",
      description: "For Order Over $100"
    },
    {
      id: 2,
      icon: "rocket-outline",
      title: "Next Day Delivery",
      description: "UK Orders Only"
    },
    {
      id: 3,
      icon: "call-outline",
      title: "Best Online Support",
      description: "Hours: 8AM - 11PM"
    },
    {
      id: 4,
      icon: "arrow-undo-outline",
      title: "Return Policy",
      description: "Easy & Free Return"
    },
    {
      id: 5,
      icon: "ticket-outline",
      title: "30% Money Back",
      description: "For Order Over $100"
    }
  ]

  return (
    <div className="service-container">
      {services.map((service) => (
        <div key={service.id} className="service-item">
          <div className="service-icon">
            <ion-icon name={service.icon}></ion-icon>
          </div>
          <div className="service-content">
            <h3 className="service-title">{service.title}</h3>
            <p className="service-desc">{service.description}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

export default Service
