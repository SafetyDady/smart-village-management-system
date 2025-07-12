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
      // For demo purposes, we'll simulate login
      // In production, this would call the actual API
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        throw new Error('Login failed')
      }

      const data = await response.json()
      
      // Store auth data
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

  const loginDemo = (role) => {
    // Demo login for development
    const demoUsers = {
      super_admin: {
        id: 1,
        email: 'admin@smartvillage.com',
        role: 'super_admin',
        first_name: 'Super',
        last_name: 'Admin',
        village_id: null
      },
      village_admin: {
        id: 2,
        email: 'village@smartvillage.com',
        role: 'village_admin',
        first_name: 'Village',
        last_name: 'Admin',
        village_id: 1
      },
      village_accounting: {
        id: 3,
        email: 'accounting@smartvillage.com',
        role: 'village_accounting',
        first_name: 'Accounting',
        last_name: 'Admin',
        village_id: 1
      }
    }

    const demoUser = demoUsers[role]
    const demoToken = `demo_token_${role}_${Date.now()}`

    localStorage.setItem('token', demoToken)
    localStorage.setItem('user', JSON.stringify(demoUser))
    
    setToken(demoToken)
    setUser(demoUser)
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

