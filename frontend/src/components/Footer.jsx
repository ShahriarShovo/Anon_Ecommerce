import React from 'react'

const Footer = () => {
  return (
    <footer className="simple-footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-links">
            <a href="#" className="footer-link">About Us</a>
            <a href="#" className="footer-link">Contact</a>
            <a href="#" className="footer-link">Privacy Policy</a>
            <a href="#" className="footer-link">Terms of Service</a>
          </div>
          
          <div className="footer-social">
            <a href="#" className="social-link">
              <ion-icon name="logo-facebook"></ion-icon>
            </a>
            <a href="#" className="social-link">
              <ion-icon name="logo-twitter"></ion-icon>
            </a>
            <a href="#" className="social-link">
              <ion-icon name="logo-instagram"></ion-icon>
            </a>
            <a href="#" className="social-link">
              <ion-icon name="logo-linkedin"></ion-icon>
            </a>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p className="copyright">
            Copyright &copy; 2024 <span className="brand-name">Anon</span>. All Rights Reserved
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
