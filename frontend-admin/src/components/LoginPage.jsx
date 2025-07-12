import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Building2, Shield, Calculator } from 'lucide-react'

const LoginPage = () => {
  const { isAuthenticated, loginDemo } = useAuth()
  const [loading, setLoading] = useState(false)

  if (isAuthenticated()) {
    return <Navigate to="/dashboard" replace />
  }

  const handleDemoLogin = async (role) => {
    setLoading(true)
    try {
      await loginDemo(role)
    } catch (error) {
      console.error('Login failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-primary rounded-full p-3">
              <Building2 className="h-8 w-8 text-primary-foreground" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Smart Village</h1>
          <p className="text-gray-600 mt-2">Admin Dashboard - ERP Accounting System</p>
        </div>

        {/* Demo Login Cards */}
        <div className="space-y-4">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-red-600" />
                <CardTitle className="text-lg">Super Administrator</CardTitle>
              </div>
              <CardDescription>
                Full system access across all villages
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => handleDemoLogin('super_admin')}
                disabled={loading}
                className="w-full bg-red-600 hover:bg-red-700"
              >
                {loading ? 'Logging in...' : 'Login as Super Admin'}
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2">
                <Building2 className="h-5 w-5 text-blue-600" />
                <CardTitle className="text-lg">Village Administrator</CardTitle>
              </div>
              <CardDescription>
                Manage village operations and accounting
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => handleDemoLogin('village_admin')}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {loading ? 'Logging in...' : 'Login as Village Admin'}
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2">
                <Calculator className="h-5 w-5 text-green-600" />
                <CardTitle className="text-lg">Accounting Staff</CardTitle>
              </div>
              <CardDescription>
                Handle financial operations and reporting
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => handleDemoLogin('village_accounting')}
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                {loading ? 'Logging in...' : 'Login as Accounting Staff'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Regular Login Form */}
        <Card>
          <CardHeader>
            <CardTitle>Regular Login</CardTitle>
            <CardDescription>
              Enter your credentials to access the system
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="admin@smartvillage.com"
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input 
                id="password" 
                type="password" 
                placeholder="Enter your password"
                disabled={loading}
              />
            </div>
            <Button 
              className="w-full" 
              disabled={loading}
            >
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>Smart Village Management System v2.0</p>
          <p>ERP Accounting Module</p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage

