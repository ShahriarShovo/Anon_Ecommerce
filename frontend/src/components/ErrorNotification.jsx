import React, {useState, useEffect} from 'react'

const ErrorNotification = ({message, isVisible, onClose, duration = 4000}) => {
    useEffect(() => {
        if(isVisible) {
            const timer = setTimeout(() => {
                onClose()
            }, duration)
            return () => clearTimeout(timer)
        }
    }, [isVisible, duration, onClose])

    if(!isVisible) return null

    return (
        <>
            <style jsx>{`
        .error-notification {
          position: fixed;
          top: 20px;
          right: 20px;
          background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
          color: white;
          padding: 16px 24px;
          border-radius: 12px;
          box-shadow: 0 8px 25px rgba(220, 53, 69, 0.3);
          z-index: 10000;
          display: flex;
          align-items: center;
          gap: 12px;
          min-width: 300px;
          max-width: 400px;
          transform: translateX(100%);
          opacity: 0;
          animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
          border: 1px solid rgba(255, 255, 255, 0.2);
          backdrop-filter: blur(10px);
        }

        .error-notification.closing {
          animation: slideOut 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }

        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        @keyframes slideOut {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(100%);
            opacity: 0;
          }
        }

        .error-icon {
          width: 24px;
          height: 24px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          flex-shrink: 0;
        }

        .error-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .error-title {
          font-weight: 600;
          font-size: 14px;
          margin: 0;
        }

        .error-message {
          font-size: 13px;
          opacity: 0.9;
          margin: 0;
          line-height: 1.4;
        }

        .error-close {
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
          opacity: 0.7;
          transition: opacity 0.2s ease;
          flex-shrink: 0;
        }

        .error-close:hover {
          opacity: 1;
          background: rgba(255, 255, 255, 0.1);
        }

        .error-progress {
          position: absolute;
          bottom: 0;
          left: 0;
          height: 3px;
          background: rgba(255, 255, 255, 0.3);
          border-radius: 0 0 12px 12px;
          animation: progress ${duration}ms linear forwards;
        }

        @keyframes progress {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
          .error-notification {
            top: 10px;
            right: 10px;
            left: 10px;
            min-width: auto;
            max-width: none;
          }
        }
      `}</style>

            <div className="error-notification">
                <div className="error-icon">
                    ⚠️
                </div>
                <div className="error-content">
                    <h4 className="error-title">Error!</h4>
                    <p className="error-message">{message}</p>
                </div>
                <button className="error-close" onClick={onClose}>
                    ×
                </button>
                <div className="error-progress"></div>
            </div>
        </>
    )
}

export default ErrorNotification
