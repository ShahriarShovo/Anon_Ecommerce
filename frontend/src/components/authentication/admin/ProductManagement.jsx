import React, { useState, useEffect, memo } from 'react'
import { useAuth } from '../../../contexts/AuthContext'

const ProductManagement = memo(() => {
  const { user } = useAuth()
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [subcategories, setSubcategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [productToDelete, setProductToDelete] = useState(null)
  const [messageTimeout, setMessageTimeout] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    short_description: '',
    category: '',
    subcategory: '',
    product_type: 'simple',
    status: 'draft',
    price: '',
    old_price: '',
    option1_name: '',
    option2_name: '',
    option3_name: '',
    track_quantity: true,
    quantity: '',
    allow_backorder: false,
    weight: '',
    weight_unit: 'kg',
    requires_shipping: true,
    taxable: true,
    featured: false,
    tags: '',
    variants: [],
    images: []
  })
  const [selectedImages, setSelectedImages] = useState([])
  const [imagePreviewUrls, setImagePreviewUrls] = useState([])
  const [showVariantModal, setShowVariantModal] = useState(false)
  const [editingVariant, setEditingVariant] = useState(null)
  const [variantFormData, setVariantFormData] = useState({
    title: '',
    sku: '',
    barcode: '',
    price: '',
    old_price: '',
    quantity: '',
    track_quantity: true,
    allow_backorder: false,
    weight: '',
    weight_unit: 'kg',
    options: [], // Dynamic options array: [{name: 'Size', value: 'Small'}, {name: 'Color', value: 'Red'}]
    position: 1,
    is_active: true
  })

  // Variant Management Functions
  const openVariantModal = (variant = null) => {
    if (variant) {
      setEditingVariant(variant)
      // Convert variant options to dynamic format
      const options = []
      if (variant.option1_name && variant.option1_value) {
        options.push({ name: variant.option1_name, value: variant.option1_value })
      }
      if (variant.option2_name && variant.option2_value) {
        options.push({ name: variant.option2_name, value: variant.option2_value })
      }
      if (variant.option3_name && variant.option3_value) {
        options.push({ name: variant.option3_name, value: variant.option3_value })
      }
      
      setVariantFormData({
        title: variant.title || '',
        sku: variant.sku || '',
        barcode: variant.barcode || '',
        price: variant.price || '',
        old_price: variant.old_price || '',
        quantity: variant.quantity || '',
        track_quantity: variant.track_quantity !== false,
        allow_backorder: variant.allow_backorder || false,
        weight: variant.weight || '',
        weight_unit: variant.weight_unit || 'kg',
        options: options,
        position: variant.position || 1,
        is_active: variant.is_active !== false
      })
    } else {
      setEditingVariant(null)
      setVariantFormData({
        title: '',
        sku: '',
        barcode: '',
        price: '',
        old_price: '',
        quantity: '',
        track_quantity: true,
        allow_backorder: false,
        weight: '',
        weight_unit: 'kg',
        options: [],
        position: formData.variants.length + 1,
        is_active: true
      })
    }
    setShowVariantModal(true)
  }

  const closeVariantModal = () => {
    setShowVariantModal(false)
    setEditingVariant(null)
    setVariantFormData({
      title: '',
      sku: '',
      barcode: '',
      price: '',
      old_price: '',
      quantity: '',
      track_quantity: true,
      allow_backorder: false,
      weight: '',
      weight_unit: 'kg',
      options: [],
      position: 1,
      is_active: true
    })
  }

  // Dynamic Options Management
  const addOption = () => {
    setVariantFormData(prev => ({
      ...prev,
      options: [...prev.options, { name: '', value: '' }]
    }))
  }

  const removeOption = (index) => {
    setVariantFormData(prev => ({
      ...prev,
      options: prev.options.filter((_, i) => i !== index)
    }))
  }

  const updateOption = (index, field, value) => {
    setVariantFormData(prev => ({
      ...prev,
      options: prev.options.map((option, i) => 
        i === index ? { ...option, [field]: value } : option
      )
    }))
  }

  const handleVariantInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setVariantFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const saveVariant = () => {
    if (!variantFormData.price) {
      showMessage('Price is required for variant', 'error')
      return
    }

    // Convert dynamic options to backend format
    const variantData = { ...variantFormData }
    
    // Clear old option fields
    variantData.option1_name = ''
    variantData.option1_value = ''
    variantData.option2_name = ''
    variantData.option2_value = ''
    variantData.option3_name = ''
    variantData.option3_value = ''
    
    // Set option fields based on dynamic options (first 3 for legacy support)
    variantFormData.options.forEach((option, index) => {
      if (index < 3 && option.name && option.value) {
        variantData[`option${index + 1}_name`] = option.name
        variantData[`option${index + 1}_value`] = option.value
      }
    })
    
    // Add dynamic options for backend
    variantData.dynamic_options = variantFormData.options.map((option, index) => ({
      name: option.name,
      value: option.value,
      position: index + 1
    }))

    const newVariants = [...formData.variants]
    
    if (editingVariant) {
      // Update existing variant
      const index = newVariants.findIndex(v => v.id === editingVariant.id)
      if (index !== -1) {
        newVariants[index] = { ...editingVariant, ...variantData }
      }
    } else {
      // Add new variant
      const newVariant = {
        id: Date.now(), // Temporary ID for frontend
        ...variantData
      }
      newVariants.push(newVariant)
    }

    setFormData(prev => ({
      ...prev,
      variants: newVariants
    }))
    
    closeVariantModal()
    showMessage(editingVariant ? 'Variant updated successfully!' : 'Variant added successfully!', 'success')
  }

  const deleteVariant = (variantId) => {
    const newVariants = formData.variants.filter(v => v.id !== variantId)
    setFormData(prev => ({
      ...prev,
      variants: newVariants
    }))
    showMessage('Variant deleted successfully!', 'success')
  }

  // Get product image URL
  const getProductImageUrl = (product) => {
    console.log('Product:', product.title, 'Primary Image:', product.primary_image, 'Images:', product.images)
    
    // Try primary image first
    if (product.primary_image) {
      // Try image_url first - construct full URL (already has /media/ prefix)
      if (product.primary_image.image_url) {
        const fullUrl = `http://127.0.0.1:8000${product.primary_image.image_url}`
        console.log('Using primary image_url:', fullUrl)
        return fullUrl
      }
      // Try image field with backend URL
      if (product.primary_image.image) {
        const fullUrl = `http://127.0.0.1:8000${product.primary_image.image}`
        console.log('Using primary image field:', fullUrl)
        return fullUrl
      }
    }
    
    // Try first image from images array
    if (product.images && product.images.length > 0) {
      const firstImage = product.images[0]
      if (firstImage.image_url) {
        const fullUrl = `http://127.0.0.1:8000${firstImage.image_url}`
        console.log('Using first image_url:', fullUrl)
        return fullUrl
      }
      if (firstImage.image) {
        const fullUrl = `http://127.0.0.1:8000${firstImage.image}`
        console.log('Using first image field:', fullUrl)
        return fullUrl
      }
    }
    
    console.log('No image found for product:', product.title)
    return null
  }

  // Show message with auto-hide
  const showMessage = (message, type) => {
    if (messageTimeout) {
      clearTimeout(messageTimeout)
    }

    if (type === 'success') {
      setSuccess(message)
      setError('')
    } else {
      setError(message)
      setSuccess('')
    }

    const timeout = setTimeout(() => {
      setSuccess('')
      setError('')
      setMessageTimeout(null)
    }, 5000)

    setMessageTimeout(timeout)
  }

  // Clear messages manually
  const clearMessages = () => {
    if (messageTimeout) {
      clearTimeout(messageTimeout)
      setMessageTimeout(null)
    }
    setSuccess('')
    setError('')
  }

  // Fetch categories
  const fetchCategories = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://127.0.0.1:8000/api/products/category/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setCategories(data)
      }
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }

  // Fetch subcategories
  const fetchSubCategories = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://127.0.0.1:8000/api/products/subcategory/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setSubcategories(data)
      }
    } catch (error) {
      console.error('Error fetching subcategories:', error)
    }
  }

  // Fetch products
  const fetchProducts = async () => {
    setLoading(true)
    setError('')
    try {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        showMessage('No authentication token found. Please login again.', 'error')
        return
      }
      
      const response = await fetch('http://127.0.0.1:8000/api/products/product/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('API Response:', data)
        console.log('Products with images:', data.results?.map(p => ({
          title: p.title,
          primary_image: p.primary_image,
          images: p.images
        })))
        setProducts(data.results || data)
      } else {
        showMessage('Failed to fetch products', 'error')
      }
    } catch (error) {
      showMessage('Error fetching products: ' + error.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  // Create product
  const createProduct = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      console.log('Creating product with data:', formData)
      const token = localStorage.getItem('access_token')
      const formDataToSend = new FormData()
      
      // Add basic fields
      Object.keys(formData).forEach(key => {
        if (key !== 'variants' && key !== 'images' && formData[key] !== '') {
          formDataToSend.append(key, formData[key])
        }
      })

      // Add uploaded images
      selectedImages.forEach((image, index) => {
        formDataToSend.append('uploaded_images', image)
      })

      // Add variants with dynamic options
      if (formData.variants && formData.variants.length > 0) {
        console.log('Sending variants:', formData.variants)
        formData.variants.forEach((variant, index) => {
          console.log(`Variant ${index}:`, variant)
          // Add variant basic data
          Object.keys(variant).forEach(key => {
            if (key !== 'dynamic_options' && key !== 'options' && variant[key] !== '') {
              formDataToSend.append(`variants[${index}][${key}]`, variant[key])
            }
          })
          
          // Add dynamic options
          if (variant.dynamic_options && variant.dynamic_options.length > 0) {
            console.log(`Variant ${index} dynamic options:`, variant.dynamic_options)
            variant.dynamic_options.forEach((option, optionIndex) => {
              formDataToSend.append(`variants[${index}][dynamic_options][${optionIndex}][name]`, option.name)
              formDataToSend.append(`variants[${index}][dynamic_options][${optionIndex}][value]`, option.value)
              formDataToSend.append(`variants[${index}][dynamic_options][${optionIndex}][position]`, option.position)
            })
          }
        })
      }

      const response = await fetch('http://127.0.0.1:8000/api/products/product/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataToSend
      })

      if (response.ok) {
        showMessage(`Product "${formData.title}" created successfully!`, 'success')
        setFormData({
          title: '', description: '', short_description: '', category: '', subcategory: '',
          product_type: 'simple', status: 'draft', price: '', old_price: '',
          option1_name: '', option2_name: '', option3_name: '',
          track_quantity: true, quantity: '', allow_backorder: false, weight: '', weight_unit: 'kg',
          requires_shipping: true, taxable: true, featured: false, tags: '', variants: [], images: []
        })
        clearAllImages()
        setShowCreateForm(false)
        fetchProducts()
      } else {
        const errorData = await response.json()
        console.error('Product creation error:', errorData)
        console.error('Response status:', response.status)
        console.error('Response headers:', response.headers)
        
        // Show detailed error message
        let errorMessage = 'Unknown error'
        if (errorData.detail) {
          errorMessage = errorData.detail
        } else if (errorData.message) {
          errorMessage = errorData.message
        } else if (typeof errorData === 'object') {
          errorMessage = JSON.stringify(errorData, null, 2)
        }
        
        showMessage(`Failed to create product "${formData.title}": ${errorMessage}`, 'error')
      }
    } catch (error) {
      showMessage(`Error creating product "${formData.title}": ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // Update product
  const updateProduct = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const token = localStorage.getItem('access_token')
      const formDataToSend = new FormData()
      
      // Add basic fields
      Object.keys(formData).forEach(key => {
        if (key !== 'variants' && key !== 'images' && formData[key] !== '') {
          formDataToSend.append(key, formData[key])
        }
      })

      // Add uploaded images
      selectedImages.forEach((image, index) => {
        formDataToSend.append('uploaded_images', image)
      })

      const response = await fetch(`http://127.0.0.1:8000/api/products/product/${editingProduct.slug}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataToSend
      })

      if (response.ok) {
        showMessage(`Product "${formData.title}" updated successfully!`, 'success')
        setFormData({
          title: '', description: '', short_description: '', category: '', subcategory: '',
          product_type: 'simple', status: 'draft', price: '', old_price: '',
          option1_name: '', option2_name: '', option3_name: '',
          track_quantity: true, quantity: '', allow_backorder: false, weight: '', weight_unit: 'kg',
          requires_shipping: true, taxable: true, featured: false, tags: '', variants: [], images: []
        })
        clearAllImages()
        setEditingProduct(null)
        setShowCreateForm(false)
        fetchProducts()
      } else {
        const errorData = await response.json()
        showMessage(`Failed to update product "${formData.title}": ${errorData.message || 'Unknown error'}`, 'error')
      }
    } catch (error) {
      showMessage(`Error updating product "${formData.title}": ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // Delete product
  const deleteProduct = async () => {
    if (!productToDelete) return

    setLoading(true)
    setError('')
    
    try {
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`http://127.0.0.1:8000/api/products/product/${productToDelete.slug}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        showMessage(`Product "${productToDelete.title}" deleted successfully!`, 'success')
        setShowDeleteModal(false)
        setProductToDelete(null)
        fetchProducts()
      } else {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }))
        showMessage(`Failed to delete product "${productToDelete.title}": ${errorData.message || 'Unknown error'}`, 'error')
      }
    } catch (error) {
      showMessage(`Error deleting product "${productToDelete.title}": ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // Show delete confirmation modal
  const showDeleteConfirmation = (product) => {
    setProductToDelete(product)
    setShowDeleteModal(true)
  }

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  // Handle image selection
  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files)
    if (files.length > 0) {
      setSelectedImages(prev => [...prev, ...files])
      
      // Create preview URLs
      const newPreviewUrls = files.map(file => URL.createObjectURL(file))
      setImagePreviewUrls(prev => [...prev, ...newPreviewUrls])
    }
  }

  // Remove image
  const removeImage = (index) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index))
    setImagePreviewUrls(prev => {
      URL.revokeObjectURL(prev[index])
      return prev.filter((_, i) => i !== index)
    })
  }

  // Clear all images
  const clearAllImages = () => {
    imagePreviewUrls.forEach(url => URL.revokeObjectURL(url))
    setSelectedImages([])
    setImagePreviewUrls([])
  }

  // Start editing product
  const startEdit = (product) => {
    setEditingProduct(product)
    setFormData({
      title: product.title,
      description: product.description || '',
      short_description: product.short_description || '',
      category: product.category || '',
      subcategory: product.subcategory || '',
      product_type: product.product_type || 'simple',
      status: product.status || 'draft',
      price: product.price || '',
      old_price: product.old_price || '',
      option1_name: product.option1_name || '',
      option2_name: product.option2_name || '',
      option3_name: product.option3_name || '',
      track_quantity: product.track_quantity !== false,
      quantity: product.quantity || '',
      allow_backorder: product.allow_backorder || false,
      weight: product.weight || '',
      weight_unit: product.weight_unit || 'kg',
      requires_shipping: product.requires_shipping !== false,
      taxable: product.taxable !== false,
      featured: product.featured || false,
      tags: product.tags || '',
      variants: product.variants || [],
      images: product.images || []
    })
    setShowCreateForm(true)
  }

  // Cancel form
  const cancelForm = () => {
    setShowCreateForm(false)
    setEditingProduct(null)
    setFormData({
      title: '', description: '', short_description: '', category: '', subcategory: '',
      product_type: 'simple', status: 'draft', price: '', old_price: '',
      option1_name: '', option2_name: '', option3_name: '',
      track_quantity: true, quantity: '', allow_backorder: false, weight: '', weight_unit: 'kg',
      requires_shipping: true, taxable: true, featured: false, tags: '', variants: [], images: []
    })
    clearAllImages()
    clearMessages()
  }

  // Cancel delete modal
  const cancelDelete = () => {
    setShowDeleteModal(false)
    setProductToDelete(null)
  }

  // Get category name by ID
  const getCategoryName = (categoryId) => {
    const category = categories.find(cat => cat.id === categoryId)
    return category ? category.name : 'No Category'
  }

  // Get subcategory name by ID
  const getSubCategoryName = (subcategoryId) => {
    const subcategory = subcategories.find(sub => sub.id === subcategoryId)
    return subcategory ? subcategory.name : 'No SubCategory'
  }

  // Load data on component mount
  useEffect(() => {
    fetchCategories()
    fetchSubCategories()
    fetchProducts()
  }, [])

  return (
    <div style={{ 
      background: 'transparent', 
      minHeight: 'calc(100vh - 20px)'
    }}>
      <div style={{ 
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        {/* Header */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          marginBottom: '32px'
        }}>
          <div>
            <h1 style={{ 
              fontSize: '32px', 
              fontWeight: '600', 
              color: '#212b36',
              margin: '0 0 8px 0'
            }}>Product Management</h1>
            <p style={{ 
              fontSize: '16px', 
              color: '#637381',
              margin: '0'
            }}>Create, edit, and manage your products with variants</p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              color: 'white',
              background: '#5c6ac4',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = '#4c51bf'
            }}
            onMouseLeave={(e) => {
              e.target.style.background = '#5c6ac4'
            }}
          >
            <span style={{ marginRight: '8px' }}>➕</span>
            Add Product
          </button>
        </div>

        {/* Messages */}
        {error && (
          <div style={{
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '24px',
            color: '#dc2626',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <span>{error}</span>
            <button
              onClick={clearMessages}
              style={{
                background: 'none',
                border: 'none',
                color: '#dc2626',
                cursor: 'pointer',
                fontSize: '18px',
                padding: '0',
                marginLeft: '12px'
              }}
            >
              ×
            </button>
          </div>
        )}
        
        {success && (
          <div style={{
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '24px',
            color: '#008060',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <span>{success}</span>
            <button
              onClick={clearMessages}
              style={{
                background: 'none',
                border: 'none',
                color: '#008060',
                cursor: 'pointer',
                fontSize: '18px',
                padding: '0',
                marginLeft: '12px'
              }}
            >
              ×
            </button>
          </div>
        )}

        {/* Create/Edit Form */}
        {showCreateForm && (
          <div style={{
            background: 'white',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e1e3e5',
            padding: '32px',
            marginBottom: '32px'
          }}>
            <h2 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#212b36',
              margin: '0 0 24px 0'
            }}>
              {editingProduct ? 'Edit Product' : 'Create New Product'}
            </h2>
            
            <form onSubmit={editingProduct ? updateProduct : createProduct}>
              {/* Basic Information */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#212b36', margin: '0 0 16px 0' }}>
                  Basic Information
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '16px' }}>
                  <div>
                    <label style={{ 
                      display: 'block', 
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#212b36',
                      marginBottom: '8px'
                    }}>
                      Product Title *
                    </label>
                    <input
                      type="text"
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      required
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#212b36'
                      }}
                      placeholder="Enter product title"
                    />
                  </div>
                  
                  <div>
                    <label style={{ 
                      display: 'block', 
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#212b36',
                      marginBottom: '8px'
                    }}>
                      Product Type *
                    </label>
                    <select
                      name="product_type"
                      value={formData.product_type}
                      onChange={handleInputChange}
                      required
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#212b36',
                        background: 'white'
                      }}
                    >
                      <option value="simple">Simple Product</option>
                      <option value="variable">Variable Product (with variants)</option>
                    </select>
                    <p style={{ 
                      fontSize: '12px', 
                      color: '#6b7280', 
                      marginTop: '4px',
                      fontStyle: 'italic'
                    }}>
                      Choose "Variable Product" to create products with multiple variants (size, color, etc.)
                    </p>
                  </div>
                  
                  <div>
                    <label style={{ 
                      display: 'block', 
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#212b36',
                      marginBottom: '8px'
                    }}>
                      Description
                    </label>
                    <textarea
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      rows="4"
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#212b36',
                        resize: 'vertical'
                      }}
                      placeholder="Enter product description"
                    />
                  </div>
                </div>
              </div>

              {/* Categorization */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#212b36', margin: '0 0 16px 0' }}>
                  Categorization
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ 
                      display: 'block', 
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#212b36',
                      marginBottom: '8px'
                    }}>
                      Category
                    </label>
                    <select
                      name="category"
                      value={formData.category}
                      onChange={handleInputChange}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#212b36',
                        background: 'white'
                      }}
                    >
                      <option value="">Select a category</option>
                      {categories.map(category => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label style={{ 
                      display: 'block', 
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#212b36',
                      marginBottom: '8px'
                    }}>
                      SubCategory
                    </label>
                    <select
                      name="subcategory"
                      value={formData.subcategory}
                      onChange={handleInputChange}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#212b36',
                        background: 'white'
                      }}
                    >
                      <option value="">Select a subcategory</option>
                      {subcategories
                        .filter(sub => !formData.category || sub.category === parseInt(formData.category))
                        .map(subcategory => (
                        <option key={subcategory.id} value={subcategory.id}>
                          {subcategory.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Pricing */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#212b36', margin: '0 0 16px 0' }}>
                  Pricing
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ 
                      display: 'block', 
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#212b36',
                      marginBottom: '8px'
                    }}>
                      Price *
                    </label>
                    <input
                      type="number"
                      name="price"
                      value={formData.price}
                      onChange={handleInputChange}
                      step="0.01"
                      min="0"
                      required
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#212b36'
                      }}
                      placeholder="0.00"
                    />
                  </div>
                  
                  <div>
                    <label style={{ 
                      display: 'block', 
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#212b36',
                      marginBottom: '8px'
                    }}>
                      Old Price
                    </label>
                    <input
                      type="number"
                      name="old_price"
                      value={formData.old_price}
                      onChange={handleInputChange}
                      step="0.01"
                      min="0"
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#212b36'
                      }}
                      placeholder="0.00"
                    />
                  </div>
                  
                </div>
              </div>


              {/* Product Variants Management */}
              {formData.product_type === 'variable' && (
                <div style={{ marginBottom: '24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#212b36', margin: '0' }}>
                      Product Variants
                    </h3>
                    <button
                      type="button"
                      onClick={() => openVariantModal()}
                      style={{
                        background: '#5c6ac4',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        padding: '8px 16px',
                        fontSize: '14px',
                        fontWeight: '500',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                    >
                      <span>+</span>
                      Add Variant
                    </button>
                  </div>

                  {formData.variants.length > 0 ? (
                    <div style={{ 
                      border: '1px solid #e1e3e5', 
                      borderRadius: '8px', 
                      overflow: 'hidden',
                      background: 'white'
                    }}>
                      {formData.variants.map((variant, index) => (
                        <div key={variant.id || index} style={{
                          padding: '16px',
                          borderBottom: index < formData.variants.length - 1 ? '1px solid #e1e3e5' : 'none',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}>
                          <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                              <div>
                                <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', fontWeight: '600', color: '#212b36' }}>
                                  {variant.title || `${formData.option1_name || 'Option 1'}: ${variant.option1_value || 'N/A'}`}
                                </h4>
                                <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#6b7280' }}>
                                  {variant.option1_value && (
                                    <span>{formData.option1_name}: {variant.option1_value}</span>
                                  )}
                                  {variant.option2_value && (
                                    <span>{formData.option2_name}: {variant.option2_value}</span>
                                  )}
                                  {variant.option3_value && (
                                    <span>{formData.option3_name}: {variant.option3_value}</span>
                                  )}
                                </div>
                              </div>
                              <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#6b7280' }}>
                                <span>Price: ${variant.price}</span>
                                {variant.old_price && <span>Old: ${variant.old_price}</span>}
                                <span>Qty: {variant.quantity || 0}</span>
                              </div>
                            </div>
                          </div>
                          <div style={{ display: 'flex', gap: '8px' }}>
                            <button
                              type="button"
                              onClick={() => openVariantModal(variant)}
                              style={{
                                background: 'transparent',
                                color: '#5c6ac4',
                                border: '1px solid #5c6ac4',
                                borderRadius: '4px',
                                padding: '4px 8px',
                                fontSize: '12px',
                                cursor: 'pointer'
                              }}
                            >
                              Edit
                            </button>
                            <button
                              type="button"
                              onClick={() => deleteVariant(variant.id)}
                              style={{
                                background: 'transparent',
                                color: '#dc2626',
                                border: '1px solid #dc2626',
                                borderRadius: '4px',
                                padding: '4px 8px',
                                fontSize: '12px',
                                cursor: 'pointer'
                              }}
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div style={{
                      border: '2px dashed #d1d5db',
                      borderRadius: '8px',
                      padding: '32px',
                      textAlign: 'center',
                      background: '#f9fafb'
                    }}>
                      <p style={{ margin: '0 0 16px 0', color: '#6b7280' }}>
                        No variants added yet. Click "Add Variant" to create your first variant.
                      </p>
                      <button
                        type="button"
                        onClick={() => openVariantModal()}
                        style={{
                          background: '#5c6ac4',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '8px 16px',
                          fontSize: '14px',
                          fontWeight: '500',
                          cursor: 'pointer'
                        }}
                      >
                        Add Your First Variant
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Inventory */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#212b36', margin: '0 0 16px 0' }}>
                  Inventory
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ 
                      display: 'block', 
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#212b36',
                      marginBottom: '8px'
                    }}>
                      Quantity
                    </label>
                    <input
                      type="number"
                      name="quantity"
                      value={formData.quantity}
                      onChange={handleInputChange}
                      min="0"
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#212b36'
                      }}
                      placeholder="0"
                    />
                  </div>
                  
                  <div>
                    <label style={{ 
                      display: 'block', 
                      fontSize: '14px', 
                      fontWeight: '500', 
                      color: '#212b36',
                      marginBottom: '8px'
                    }}>
                      Status
                    </label>
                    <select
                      name="status"
                      value={formData.status}
                      onChange={handleInputChange}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#212b36',
                        background: 'white'
                      }}
                    >
                      <option value="draft">Draft</option>
                      <option value="active">Active</option>
                      <option value="archived">Archived</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Product Images */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#212b36', margin: '0 0 16px 0' }}>
                  Product Images
                </h3>
                
                {/* Image Upload */}
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ 
                    display: 'block', 
                    fontSize: '14px', 
                    fontWeight: '500', 
                    color: '#212b36',
                    marginBottom: '8px'
                  }}>
                    Upload Images
                  </label>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleImageSelect}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px dashed #e1e3e5',
                      borderRadius: '8px',
                      fontSize: '14px',
                      color: '#212b36',
                      background: '#fafbfc',
                      cursor: 'pointer'
                    }}
                  />
                  <p style={{ 
                    fontSize: '12px', 
                    color: '#637381', 
                    margin: '8px 0 0 0' 
                  }}>
                    Select multiple images. The first image will be set as primary.
                  </p>
                </div>

                {/* Image Previews */}
                {imagePreviewUrls.length > 0 && (
                  <div>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between',
                      marginBottom: '12px'
                    }}>
                      <span style={{ 
                        fontSize: '14px', 
                        fontWeight: '500', 
                        color: '#212b36' 
                      }}>
                        Selected Images ({imagePreviewUrls.length})
                      </span>
                      <button
                        type="button"
                        onClick={clearAllImages}
                        style={{
                          padding: '6px 12px',
                          border: '1px solid #e1e3e5',
                          borderRadius: '6px',
                          fontSize: '12px',
                          fontWeight: '500',
                          color: '#dc2626',
                          background: 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.background = '#fef2f2'
                          e.target.style.borderColor = '#dc2626'
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.background = 'white'
                          e.target.style.borderColor = '#e1e3e5'
                        }}
                      >
                        Clear All
                      </button>
                    </div>
                    
                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', 
                      gap: '12px' 
                    }}>
                      {imagePreviewUrls.map((url, index) => (
                        <div
                          key={index}
                          style={{
                            position: 'relative',
                            border: '1px solid #e1e3e5',
                            borderRadius: '8px',
                            overflow: 'hidden',
                            background: '#fafbfc'
                          }}
                        >
                          <img
                            src={url}
                            alt={`Preview ${index + 1}`}
                            style={{
                              width: '100%',
                              height: '120px',
                              objectFit: 'cover'
                            }}
                          />
                          {index === 0 && (
                            <div style={{
                              position: 'absolute',
                              top: '4px',
                              left: '4px',
                              background: '#5c6ac4',
                              color: 'white',
                              padding: '2px 6px',
                              borderRadius: '4px',
                              fontSize: '10px',
                              fontWeight: '500'
                            }}>
                              Primary
                            </div>
                          )}
                          <button
                            type="button"
                            onClick={() => removeImage(index)}
                            style={{
                              position: 'absolute',
                              top: '4px',
                              right: '4px',
                              width: '24px',
                              height: '24px',
                              border: 'none',
                              borderRadius: '50%',
                              background: 'rgba(220, 38, 38, 0.9)',
                              color: 'white',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: '12px',
                              fontWeight: 'bold'
                            }}
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Form Actions */}
              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '12px 24px',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: 'white',
                    background: loading ? '#9ca3af' : '#5c6ac4',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  {loading ? 'Saving...' : (editingProduct ? 'Update Product' : 'Create Product')}
                </button>
                
                <button
                  type="button"
                  onClick={cancelForm}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '12px 24px',
                    border: '1px solid #e1e3e5',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#212b36',
                    background: 'white',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Variant Modal */}
        {showVariantModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '24px',
              width: '90%',
              maxWidth: '600px',
              maxHeight: '90vh',
              overflow: 'auto',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#212b36', margin: '0' }}>
                  {editingVariant ? 'Edit Variant' : 'Add Variant'}
                </h2>
                <button
                  type="button"
                  onClick={closeVariantModal}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    fontSize: '24px',
                    cursor: 'pointer',
                    color: '#6b7280'
                  }}
                >
                  ×
                </button>
              </div>

              <form onSubmit={(e) => { e.preventDefault(); saveVariant(); }}>
                <div style={{ display: 'grid', gap: '16px' }}>
                  {/* Option Names Section */}
                  <div style={{ 
                    background: '#f8fafc', 
                    padding: '16px', 
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0'
                  }}>
                    <h4 style={{ 
                      fontSize: '14px', 
                      fontWeight: '600', 
                      color: '#212b36', 
                      margin: '0 0 12px 0' 
                    }}>
                      Define Variant Options
                    </h4>
                    <p style={{ 
                      fontSize: '12px', 
                      color: '#6b7280', 
                      margin: '0 0 16px 0',
                      fontStyle: 'italic'
                    }}>
                      Define the options for this variant (e.g., Size, Color, Material)
                    </p>
                    
                    {/* Dynamic Options */}
                    {variantFormData.options.map((option, index) => (
                      <div key={index} style={{ 
                        display: 'grid', 
                        gridTemplateColumns: '1fr 1fr auto', 
                        gap: '12px', 
                        alignItems: 'end',
                        padding: '12px',
                        background: '#f8fafc',
                        borderRadius: '6px',
                        border: '1px solid #e2e8f0'
                      }}>
                        <div>
                          <label style={{ display: 'block', fontSize: '12px', fontWeight: '500', color: '#212b36', marginBottom: '4px' }}>
                            Option Name
                          </label>
                          <input
                            type="text"
                            value={option.name}
                            onChange={(e) => updateOption(index, 'name', e.target.value)}
                            placeholder="e.g., Size, Color, Material"
                            style={{
                              width: '100%',
                              padding: '8px 12px',
                              border: '1px solid #e1e3e5',
                              borderRadius: '6px',
                              fontSize: '12px',
                              color: '#212b36'
                            }}
                          />
                        </div>
                        
                        <div>
                          <label style={{ display: 'block', fontSize: '12px', fontWeight: '500', color: '#212b36', marginBottom: '4px' }}>
                            Option Value
                          </label>
                          <input
                            type="text"
                            value={option.value}
                            onChange={(e) => updateOption(index, 'value', e.target.value)}
                            placeholder="e.g., Small, Red, Cotton"
                            style={{
                              width: '100%',
                              padding: '8px 12px',
                              border: '1px solid #e1e3e5',
                              borderRadius: '6px',
                              fontSize: '12px',
                              color: '#212b36'
                            }}
                          />
                        </div>
                        
                        <button
                          type="button"
                          onClick={() => removeOption(index)}
                          style={{
                            background: '#ef4444',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '8px 12px',
                            fontSize: '12px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}
                        >
                          🗑️ Remove
                        </button>
                      </div>
                    ))}
                    
                    {/* Add Option Button */}
                    <button
                      type="button"
                      onClick={addOption}
                      style={{
                        background: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        padding: '12px 16px',
                        fontSize: '14px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        justifyContent: 'center',
                        marginTop: '8px'
                      }}
                    >
                      ➕ Add Option
                    </button>
                  </div>

                  {/* Basic Information */}
                  <div>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#212b36', marginBottom: '8px' }}>
                      Variant Title
                    </label>
                    <input
                      type="text"
                      name="title"
                      value={variantFormData.title}
                      onChange={handleVariantInputChange}
                      placeholder="e.g., Small - Red - Cotton"
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e1e3e5',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#212b36'
                      }}
                    />
                  </div>


                  {/* Pricing */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#212b36', marginBottom: '8px' }}>
                        Price *
                      </label>
                      <input
                        type="number"
                        name="price"
                        value={variantFormData.price}
                        onChange={handleVariantInputChange}
                        step="0.01"
                        min="0"
                        required
                        style={{
                          width: '100%',
                          padding: '12px 16px',
                          border: '1px solid #e1e3e5',
                          borderRadius: '8px',
                          fontSize: '14px',
                          color: '#212b36'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#212b36', marginBottom: '8px' }}>
                        Old Price
                      </label>
                      <input
                        type="number"
                        name="old_price"
                        value={variantFormData.old_price}
                        onChange={handleVariantInputChange}
                        step="0.01"
                        min="0"
                        style={{
                          width: '100%',
                          padding: '12px 16px',
                          border: '1px solid #e1e3e5',
                          borderRadius: '8px',
                          fontSize: '14px',
                          color: '#212b36'
                        }}
                      />
                    </div>
                  </div>

                  {/* Inventory */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#212b36', marginBottom: '8px' }}>
                        Quantity
                      </label>
                      <input
                        type="number"
                        name="quantity"
                        value={variantFormData.quantity}
                        onChange={handleVariantInputChange}
                        min="0"
                        style={{
                          width: '100%',
                          padding: '12px 16px',
                          border: '1px solid #e1e3e5',
                          borderRadius: '8px',
                          fontSize: '14px',
                          color: '#212b36'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#212b36', marginBottom: '8px' }}>
                        SKU
                      </label>
                      <input
                        type="text"
                        name="sku"
                        value={variantFormData.sku}
                        onChange={handleVariantInputChange}
                        placeholder="Stock Keeping Unit"
                        style={{
                          width: '100%',
                          padding: '12px 16px',
                          border: '1px solid #e1e3e5',
                          borderRadius: '8px',
                          fontSize: '14px',
                          color: '#212b36'
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
                  <button
                    type="button"
                    onClick={closeVariantModal}
                    style={{
                      background: 'transparent',
                      color: '#6b7280',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      padding: '8px 16px',
                      fontSize: '14px',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    style={{
                      background: '#5c6ac4',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      padding: '8px 16px',
                      fontSize: '14px',
                      cursor: 'pointer'
                    }}
                  >
                    {editingVariant ? 'Update Variant' : 'Add Variant'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Products List */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          border: '1px solid #e1e3e5',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '24px',
            borderBottom: '1px solid #e1e3e5'
          }}>
            <h3 style={{ 
              fontSize: '18px', 
              fontWeight: '600', 
              color: '#212b36',
              margin: '0'
            }}>Products ({products.length})</h3>
          </div>

          {loading ? (
            <div style={{ 
              padding: '48px', 
              textAlign: 'center',
              color: '#637381'
            }}>
              Loading products...
            </div>
          ) : products.length === 0 ? (
            <div style={{ 
              padding: '48px', 
              textAlign: 'center',
              color: '#637381'
            }}>
              No products found. Create your first product!
            </div>
          ) : (
            <div style={{ padding: '24px' }}>
              <div style={{ display: 'grid', gap: '16px' }}>
                {products.map((product) => (
                  <div
                    key={product.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '20px',
                      border: '1px solid #f3f4f6',
                      borderRadius: '8px',
                      background: '#fafbfc'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      {/* Product Image */}
                      <div style={{
                        width: '80px',
                        height: '80px',
                        borderRadius: '8px',
                        overflow: 'hidden',
                        marginRight: '16px',
                        background: '#f3f4f6',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: '2px solid #e1e3e5',
                        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
                      }}>
                        {getProductImageUrl(product) ? (
                          <img
                            src={getProductImageUrl(product)}
                            alt={product.primary_image?.alt_text || product.title}
                            style={{
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover',
                              transition: 'transform 0.2s ease'
                            }}
                            onError={(e) => {
                              console.log('Image failed to load:', e.target.src)
                              e.target.style.display = 'none'
                              e.target.nextSibling.style.display = 'flex'
                            }}
                            onLoad={(e) => {
                              console.log('Image loaded successfully:', e.target.src)
                            }}
                            onMouseEnter={(e) => {
                              e.target.style.transform = 'scale(1.05)'
                            }}
                            onMouseLeave={(e) => {
                              e.target.style.transform = 'scale(1)'
                            }}
                          />
                        ) : null}
                        <div style={{
                          display: getProductImageUrl(product) ? 'none' : 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          width: '100%',
                          height: '100%',
                          background: 'linear-gradient(135deg, #5c6ac4 0%, #7c3aed 100%)',
                          color: 'white',
                          fontSize: '28px',
                          fontWeight: 'bold'
                        }}>
                          📦
                        </div>
                      </div>
                      
                      <div>
                        <h4 style={{ 
                          margin: '0 0 4px 0', 
                          fontSize: '16px', 
                          fontWeight: '600', 
                          color: '#212b36' 
                        }}>
                          {product.title}
                        </h4>
                        <p style={{ 
                          margin: '0 0 4px 0', 
                          fontSize: '14px', 
                          color: '#637381' 
                        }}>
                          Category: {getCategoryName(product.category)}
                        </p>
                        <p style={{ 
                          margin: '0 0 4px 0', 
                          fontSize: '12px', 
                          color: '#5c6ac4',
                          fontWeight: '500'
                        }}>
                          Status: {product.status} | Price: ${product.price || '0.00'}
                        </p>
                        {product.variant_count > 0 && (
                          <p style={{ 
                            margin: '0', 
                            fontSize: '12px', 
                            color: '#10b981',
                            fontWeight: '500'
                          }}>
                            {product.variant_count} variant{product.variant_count > 1 ? 's' : ''}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => startEdit(product)}
                        style={{
                          padding: '8px 12px',
                          border: '1px solid #e1e3e5',
                          borderRadius: '6px',
                          fontSize: '12px',
                          fontWeight: '500',
                          color: '#212b36',
                          background: 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.background = '#f6f7f9'
                          e.target.style.borderColor = '#5c6ac4'
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.background = 'white'
                          e.target.style.borderColor = '#e1e3e5'
                        }}
                      >
                        Edit
                      </button>
                      
                      <button
                        onClick={() => showDeleteConfirmation(product)}
                        style={{
                          padding: '8px 12px',
                          border: '1px solid #fecaca',
                          borderRadius: '6px',
                          fontSize: '12px',
                          fontWeight: '500',
                          color: '#dc2626',
                          background: 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.background = '#fef2f2'
                          e.target.style.borderColor = '#dc2626'
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.background = 'white'
                          e.target.style.borderColor = '#fecaca'
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '32px',
              maxWidth: '400px',
              width: '90%',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
            }}>
              <div style={{
                width: '64px',
                height: '64px',
                background: '#fef2f2',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 24px'
              }}>
                <span style={{ fontSize: '24px' }}>⚠️</span>
              </div>
              
              <h3 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#212b36',
                margin: '0 0 12px 0',
                textAlign: 'center'
              }}>
                Delete Product
              </h3>
              
              <p style={{
                fontSize: '16px',
                color: '#637381',
                margin: '0 0 24px 0',
                textAlign: 'center',
                lineHeight: '1.5'
              }}>
                Are you sure you want to delete <strong>"{productToDelete?.title}"</strong>? 
                This action cannot be undone and will also delete all associated variants and images.
              </p>
              
              <div style={{
                display: 'flex',
                gap: '12px',
                justifyContent: 'center'
              }}>
                <button
                  onClick={cancelDelete}
                  style={{
                    padding: '12px 24px',
                    border: '1px solid #e1e3e5',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#212b36',
                    background: 'white',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = '#f6f7f9'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = 'white'
                  }}
                >
                  Cancel
                </button>
                
                <button
                  onClick={deleteProduct}
                  disabled={loading}
                  style={{
                    padding: '12px 24px',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: 'white',
                    background: loading ? '#9ca3af' : '#dc2626',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) {
                      e.target.style.background = '#b91c1c'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!loading) {
                      e.target.style.background = '#dc2626'
                    }
                  }}
                >
                  {loading ? 'Deleting...' : 'Delete Product'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
})

export default ProductManagement
