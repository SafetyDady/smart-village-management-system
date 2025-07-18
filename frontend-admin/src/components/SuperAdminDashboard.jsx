import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { dashboardAPI } from '../services/api'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { 
  Building2, 
  Users, 
  Calculator, 
  TrendingUp, 
  DollarSign, 
  FileText,
  Settings,
  LogOut,
  Menu,
  X,
  Home,
  Receipt,
  CreditCard,
  PieChart
} from 'lucide-react'

const SuperAdminDashboard = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [dashboardData, setDashboardData] = useState(null)
  const [recentActivities, setRecentActivities] = useState([])
  const [loading, setLoading] = useState(true)
  const [activitiesLoading, setActivitiesLoading] = useState(true)
  const [error, setError] = useState(null)

  // Load dashboard data
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true)
        const data = await dashboardAPI.getSummary()
        setDashboardData(data)
        setError(null)
      } catch (err) {
        console.error('Dashboard Error:', err)
        setError(err.message)
        // Fallback to mock data if API fails
        setDashboardData({
          total_villages: 12,
          total_revenue: 2450000,
          active_users: 1247,
          pending_invoices: 15,
          growth: {
            villages: '+2 this month',
            revenue: '+15% from last month',
            users: '+8% from last month',
            invoices: '-12% from last month'
          }
        })
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  // Load recent activities
  useEffect(() => {
    const loadRecentActivities = async () => {
      try {
        setActivitiesLoading(true)
        const data = await dashboardAPI.getRecentActivities(4)
        setRecentActivities(data.activities || [])
      } catch (err) {
        console.error('Recent Activities Error:', err)
        // Fallback to mock data if API fails
        setRecentActivities([
          { 
            type: 'invoice',
            message: 'New invoice created for Green Valley Village', 
            time: '2 minutes ago', 
            icon: 'receipt',
            amount: 5000
          },
          { 
            type: 'payment',
            message: 'Payment received from Sunset Hills Community', 
            time: '15 minutes ago', 
            icon: 'credit-card',
            amount: 3500
          },
          { 
            type: 'user',
            message: 'New village admin registered', 
            time: '1 hour ago', 
            icon: 'users',
            amount: null
          },
          { 
            type: 'property',
            message: 'Mountain View Estate added new property', 
            time: '2 hours ago', 
            icon: 'building',
            amount: null
          },
        ])
      } finally {
        setActivitiesLoading(false)
      }
    }

    loadRecentActivities()
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard', active: true },
    { icon: Building2, label: 'Villages', path: '/villages' },
    { icon: Users, label: 'Users', path: '/users' },
    { icon: Calculator, label: 'Accounting', path: '/accounting' },
    { icon: PieChart, label: 'Reports', path: '/reports' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ]

  // Create stats from API data
  const stats = dashboardData ? [
    {
      title: 'Total Villages',
      value: dashboardData.total_villages.toString(),
      change: dashboardData.growth?.villages || '+0 this month',
      icon: Building2,
      color: 'text-blue-600'
    },
    {
      title: 'Total Revenue',
      value: `฿${dashboardData.total_revenue.toLocaleString()}`,
      change: dashboardData.growth?.revenue || '+0% from last month',
      icon: DollarSign,
      color: 'text-green-600'
    },
    {
      title: 'Active Users',
      value: dashboardData.active_users.toLocaleString(),
      change: dashboardData.growth?.users || '+0% from last month',
      icon: Users,
      color: 'text-purple-600'
    },
    {
      title: 'Pending Invoices',
      value: dashboardData.pending_invoices.toString(),
      change: dashboardData.growth?.invoices || '+0% from last month',
      icon: FileText,
      color: 'text-orange-600'
    }
  ] : []

  // Map activity types to icons and colors
  const getActivityIcon = (type, iconName) => {
    const iconMap = {
      'receipt': Receipt,
      'credit-card': CreditCard,
      'users': Users,
      'building': Building2,
      'invoice': Receipt,
      'payment': CreditCard,
      'user': Users,
      'property': Building2
    }
    return iconMap[iconName] || iconMap[type] || Receipt
  }

  const getActivityColor = (type) => {
    const colorMap = {
      'invoice': 'text-green-600',
      'payment': 'text-blue-600',
      'user': 'text-purple-600',
      'property': 'text-orange-600'
    }
    return colorMap[type] || 'text-gray-600'
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white border-b border-border h-16 fixed top-0 left-0 right-0 z-50">
        <div className="flex items-center justify-between h-full px-4">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            <div className="flex items-center space-x-2">
              <Building2 className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold">Smart Village Admin</h1>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium">{user?.first_name} {user?.last_name}</p>
              <p className="text-xs text-muted-foreground">Super Administrator</p>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <aside className={`fixed top-16 left-0 z-40 w-64 h-[calc(100vh-4rem)] bg-white border-r border-border transform transition-transform lg:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <nav className="p-4 space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                item.active 
                  ? 'bg-primary text-primary-foreground' 
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              }`}
            >
              <item.icon className="h-5 w-5" />
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className={`pt-16 transition-all duration-300 ${sidebarOpen ? 'lg:ml-64' : 'lg:ml-64'}`}>
        <div className="p-6">
          {/* Welcome Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-foreground">Welcome back, {user?.first_name}!</h2>
            <p className="text-muted-foreground mt-2">Here's what's happening across all villages today.</p>
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600">Failed to load dashboard data: {error}</p>
                <p className="text-sm text-red-500 mt-1">Showing fallback data. Please check your connection.</p>
              </div>
            )}
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {loading ? (
              // Loading skeleton
              Array.from({ length: 4 }).map((_, index) => (
                <Card key={index}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <div className="h-4 bg-gray-200 rounded w-24 animate-pulse"></div>
                    <div className="h-4 w-4 bg-gray-200 rounded animate-pulse"></div>
                  </CardHeader>
                  <CardContent>
                    <div className="h-8 bg-gray-200 rounded w-16 mb-2 animate-pulse"></div>
                    <div className="h-3 bg-gray-200 rounded w-20 animate-pulse"></div>
                  </CardContent>
                </Card>
              ))
            ) : (
              stats.map((stat, index) => (
                <Card key={index}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                    <stat.icon className={`h-4 w-4 ${stat.color}`} />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stat.value}</div>
                    <p className="text-xs text-muted-foreground">{stat.change}</p>
                  </CardContent>
                </Card>
              ))
            )}
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/accounting')}>
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <Calculator className="h-6 w-6 text-green-600" />
                  <CardTitle>ERP Accounting</CardTitle>
                </div>
                <CardDescription>
                  Manage invoices, payments, and receipts across all villages
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-2xl font-bold">
                      {loading ? '...' : dashboardData ? `฿${(dashboardData.total_revenue / 1000000).toFixed(1)}M` : '฿0'}
                    </p>
                    <p className="text-sm text-muted-foreground">Total Revenue</p>
                  </div>
                  <Button>Access</Button>
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <Building2 className="h-6 w-6 text-blue-600" />
                  <CardTitle>Village Management</CardTitle>
                </div>
                <CardDescription>
                  Oversee all village operations and administration
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-2xl font-bold">
                      {loading ? '...' : dashboardData ? dashboardData.total_villages : '0'}
                    </p>
                    <p className="text-sm text-muted-foreground">Active Villages</p>
                  </div>
                  <Button variant="outline">Manage</Button>
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <Users className="h-6 w-6 text-purple-600" />
                  <CardTitle>User Management</CardTitle>
                </div>
                <CardDescription>
                  Control user access and permissions system-wide
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-2xl font-bold">
                      {loading ? '...' : dashboardData ? dashboardData.active_users.toLocaleString() : '0'}
                    </p>
                    <p className="text-sm text-muted-foreground">Total Users</p>
                  </div>
                  <Button variant="outline">Manage</Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest system activities across all villages</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activitiesLoading ? (
                  // Loading skeleton for activities
                  Array.from({ length: 4 }).map((_, index) => (
                    <div key={index} className="flex items-center space-x-3 p-3 rounded-lg">
                      <div className="h-5 w-5 bg-gray-200 rounded animate-pulse"></div>
                      <div className="flex-1">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2 animate-pulse"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/4 animate-pulse"></div>
                      </div>
                    </div>
                  ))
                ) : recentActivities.length > 0 ? (
                  recentActivities.map((activity, index) => {
                    const ActivityIcon = getActivityIcon(activity.type, activity.icon)
                    const color = getActivityColor(activity.type)
                    
                    return (
                      <div key={index} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-accent">
                        <ActivityIcon className={`h-5 w-5 ${color}`} />
                        <div className="flex-1">
                          <p className="text-sm font-medium">{activity.message}</p>
                          <div className="flex items-center space-x-2">
                            <p className="text-xs text-muted-foreground">{activity.time || activity.timestamp}</p>
                            {activity.amount && (
                              <span className="text-xs text-green-600 font-medium">
                                ฿{activity.amount.toLocaleString()}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No recent activities found</p>
                    <p className="text-sm">Activities will appear here as they happen</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

export default SuperAdminDashboard

