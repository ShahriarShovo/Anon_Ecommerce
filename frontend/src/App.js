import React, {useState} from 'react'
import {AuthProvider} from './contexts/AuthContext'
import {CategoriesProvider} from './contexts/CategoriesContext'
import Header from './components/Header'
import Banner from './components/Banner'
import ProductContainer from './components/ProductContainer'
import Blog from './components/Blog'
import Footer from './components/Footer'
import Modal from './components/Modal'
import NotificationToast from './components/NotificationToast'
import {LoginModal} from './components/authentication'
import ProfilePage from './components/authentication/customer/ProfilePage'
import UserDashboard from './components/authentication/customer/UserDashboard'
import AdminDashboard from './components/authentication/admin/AdminDashboard'
import SingleProduct from './components/SingleProduct'
import CartPageFull from './components/CartPageFull'

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isToastVisible, setIsToastVisible] = useState(true)
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)

  // Simple routing logic
  const currentPath = window.location.pathname
  console.log('Current path:', currentPath) // Debug log

  // If on cart page, show cart
  if(currentPath === '/cart') {
    return (
      <AuthProvider>
        <CategoriesProvider>
          <div className="App">
            {/* Overlay */}
            <div className="overlay" data-overlay></div>

            {/* Auth Modal */}
            <LoginModal
              isOpen={isAuthModalOpen}
              onClose={() => setIsAuthModalOpen(false)}
            />

            <Header onAuthClick={() => setIsAuthModalOpen(true)} />
            <CartPageFull />
            <Footer />
          </div>
        </CategoriesProvider>
      </AuthProvider>
    )
  }

  // If on single product page, show single product
  if(currentPath.startsWith('/product/')) {
    return (
      <AuthProvider>
        <CategoriesProvider>
          <div className="App">
            {/* Overlay */}
            <div className="overlay" data-overlay></div>

            {/* Auth Modal */}
            <LoginModal
              isOpen={isAuthModalOpen}
              onClose={() => setIsAuthModalOpen(false)}
            />

            <Header onAuthClick={() => setIsAuthModalOpen(true)} />
            <SingleProduct />
            <Footer />
          </div>
        </CategoriesProvider>
      </AuthProvider>
    )
  }

  // If on dashboard page, show dashboard
  if(currentPath === '/dashboard' || currentPath.startsWith('/dashboard/')) {
    console.log('Rendering UserDashboard') // Debug log
    return (
      <AuthProvider>
        <CategoriesProvider>
          <div className="App">
            {/* Overlay */}
            <div className="overlay" data-overlay></div>

            {/* Auth Modal */}
            <LoginModal
              isOpen={isAuthModalOpen}
              onClose={() => setIsAuthModalOpen(false)}
            />

            <Header onAuthClick={() => setIsAuthModalOpen(true)} />
            <UserDashboard />
            <Footer />
          </div>
        </CategoriesProvider>
      </AuthProvider>
    )
  }

  // If on admin dashboard page, show admin dashboard
  if(currentPath === '/admin-dashboard' || currentPath.startsWith('/admin-dashboard/')) {
    console.log('Rendering AdminDashboard') // Debug log
    return (
      <AuthProvider>
        <CategoriesProvider>
          <div className="App">
            {/* Overlay */}
            <div className="overlay" data-overlay></div>

            {/* Auth Modal */}
            <LoginModal
              isOpen={isAuthModalOpen}
              onClose={() => setIsAuthModalOpen(false)}
            />

            <Header onAuthClick={() => setIsAuthModalOpen(true)} />
            <AdminDashboard />
            <Footer />
          </div>
        </CategoriesProvider>
      </AuthProvider>
    )
  }

  // If on profile page, show only profile
  if(currentPath === '/profile') {
    return (
      <AuthProvider>
        <CategoriesProvider>
          <div className="App">
            {/* Overlay */}
            <div className="overlay" data-overlay></div>

            {/* Auth Modal */}
            <LoginModal
              isOpen={isAuthModalOpen}
              onClose={() => setIsAuthModalOpen(false)}
            />

            <Header onAuthClick={() => setIsAuthModalOpen(true)} />
            <ProfilePage />
            <Footer />
          </div>
        </CategoriesProvider>
      </AuthProvider>
    )
  }

  // Default home page
  return (
    <AuthProvider>
      <CategoriesProvider>
        <div className="App">
          {/* Overlay */}
          <div className="overlay" data-overlay></div>

          {/* Modal */}
          <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />

          {/* Notification Toast */}
          <NotificationToast
            isVisible={isToastVisible}
            onClose={() => setIsToastVisible(false)}
          />

          {/* Auth Modal */}
          <LoginModal
            isOpen={isAuthModalOpen}
            onClose={() => setIsAuthModalOpen(false)}
          />

          {/* Header */}
          <Header onAuthClick={() => setIsAuthModalOpen(true)} />

          {/* Main Content */}
          <main>
            {/* Banner */}
            <Banner />

            {/* Product Container */}
            <ProductContainer />

            {/* Blog */}
            <Blog />
          </main>

          {/* Footer */}
          <Footer />
        </div>
      </CategoriesProvider>
    </AuthProvider>
  )
}

export default App