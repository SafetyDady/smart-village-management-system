import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './App.css'

// Components
import LoginPage from './components/LoginPage'
import SuperAdminDashboard from './components/SuperAdminDashboard'
import VillageAdminDashboard from './components/VillageAdminDashboard'
import AccountingModule from './components/AccountingModule'
import ProtectedRoute from './components/ProtectedRoute'

// Context
import { AuthProvider } from './contexts/AuthContext'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-background">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Protected Routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <Navigate to="/dashboard" replace />
              </ProtectedRoute>
            } />
            
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <DashboardRouter />
              </ProtectedRoute>
            } />
            
            <Route path="/accounting/*" element={
              <ProtectedRoute allowedRoles={['super_admin', 'village_admin', 'village_accounting']}>
                <AccountingModule />
              </ProtectedRoute>
            } />
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

// Dashboard Router Component
function DashboardRouter() {
  const [user, setUser] = useState(null)
  
  useEffect(() => {
    // Get user from localStorage or context
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    }
  }, [])
  
  if (!user) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
    </div>
  }
  
  // Route based on user role
  switch (user.role) {
    case 'super_admin':
      return <SuperAdminDashboard />
    case 'village_admin':
    case 'village_accounting':
      return <VillageAdminDashboard />
    default:
      return <Navigate to="/login" replace />
  }
}

export default App

