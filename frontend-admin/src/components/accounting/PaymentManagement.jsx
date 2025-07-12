import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table'
import { Plus, CreditCard, Banknote, Smartphone, QrCode } from 'lucide-react'
import { MockDataService } from '../../services/api'

const PaymentManagement = () => {
  const { user } = useAuth()
  const [payments, setPayments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadPayments()
  }, [])

  const loadPayments = async () => {
    try {
      setLoading(true)
      const mockData = MockDataService.generateMockPayments(30)
      setPayments(mockData)
    } catch (error) {
      console.error('Failed to load payments:', error)
    } finally {
      setLoading(false)
    }
  }

  const getMethodIcon = (method) => {
    const icons = {
      bank_transfer: Banknote,
      cash: Banknote,
      qr_code: QrCode,
      credit_card: CreditCard,
      mobile_banking: Smartphone
    }
    const Icon = icons[method] || CreditCard
    return <Icon className="h-4 w-4" />
  }

  const getMethodBadge = (method) => {
    const labels = {
      bank_transfer: 'Bank Transfer',
      cash: 'Cash',
      qr_code: 'QR Code',
      credit_card: 'Credit Card',
      mobile_banking: 'Mobile Banking'
    }

    return (
      <Badge variant="outline" className="flex items-center space-x-1">
        {getMethodIcon(method)}
        <span>{labels[method] || method}</span>
      </Badge>
    )
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('th-TH', {
      style: 'currency',
      currency: 'THB'
    }).format(amount)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('th-TH')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Payment Management</h2>
          <p className="text-muted-foreground">
            Record and track payments from residents
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Record Payment
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Payments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{payments.length}</div>
            <p className="text-sm text-muted-foreground">This month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Total Amount</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(payments.reduce((sum, p) => sum + parseFloat(p.amount), 0))}
            </div>
            <p className="text-sm text-muted-foreground">Received this month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Average Payment</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(payments.reduce((sum, p) => sum + parseFloat(p.amount), 0) / payments.length)}
            </div>
            <p className="text-sm text-muted-foreground">Per transaction</p>
          </CardContent>
        </Card>
      </div>

      {/* Payment Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Payments</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Reference</TableHead>
                <TableHead>Property</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Method</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Bank Ref</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {payments.slice(0, 10).map((payment) => (
                <TableRow key={payment.id}>
                  <TableCell className="font-medium">
                    {payment.reference_number}
                  </TableCell>
                  <TableCell>Property #{payment.property_id}</TableCell>
                  <TableCell className="font-medium">
                    {formatCurrency(payment.amount)}
                  </TableCell>
                  <TableCell>{getMethodBadge(payment.method)}</TableCell>
                  <TableCell>{formatDate(payment.payment_date)}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {payment.bank_reference || '-'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

export default PaymentManagement

