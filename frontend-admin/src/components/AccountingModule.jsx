import { useState, useEffect } from 'react'
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { 
  ArrowLeft,
  FileText, 
  CreditCard, 
  Receipt,
  Plus,
  Search,
  Filter,
  Download,
  TrendingUp,
  DollarSign,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'

// Import sub-components
import InvoiceManagement from './accounting/InvoiceManagement'
import PaymentManagement from './accounting/PaymentManagement'
import ReceiptManagement from './accounting/ReceiptManagement'
import AccountingDashboard from './accounting/AccountingDashboard'

const AccountingModule = () => {
  const { user, hasRole } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    totalInvoices: 0,
    totalPayments: 0,
    totalReceipts: 0,
    pendingAmount: 0,
    paidAmount: 0,
    overdueAmount: 0
  })

  // Check if user has access to accounting module
  if (!hasRole(['super_admin', 'village_admin', 'village_accounting'])) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-16 w-16 text-destructive mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-destructive mb-2">Access Denied</h1>
          <p className="text-muted-foreground mb-4">
            You don't have permission to access the accounting module.
          </p>
          <Button onClick={() => navigate('/dashboard')}>
            Return to Dashboard
          </Button>
        </div>
      </div>
    )
  }

  const getCurrentTab = () => {
    const path = location.pathname
    if (path.includes('/invoices')) return 'invoices'
    if (path.includes('/payments')) return 'payments'
    if (path.includes('/receipts')) return 'receipts'
    return 'dashboard'
  }

  const handleTabChange = (value) => {
    switch (value) {
      case 'dashboard':
        navigate('/accounting')
        break
      case 'invoices':
        navigate('/accounting/invoices')
        break
      case 'payments':
        navigate('/accounting/payments')
        break
      case 'receipts':
        navigate('/accounting/receipts')
        break
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white border-b border-border">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate('/dashboard')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Button>
              <div>
                <h1 className="text-2xl font-bold">ERP Accounting System</h1>
                <p className="text-muted-foreground">
                  {user?.role === 'super_admin' 
                    ? 'System-wide financial management' 
                    : `Financial management for ${user?.village?.name || 'your village'}`
                  }
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Quick Invoice
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="border-b border-border">
        <div className="px-6">
          <Tabs value={getCurrentTab()} onValueChange={handleTabChange}>
            <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:grid-cols-4">
              <TabsTrigger value="dashboard" className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4" />
                <span>Dashboard</span>
              </TabsTrigger>
              <TabsTrigger value="invoices" className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>Invoices</span>
              </TabsTrigger>
              <TabsTrigger value="payments" className="flex items-center space-x-2">
                <CreditCard className="h-4 w-4" />
                <span>Payments</span>
              </TabsTrigger>
              <TabsTrigger value="receipts" className="flex items-center space-x-2">
                <Receipt className="h-4 w-4" />
                <span>Receipts</span>
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-6">
        <Routes>
          <Route path="/" element={<AccountingDashboard />} />
          <Route path="/invoices" element={<InvoiceManagement />} />
          <Route path="/payments" element={<PaymentManagement />} />
          <Route path="/receipts" element={<ReceiptManagement />} />
        </Routes>
      </main>
    </div>
  )
}

export default AccountingModule

