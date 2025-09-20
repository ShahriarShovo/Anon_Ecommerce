import React, {useState, useEffect} from "react"
import apiService from "../services/api"

const InvoiceModal = ({isOpen, onClose, orderData}) => {
  const [invoice, setInvoice] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if(isOpen && orderData) {
      generateInvoice()
    }
  }, [isOpen, orderData])

  const generateInvoice = async () => {
    if(!orderData?.id) {
      console.log('🧾 InvoiceModal: No orderData.id provided')
      return
    }

    console.log('🧾 InvoiceModal: Generating invoice for order:', orderData.id)
    setLoading(true)
    setError(null)

    try {
      const response = await apiService.generateInvoice(orderData.id)
      console.log('🧾 InvoiceModal: Invoice API response:', response)

      if(response.success) {
        console.log('🧾 InvoiceModal: Invoice generated successfully:', response.invoice)
        setInvoice(response.invoice)
      } else {
        console.error('🧾 InvoiceModal: Invoice generation failed:', response.message)
        setError(response.message || "Failed to generate invoice")
      }
    } catch(err) {
      console.error("🧾 InvoiceModal: Invoice generation error:", err)
      setError("Failed to generate invoice. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-BD', {
      style: 'currency',
      currency: 'BDT',
      minimumFractionDigits: 2
    }).format(price)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-GB')
  }

  const downloadInvoicePDF = async (invoiceId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/invoice/${invoiceId}/download/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if(response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `invoice_${invoiceId}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        console.error('Failed to download PDF')
        alert('Failed to download PDF. Please try again.')
      }
    } catch(error) {
      console.error('Download error:', error)
      alert('Failed to download PDF. Please try again.')
    }
  }

  const printInvoicePDF = async (invoiceId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/invoice/${invoiceId}/download/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if(response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)

        // Create a new window for printing
        const printWindow = window.open(url, '_blank')
        if(printWindow) {
          printWindow.onload = () => {
            printWindow.print()
            printWindow.close()
          }
        }

        // Clean up after a delay
        setTimeout(() => {
          window.URL.revokeObjectURL(url)
        }, 1000)
      } else {
        console.error('Failed to load PDF for printing')
        alert('Failed to load PDF for printing. Please try again.')
      }
    } catch(error) {
      console.error('Print error:', error)
      alert('Failed to print PDF. Please try again.')
    }
  }

  if(!isOpen) return null

  return (
    <>
      <style jsx>{`
        .invoice-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(4px);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
          opacity: 0;
          visibility: hidden;
          transition: all 0.3s ease;
        }

        .invoice-overlay.active {
          opacity: 1;
          visibility: visible;
        }

        .invoice-modal {
          background: #fff;
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
          width: 100%;
          max-width: 900px;
          max-height: 90vh;
          overflow: auto;
          padding: 0;
          transform: scale(0.9);
          transition: transform 0.3s ease;
        }

        .invoice-overlay.active .invoice-modal {
          transform: scale(1);
        }

        .invoice-header {
          background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
          color: white;
          padding: 24px;
          border-radius: 12px 12px 0 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .invoice-close-btn {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background 0.3s ease;
        }

        .invoice-close-btn:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .invoice-content {
          padding: 30px;
        }

        .invoice-table {
          width: 100%;
          border-collapse: collapse;
          margin: 20px 0;
        }

        .invoice-table th,
        .invoice-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #dee2e6;
        }

        .invoice-table th {
          background-color: #f8f9fa;
          font-weight: 600;
          color: #495057;
        }

        .invoice-table .text-end {
          text-align: right;
        }

        .total-section {
          background-color: #f8f9fa;
          padding: 15px;
          border-radius: 8px;
          margin-top: 20px;
        }

        .btn-print {
          background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          font-size: 14px;
          transition: all 0.3s ease;
          box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .btn-print:hover {
          background: linear-gradient(135deg, #218838 0%, #1ea085 100%);
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
        }

        .btn-download {
          background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          font-size: 14px;
          transition: all 0.3s ease;
          box-shadow: 0 2px 4px rgba(0, 123, 255, 0.2);
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .btn-download:hover {
          background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
        }

        .loading-spinner {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 200px;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #667eea;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>

      <div className={`invoice-overlay ${isOpen ? 'active' : ''}`} onClick={onClose}>
        <div className="invoice-modal" onClick={(e) => e.stopPropagation()}>
          <div className="invoice-header">
            <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
              <div style={{
                width: '40px',
                height: '40px',
                background: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '20px'
              }}>
                🛍️
              </div>
              <h2 style={{margin: 0}}>Invoice</h2>
            </div>
            <button className="invoice-close-btn" onClick={onClose}>
              ✕
            </button>
          </div>

          <div className="invoice-content">
            {loading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
              </div>
            ) : error ? (
              <div style={{color: '#dc3545', textAlign: 'center', padding: '20px'}}>
                {error}
              </div>
            ) : invoice ? (
              <>
                {/* Company Info */}
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '30px'}}>
                  <div>
                    <div style={{display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px'}}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '16px',
                        color: 'white'
                      }}>
                        🛍️
                      </div>
                      <h3 style={{margin: 0}}>{invoice.company_name || 'Company Name'}</h3>
                    </div>
                    <p>{invoice.company_address || 'Company Address'}</p>
                    <p>Phone: {invoice.company_phone || 'N/A'}</p>
                    <p>Email: {invoice.company_email || 'N/A'}</p>
                  </div>
                  <div style={{textAlign: 'right'}}>
                    <h4>Invoice #{invoice.invoice_number || 'N/A'}</h4>
                    <p>Order ID: {invoice.order?.order_number || 'N/A'}</p>
                    <p>Date: {invoice.invoice_date ? formatDate(invoice.invoice_date) : 'N/A'}</p>
                    <p>Due: {invoice.due_date ? formatDate(invoice.due_date) : 'N/A'}</p>
                  </div>
                </div>

                {/* Bill To */}
                {invoice.order.delivery_address && (
                  <div style={{marginBottom: '30px'}}>
                    <h4>Bill To</h4>
                    <address style={{fontStyle: 'normal'}}>
                      <strong>{invoice.order.delivery_address.full_name}</strong><br />
                      {invoice.order.delivery_address.address_line_1}<br />
                      {invoice.order.delivery_address.city}, {invoice.order.delivery_address.country}<br />
                      Phone: {invoice.order.delivery_address.phone_number}
                    </address>
                  </div>
                )}

                {/* Order Items */}
                <table className="invoice-table">
                  <thead>
                    <tr>
                      <th>Qty</th>
                      <th>Product</th>
                      <th className="text-end">Unit Price</th>
                      <th className="text-end">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {invoice.order.items && invoice.order.items.map((item, index) => (
                      <tr key={index}>
                        <td>{item.quantity || 0}</td>
                        <td>
                          {item.product_name || 'N/A'}
                          {item.variant_title && <br />}
                          {item.variant_title && <small style={{color: '#6c757d'}}>{item.variant_title}</small>}
                        </td>
                        <td className="text-end">{formatPrice(item.unit_price || 0)}</td>
                        <td className="text-end">{formatPrice(item.total_price || 0)}</td>
                      </tr>
                    ))}
                    <tr>
                      <td colSpan="3" className="text-end"><strong>Subtotal</strong></td>
                      <td className="text-end"><strong>{formatPrice(invoice.order.subtotal || 0)}</strong></td>
                    </tr>
                    {(invoice.order.shipping_cost || 0) > 0 && (
                      <tr>
                        <td colSpan="3" className="text-end">Shipping</td>
                        <td className="text-end">{formatPrice(invoice.order.shipping_cost || 0)}</td>
                      </tr>
                    )}
                    {(invoice.order.tax_amount || 0) > 0 && (
                      <tr>
                        <td colSpan="3" className="text-end">Tax</td>
                        <td className="text-end">{formatPrice(invoice.order.tax_amount || 0)}</td>
                      </tr>
                    )}
                    <tr className="total-section">
                      <td colSpan="3" className="text-end"><strong>TOTAL</strong></td>
                      <td className="text-end"><strong>{formatPrice(invoice.order.total_amount || 0)}</strong></td>
                    </tr>
                  </tbody>
                </table>

                {/* Payment Info */}
                {invoice.order.payment && (
                  <div style={{
                    backgroundColor: '#e3f2fd',
                    padding: '15px',
                    borderRadius: '8px',
                    marginTop: '20px'
                  }}>
                    <h5>Payment Information</h5>
                    <p><strong>Payment Method:</strong> {invoice.order.payment.payment_method?.name || 'N/A'}</p>
                    <p><strong>Status:</strong> {invoice.order.payment.status || 'N/A'}</p>
                    {invoice.order.payment.payment_method?.is_cod && (
                      <p><em>This is a Cash on Delivery order. Payment will be collected upon delivery.</em></p>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'center',
                  gap: '15px',
                  marginTop: '30px',
                  padding: '20px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '8px',
                  border: '1px solid #dee2e6'
                }}>
                  <button className="btn-print" onClick={() => printInvoicePDF(invoice.id)}>
                    🖨️ Print Invoice
                  </button>
                  <button className="btn-download" onClick={() => downloadInvoicePDF(invoice.id)}>
                    📄 Download PDF
                  </button>
                </div>
              </>
            ) : null}
          </div>
        </div>
      </div>
    </>
  )
}

export default InvoiceModal
