# 🛍️ Anon - React eCommerce Frontend

A modern, responsive eCommerce website built with React.js, featuring a clean UI design and smooth user experience.

## 🚀 Features

### 🎨 **UI/UX Features**

- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Modern UI** - Clean, professional design with smooth animations
- **Fast Loading** - Optimized components and CSS for quick performance
- **Interactive Elements** - Hover effects, transitions, and smooth scrolling

### 🔐 **Authentication System**

- **Sign In/Sign Up** - Complete authentication modal
- **Password Visibility Toggle** - Show/hide password with eye icon
- **Social Login** - Google and Facebook integration ready
- **Forgot Password** - Password reset functionality
- **User Profile** - Profile management system

### 🛒 **E-commerce Features**

- **Product Grid** - Beautiful product showcase with hover effects
- **Banner Slider** - Auto-rotating promotional banners
- **Category Navigation** - Easy product browsing
- **Search Functionality** - Product search with real-time results
- **Shopping Cart** - Add to cart functionality (ready for backend integration)

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── authentication/          # Auth components
│   │   │   ├── LoginModal.jsx      # Sign in/up modal
│   │   │   ├── Profile.jsx         # User profile
│   │   │   ├── ForgotPassword.jsx  # Password reset
│   │   │   ├── auth.css            # Auth styles
│   │   │   └── index.js            # Auth exports
│   │   ├── Header.jsx              # Navigation header
│   │   ├── Banner.jsx              # Hero banner slider
│   │   ├── ProductContainer.jsx    # Product sections
│   │   ├── ProductGrid.jsx         # Product showcase
│   │   ├── Footer.jsx              # Site footer
│   │   └── ...                     # Other components
│   ├── App.jsx                     # Main app component
│   ├── main.jsx                    # App entry point
│   └── index.css                   # Global styles
├── assets/                         # Static assets
│   ├── css/                        # Original CSS files
│   ├── images/                     # Images and icons
│   └── js/                         # JavaScript files
├── package.json                    # Dependencies
├── vite.config.js                  # Vite configuration
└── index.html                      # HTML template
```

## 🛠️ Installation & Setup

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation Steps

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Start development server**

   ```bash
   npm run dev
   ```

4. **Open in browser**
   ```
   http://localhost:3000
   ```

## 🎯 Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔧 Technologies Used

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **CSS3** - Custom styling with CSS variables
- **Ion Icons** - Beautiful icon library
- **Google Fonts** - Poppins font family

## 🎨 Design System

### Colors

```css
--salmon-pink: #ff6b6b    /* Primary color */
--eerie-black: #212121    /* Text color */
--sonic-silver: #777777   /* Secondary text */
--cultured: #f5f5f5       /* Background */
--white: #ffffff          /* Pure white */
```

### Typography

- **Font Family**: Poppins (Google Fonts)
- **Font Weights**: 300, 400, 500, 600, 700, 800, 900
- **Responsive**: Scales from mobile to desktop

## 🔐 Authentication Components

### LoginModal

- Sign in/Sign up toggle
- Form validation
- Password visibility toggle
- Social login buttons

### Profile

- User information management
- Edit profile functionality
- Address management
- Logout functionality

### ForgotPassword

- Email-based password reset
- Success/error states
- Back to login navigation

## 📱 Responsive Breakpoints

```css
/* Mobile First Approach */
- Mobile: 320px - 480px
- Tablet: 481px - 768px
- Desktop: 769px - 1024px
- Large Desktop: 1025px+
```

## 🚀 Performance Optimizations

- **React.memo** - Prevents unnecessary re-renders
- **useCallback** - Optimized event handlers
- **CSS Optimization** - Fast animations and transitions
- **Lazy Loading** - Components load when needed
- **Image Optimization** - Proper image sizing and formats

## 🔗 Backend Integration

The frontend is ready to integrate with Django backend:

### API Endpoints (Expected)

```
POST /api/auth/login/          # User login
POST /api/auth/register/       # User registration
GET  /api/products/            # Product list
POST /api/cart/add/            # Add to cart
GET  /api/user/profile/        # User profile
```

### State Management

- Ready for Redux/Context API integration
- Form state management
- User authentication state
- Shopping cart state

## 🎯 Key Features

### 🏠 **Homepage**

- Hero banner with auto-slider
- Product grid showcase
- Category navigation
- Blog section
- Footer with links

### 🔐 **Authentication**

- Modal-based login/signup
- Password strength validation
- Social login integration
- Profile management

### 🛒 **E-commerce**

- Product browsing
- Search functionality
- Shopping cart
- Wishlist (ready for implementation)

## 📝 Development Notes

### Adding New Components

1. Create component in appropriate folder
2. Export from index.js if needed
3. Import and use in App.jsx
4. Add styles to relevant CSS file

### Styling Guidelines

- Use CSS variables for colors
- Follow mobile-first approach
- Use consistent spacing and typography
- Test on multiple screen sizes

### State Management

- Use React hooks for local state
- Consider Context API for global state
- Implement proper error handling
- Add loading states for better UX

## 🐛 Troubleshooting

### Common Issues

1. **Modal not opening**

   - Check if CSS animations are properly loaded
   - Verify component state management

2. **Styling issues**

   - Ensure CSS files are properly imported
   - Check for CSS conflicts

3. **Build errors**
   - Clear node_modules and reinstall
   - Check for missing dependencies

## 📞 Support

For issues and questions:

- Check the console for errors
- Verify all dependencies are installed
- Ensure Node.js version compatibility

## 🎉 Conclusion

This React eCommerce frontend provides a solid foundation for a modern online store with:

- Beautiful, responsive design
- Complete authentication system
- Optimized performance
- Easy backend integration
- Scalable architecture

Ready to build your dream eCommerce platform! 🚀
