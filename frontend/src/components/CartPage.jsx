import React from "react"

const CartPage = () => {
    // This component is no longer used
    // Cart functionality has been moved to CartPageFull.jsx
    // and is accessible via /cart route

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            fontSize: '18px',
            color: '#666',
            flexDirection: 'column',
            gap: '20px'
        }}>
            <div>Cart functionality has been moved to the dedicated cart page.</div>
            <div>
                Please navigate to <a href="/cart" style={{color: '#6366f1', textDecoration: 'underline'}}>/cart</a>
            </div>
        </div>
    )
}

export default CartPage
