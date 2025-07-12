import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { 
  DollarSign, 
  FileText, 
  CreditCard, 
  Receipt,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { MockDataService } from '../../services/api'

const AccountingDashboard = () => {
  const { user, hasRole } = useAuth()
  const [stats, setStats] = useState({
    totalInvoices: 0,
    totalAmount: 0,
    paidAmount: 0,
    pendingAmount: 0,
    overdueAmount: 0,
    totalPayments: 0,
    totalReceipts: 0
  })
  const [chartData, setChartData] = useState([])
  const [statusData, setStatusData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // For demo purposes, use mock data
      const mockInvoices = MockDataService.generateMockInvoices(50)
      const mockPayments = MockDataService.generateMockPayments(35)
      const mockReceipts = MockDataService.generateMockReceipts(35)

      // Calculate stats
      const totalAmount = mockInvoices.reduce((sum, inv) => sum + parseFloat(inv.amount), 0)
      const paidAmount = mockInvoices
        .filter(inv => inv.status === 'paid')
        .reduce((sum, inv) => sum + parseFloat(inv.amount), 0)
      const pendingAmount = mockInvoices
        .filter(inv => inv.status === 'pending')
        .reduce((sum, inv) => sum + parseFloat(inv.amount), 0)
      const overdueAmount = mockInvoices
        .filter(inv => inv.status === 'overdue')
        .reduce((sum, inv) => sum + parseFloat(inv.amount), 0)

      setStats({
        totalInvoices: mockInvoices.length,
        totalAmount,
        paidAmount,
        pendingAmount,
        overdueAmount,
        totalPayments: mockPayments.length,
        totalReceipts: mockReceipts.length
      })

      // Prepare chart data (monthly revenue)
      const monthlyData = []
      for (let i = 5; i >= 0; i--) {
        const date = new Date()
        date.setMonth(date.getMonth() - i)
        const monthName = date.toLocaleDateString('en-US', { month: 'short' })
        
        monthlyData.push({
          month: monthName,
          revenue: Math.floor(Math.random() * 200000) + 100000,
          invoices: Math.floor(Math.random() * 50) + 20
        })
      }
      setChartData(monthlyData)

      // Prepare status data for pie chart
      const statusCounts = {
        paid: mockInvoices.filter(inv => inv.status === 'paid').length,
        pending: mockInvoices.filter(inv => inv.status === 'pending').length,
        overdue: mockInvoices.filter(inv => inv.status === 'overdue').length,
        canceled: mockInvoices.filter(inv => inv.status === 'canceled').length
      }

      setStatusData([
        { name: 'Paid', value: statusCounts.paid, color: '#22c55e' },
        { name: 'Pending', value: statusCounts.pending, color: '#f59e0b' },
        { name: 'Overdue', value: statusCounts.overdue, color: '#ef4444' },
        { name: 'Canceled', value: statusCounts.canceled, color: '#6b7280' }
      ])

    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('th-TH', {
      style: 'currency',
      currency: 'THB'
    }).format(amount)
  }

  const statCards = [
    {
      title: 'Total Revenue',
      value: formatCurrency(stats.totalAmount),
      change: '+12% from last month',
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Paid Amount',
      value: formatCurrency(stats.paidAmount),
      change: `${stats.totalInvoices} invoices`,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Pending Amount',
      value: formatCurrency(stats.pendingAmount),
      change: 'Awaiting payment',
      icon: Clock,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50'
    },
    {
      title: 'Overdue Amount',
      value: formatCurrency(stats.overdueAmount),
      change: 'Requires attention',
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">Accounting Dashboard</h2>
        <p className="text-muted-foreground">
          {hasRole('super_admin') 
            ? 'System-wide financial overview and analytics'
            : 'Village financial overview and analytics'
          }
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.change}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Monthly Revenue Trend</CardTitle>
            <CardDescription>Revenue and invoice count over the last 6 months</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'revenue' ? formatCurrency(value) : value,
                    name === 'revenue' ? 'Revenue' : 'Invoices'
                  ]}
                />
                <Bar dataKey="revenue" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Invoice Status Distribution</CardTitle>
            <CardDescription>Current status breakdown of all invoices</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <FileText className="h-6 w-6 text-blue-600" />
              <CardTitle>Manage Invoices</CardTitle>
            </div>
            <CardDescription>Create, edit, and track invoices</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <div>
                <p className="text-2xl font-bold">{stats.totalInvoices}</p>
                <p className="text-sm text-muted-foreground">Total Invoices</p>
              </div>
              <Button>View All</Button>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <CreditCard className="h-6 w-6 text-green-600" />
              <CardTitle>Process Payments</CardTitle>
            </div>
            <CardDescription>Record and manage payments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <div>
                <p className="text-2xl font-bold">{stats.totalPayments}</p>
                <p className="text-sm text-muted-foreground">Total Payments</p>
              </div>
              <Button>View All</Button>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Receipt className="h-6 w-6 text-purple-600" />
              <CardTitle>Generate Receipts</CardTitle>
            </div>
            <CardDescription>Create and manage receipts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <div>
                <p className="text-2xl font-bold">{stats.totalReceipts}</p>
                <p className="text-sm text-muted-foreground">Total Receipts</p>
              </div>
              <Button>View All</Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest accounting activities</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { icon: FileText, text: 'Invoice #INV-001-2024-0156 created for ฿5,000', time: '5 minutes ago', color: 'text-blue-600' },
              { icon: CreditCard, text: 'Payment of ฿3,500 received via bank transfer', time: '15 minutes ago', color: 'text-green-600' },
              { icon: Receipt, text: 'Receipt #RCP-001-2024-0089 generated', time: '1 hour ago', color: 'text-purple-600' },
              { icon: AlertTriangle, text: 'Invoice #INV-001-2024-0145 is now overdue', time: '2 hours ago', color: 'text-red-600' },
              { icon: CheckCircle, text: 'Invoice #INV-001-2024-0144 marked as paid', time: '3 hours ago', color: 'text-green-600' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-accent">
                <activity.icon className={`h-5 w-5 ${activity.color}`} />
                <div className="flex-1">
                  <p className="text-sm font-medium">{activity.text}</p>
                  <p className="text-xs text-muted-foreground">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default AccountingDashboard

