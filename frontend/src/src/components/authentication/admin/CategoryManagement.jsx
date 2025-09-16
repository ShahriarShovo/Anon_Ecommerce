import React, { useState, useEffect, memo } from 'react'
import { useAuth } from '../../../contexts/AuthContext'

const CategoryManagement = memo(() => {
  const { user } = useAuth()
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingCategory, setEditingCategory] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    image: null
  })
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [categoryToDelete, setCategoryToDelete] = useState(null)
  const [messageTimeout, setMessageTimeout] = useState(null)

  // Show message with auto-hide
  const showMessage = (message, type) => {
    // Clear existing timeout
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

    // Set auto-hide timeout
    const timeout = setTimeout(() => {
      setSuccess('')
      setError('')
      setMessageTimeout(null)
    }, 5000) // Hide after 5 seconds

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

  // Fetch categories from API
  const fetchCategories = async () => {
    setLoading(true)
    setError('')
    try {
      const token = localStorage.getItem('access_token')
      console.log('Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'No token found')
      
      if (!token) {
        showMessage('No authentication token found. Please login again.', 'error')
        return
      }
      
      const response = await fetch('http://127.0.0.1:8000/api/products/category/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setCategories(data)
      } else {
        showMessage('Failed to fetch categories', 'error')
      }
    } catch (error) {
      showMessage('Error fetching categories: ' + error.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  // Create new category
  const createCategory = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const token = localStorage.getItem('access_token')
      const formDataToSend = new FormData()
      formDataToSend.append('name', formData.name)
      formDataToSend.append('slug', formData.slug)
      formDataToSend.append('description', formData.description)
      if (formData.image) {
        formDataToSend.append('image', formData.image)
      }

      const response = await fetch('http://127.0.0.1:8000/api/products/category/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataToSend
      })

      if (response.ok) {
        showMessage(`Category "${formData.name}" created successfully!`, 'success')
        setFormData({ name: '', slug: '', description: '', image: null })
        setShowCreateForm(false)
        fetchCategories() // Refresh the list
      } else {
        const errorData = await response.json()
        showMessage(`Failed to create category "${formData.name}": ${errorData.message || 'Unknown error'}`, 'error')
      }
    } catch (error) {
      showMessage(`Error creating category "${formData.name}": ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // Update category
  const updateCategory = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const token = localStorage.getItem('access_token')
      const formDataToSend = new FormData()
      formDataToSend.append('name', formData.name)
      formDataToSend.append('slug', formData.slug)
      formDataToSend.append('description', formData.description)
      if (formData.image) {
        formDataToSend.append('image', formData.image)
      }

      const response = await fetch(`http://127.0.0.1:8000/api/products/category/${editingCategory.slug}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataToSend
      })

      if (response.ok) {
        showMessage(`Category "${formData.name}" updated successfully!`, 'success')
        setFormData({ name: '', slug: '', description: '', image: null })
        setEditingCategory(null)
        fetchCategories() // Refresh the list
      } else {
        const errorData = await response.json()
        showMessage(`Failed to update category "${formData.name}": ${errorData.message || 'Unknown error'}`, 'error')
      }
    } catch (error) {
      showMessage(`Error updating category "${formData.name}": ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // Delete category
  const deleteCategory = async () => {
    if (!categoryToDelete) return

    setLoading(true)
    setError('')
    
    try {
      const token = localStorage.getItem('access_token')
      console.log('Deleting category:', categoryToDelete)
      console.log('Using slug for deletion:', categoryToDelete.slug)
      
      const response = await fetch(`http://127.0.0.1:8000/api/products/category/${categoryToDelete.slug}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      console.log('Delete response status:', response.status)
      
      if (response.ok) {
        showMessage(`Category "${categoryToDelete.name}" deleted successfully!`, 'success')
        setShowDeleteModal(false)
        setCategoryToDelete(null)
        fetchCategories() // Refresh the list
      } else {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }))
        console.error('Delete error:', errorData)
        showMessage(`Failed to delete category "${categoryToDelete.name}": ${errorData.message || 'Unknown error'}`, 'error')
      }
    } catch (error) {
      console.error('Delete error:', error)
      showMessage(`Error deleting category "${categoryToDelete.name}": ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // Show delete confirmation modal
  const showDeleteConfirmation = (category) => {
    setCategoryToDelete(category)
    setShowDeleteModal(true)
  }

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, files } = e.target
    if (name === 'image') {
      setFormData(prev => ({ ...prev, [name]: files[0] }))
    } else {
      setFormData(prev => ({ ...prev, [name]: value }))
    }
  }

  // Start editing category
  const startEdit = (category) => {
    setEditingCategory(category)
    setFormData({
      name: category.name,
      slug: category.slug,
      description: category.description || '',
      image: null
    })
    setShowCreateForm(true)
  }

  // Cancel form
  const cancelForm = () => {
    setShowCreateForm(false)
    setEditingCategory(null)
    setFormData({ name: '', slug: '', description: '', image: null })
    clearMessages()
  }

  // Cancel delete modal
  const cancelDelete = () => {
    setShowDeleteModal(false)
    setCategoryToDelete(null)
  }

  // Auto-generate slug from name
  const generateSlug = (name) => {
    return name.toLowerCase()
      .replace(/[^a-z0-9 -]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim('-')
  }

  // Handle name change and auto-generate slug
  const handleNameChange = (e) => {
    const name = e.target.value
    setFormData(prev => ({
      ...prev,
      name: name,
      slug: generateSlug(name)
    }))
  }

  // Load categories on component mount
  useEffect(() => {
    fetchCategories()
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
            }}>Category Management</h1>
            <p style={{ 
              fontSize: '16px', 
              color: '#637381',
              margin: '0'
            }}>Create, edit, and manage product categories</p>
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
              background: '#f59e0b',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = '#d97706'
            }}
            onMouseLeave={(e) => {
              e.target.style.background = '#f59e0b'
            }}
          >
            <span style={{ marginRight: '8px' }}>➕</span>
            Add Category
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
              {editingCategory ? 'Edit Category' : 'Create New Category'}
            </h2>
            
            <form onSubmit={editingCategory ? updateCategory : createCategory}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                <div>
                  <label style={{ 
                    display: 'block', 
                    fontSize: '14px', 
                    fontWeight: '500', 
                    color: '#212b36',
                    marginBottom: '8px'
                  }}>
                    Category Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleNameChange}
                    required
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '1px solid #e1e3e5',
                      borderRadius: '8px',
                      fontSize: '14px',
                      color: '#212b36'
                    }}
                    placeholder="Enter category name"
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
                    Slug *
                  </label>
                  <input
                    type="text"
                    name="slug"
                    value={formData.slug}
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
                    placeholder="category-slug"
                  />
                </div>
              </div>

              <div style={{ marginBottom: '24px' }}>
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
                  placeholder="Enter category description"
                />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label style={{ 
                  display: 'block', 
                  fontSize: '14px', 
                  fontWeight: '500', 
                  color: '#212b36',
                  marginBottom: '8px'
                }}>
                  Category Image
                </label>
                <input
                  type="file"
                  name="image"
                  onChange={handleInputChange}
                  accept="image/*"
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
                    background: loading ? '#9ca3af' : '#f59e0b',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  {loading ? 'Saving...' : (editingCategory ? 'Update Category' : 'Create Category')}
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

        {/* Categories List */}
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
            }}>Categories ({categories.length})</h3>
          </div>

          {loading ? (
            <div style={{ 
              padding: '48px', 
              textAlign: 'center',
              color: '#637381'
            }}>
              Loading categories...
            </div>
          ) : categories.length === 0 ? (
            <div style={{ 
              padding: '48px', 
              textAlign: 'center',
              color: '#637381'
            }}>
              No categories found. Create your first category!
            </div>
          ) : (
            <div style={{ padding: '24px' }}>
              <div style={{ display: 'grid', gap: '16px' }}>
                {categories.map((category) => (
                  <div
                    key={category.id}
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
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginRight: '16px'
                      }}>
                        <span style={{ color: 'white', fontSize: '20px' }}>📂</span>
                      </div>
                      <div>
                        <h4 style={{ 
                          margin: '0 0 4px 0', 
                          fontSize: '16px', 
                          fontWeight: '600', 
                          color: '#212b36' 
                        }}>
                          {category.name}
                        </h4>
                        <p style={{ 
                          margin: '0 0 4px 0', 
                          fontSize: '14px', 
                          color: '#637381' 
                        }}>
                          Slug: {category.slug}
                        </p>
                        {category.description && (
                          <p style={{ 
                            margin: '0', 
                            fontSize: '12px', 
                            color: '#9ca3af' 
                          }}>
                            {category.description}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => startEdit(category)}
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
                        onClick={() => showDeleteConfirmation(category)}
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
                Delete Category
              </h3>
              
              <p style={{
                fontSize: '16px',
                color: '#637381',
                margin: '0 0 24px 0',
                textAlign: 'center',
                lineHeight: '1.5'
              }}>
                Are you sure you want to delete <strong>"{categoryToDelete?.name}"</strong>? 
                This action cannot be undone and will also delete all associated subcategories.
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
                  onClick={deleteCategory}
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
                  {loading ? 'Deleting...' : 'Delete Category'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
})

export default CategoryManagement
