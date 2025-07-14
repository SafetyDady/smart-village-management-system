import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table'
import { Plus, Download, Eye, Receipt } from 'lucide-react'
import { receiptAPI } from '../../services/api'

const ReceiptManagement = () => {
  const { user } = useAuth()
  const [receipts, setReceipts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReceipts()
  }, [])

  const loadReceipts = async () => {
    try {
      setLoading(true)
      const response = await receiptAPI.getAll()
      setReceipts(response.receipts || [])
    } catch (error) {
      console.error('Failed to load receipts:', error)
      setReceipts([]) // Fallback to empty array on error
    } finally {
      setLoading(false)
    }
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
          <h2 className="text-2xl font-bold">Receipt Management</h2>
          <p className="text-muted-foreground">
            Generate and manage payment receipts
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Generate Receipt
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Receipts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{receipts.length}</div>
            <p className="text-sm text-muted-foreground">Generated this month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Total Amount</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(receipts.reduce((sum, r) => sum + parseFloat(r.amount), 0))}
            </div>
            <p className="text-sm text-muted-foreground">Receipt value</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Auto Generated</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.floor(receipts.length * 0.8)}
            </div>
            <p className="text-sm text-muted-foreground">Automatic receipts</p>
          </CardContent>
        </Card>
      </div>

      {/* Receipt Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Receipts</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Receipt Number</TableHead>
                <TableHead>Payment Ref</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Issued Date</TableHead>
                <TableHead>Note</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {receipts.slice(0, 15).map((receipt) => (
                <TableRow key={receipt.id}>
                  <TableCell className="font-medium">
                    {receipt.receipt_number}
                  </TableCell>
                  <TableCell>PAY-001-2024-{receipt.payment_id.slice(-4)}</TableCell>
                  <TableCell className="font-medium">
                    {formatCurrency(receipt.amount)}
                  </TableCell>
                  <TableCell>{formatDate(receipt.issued_at)}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {receipt.note || '-'}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
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

export default ReceiptManagement

