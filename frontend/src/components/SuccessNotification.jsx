import React, {useState, useEffect} from 'react'

const SuccessNotification = ({message, isVisible, onClose, duration = 3000}) => {
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
        .success-notification {
          position: fixed;
          top: 20px;
          right: 20px;
          background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
          color: white;
          padding: 16px 24px;
          border-radius: 12px;
          box-shadow: 0 8px 25px rgba(40, 167, 69, 0.3);
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

        .success-notification.closing {
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

        .success-icon {
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

        .success-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .success-title {
          font-weight: 600;
          font-size: 14px;
          margin: 0;
        }

        .success-message {
          font-size: 13px;
          opacity: 0.9;
          margin: 0;
          line-height: 1.4;
        }

        .success-close {
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

        .success-close:hover {
          opacity: 1;
          background: rgba(255, 255, 255, 0.1);
        }

        .success-progress {
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
          .success-notification {
            top: 10px;
            right: 10px;
            left: 10px;
            min-width: auto;
            max-width: none;
          }
        }
      `}</style>

            <div className="success-notification">
                <div className="success-icon">
                    ✓
                </div>
                <div className="success-content">
                    <h4 className="success-title">Success!</h4>
                    <p className="success-message">{message}</p>
                </div>
                <button className="success-close" onClick={onClose}>
                    ×
                </button>
                <div className="success-progress"></div>
            </div>
        </>
    )
}

export default SuccessNotification
