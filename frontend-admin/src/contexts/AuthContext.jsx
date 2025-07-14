import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing auth data on mount
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    
    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
    
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    try {
      // Call real Backend API for authentication
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Login failed')
      }

      const data = await response.json()
      
      // Store real JWT token and user data
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      setToken(data.access_token)
      setUser(data.user)
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: error.message }
    }
  }

  const loginDemo = async (role) => {
    // Use real authentication with predefined demo credentials
    const demoCredentials = {
      super_admin: {
        email: 'admin@smartvillage.com',
        password: 'admin123'
      },
      village_admin: {
        email: 'village@smartvillage.com', 
        password: 'village123'
      },
      village_accounting: {
        email: 'accounting@smartvillage.com',
        password: 'accounting123'
      }
    }

    const credentials = demoCredentials[role]
    if (!credentials) {
      console.error('Invalid demo role:', role)
      return { success: false, error: 'Invalid role' }
    }

    // Call real login function with demo credentials
    return await login(credentials.email, credentials.password)
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  const isAuthenticated = () => {
    return !!token && !!user
  }

  const hasRole = (allowedRoles) => {
    if (!user) return false
    if (Array.isArray(allowedRoles)) {
      return allowedRoles.includes(user.role)
    }
    return user.role === allowedRoles
  }

  const getAuthHeaders = () => {
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }

  const value = {
    user,
    token,
    loading,
    login,
    loginDemo,
    logout,
    isAuthenticated,
    hasRole,
    getAuthHeaders
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

