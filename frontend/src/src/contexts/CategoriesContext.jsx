import React, { createContext, useContext, useState, useEffect } from 'react'
import apiService from '../services/api'

const CategoriesContext = createContext()

export const useCategories = () => {
  const context = useContext(CategoriesContext)
  if (!context) {
    throw new Error('useCategories must be used within a CategoriesProvider')
  }
  return context
}

export const CategoriesProvider = ({ children }) => {
  const [categories, setCategories] = useState([])
  const [subcategories, setSubcategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Load categories
  const loadCategories = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiService.getCategories()
      setCategories(data.results || data)
    } catch (err) {
      console.error('Failed to load categories:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Load subcategories
  const loadSubCategories = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiService.getSubCategories()
      setSubcategories(data)
    } catch (err) {
      console.error('Failed to load subcategories:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Load subcategories by category
  const loadSubCategoriesByCategory = async (categorySlug) => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiService.getSubCategoriesByCategory(categorySlug)
      return data.results || data
    } catch (err) {
      console.error('Failed to load subcategories by category:', err)
      setError(err.message)
      return []
    } finally {
      setLoading(false)
    }
  }

  // Get subcategories for a specific category
  const getSubCategoriesForCategory = (categorySlug) => {
    if (!subcategories || subcategories.length === 0) {
      return []
    }
    return subcategories.filter(sub => sub.category_slug === categorySlug)
  }

  // Load all data on mount
  useEffect(() => {
    loadCategories()
    loadSubCategories()
  }, [])


  const value = {
    categories,
    subcategories,
    loading,
    error,
    loadCategories,
    loadSubCategories,
    loadSubCategoriesByCategory,
    getSubCategoriesForCategory,
  }

  return (
    <CategoriesContext.Provider value={value}>
      {children}
    </CategoriesContext.Provider>
  )
}
