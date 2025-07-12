import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Badge } from '../ui/badge'
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog'
import { 
  Plus, 
  Search, 
  Filter, 
  Download, 
  Edit, 
  Trash2, 
  Eye,
  CheckCircle,
  Clock,
  AlertTriangle,
  XCircle
} from 'lucide-react'
import { MockDataService } from '../../services/api'

const InvoiceManagement = () => {
  const { user, hasRole } = useAuth()
  const [invoices, setInvoices] = useState([])
  const [filteredInvoices, setFilteredInvoices] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [selectedInvoice, setSelectedInvoice] = useState(null)
  const [showViewDialog, setShowViewDialog] = useState(false)

  useEffect(() => {
    loadInvoices()
  }, [])

  useEffect(() => {
    filterInvoices()
  }, [invoices, searchTerm, statusFilter, typeFilter])

  const loadInvoices = async () => {
    try {
      setLoading(true)
      // For demo purposes, use mock data
      const mockData = MockDataService.generateMockInvoices(50)
      setInvoices(mockData)
    } catch (error) {
      console.error('Failed to load invoices:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterInvoices = () => {
    let filtered = invoices

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(invoice => 
        invoice.reference_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        invoice.description.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(invoice => invoice.status === statusFilter)
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(invoice => invoice.invoice_type === typeFilter)
    }

    setFilteredInvoices(filtered)
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { label: 'Pending', variant: 'secondary', icon: Clock },
      paid: { label: 'Paid', variant: 'default', icon: CheckCircle },
      overdue: { label: 'Overdue', variant: 'destructive', icon: AlertTriangle },
      canceled: { label: 'Canceled', variant: 'outline', icon: XCircle }
    }

    const config = statusConfig[status] || statusConfig.pending
    const Icon = config.icon

    return (
      <Badge variant={config.variant} className="flex items-center space-x-1">
        <Icon className="h-3 w-3" />
        <span>{config.label}</span>
      </Badge>
    )
  }

  const getTypeBadge = (type) => {
    const typeLabels = {
      monthly_fee: 'Monthly Fee',
      utility_bill: 'Utility Bill',
      maintenance_fee: 'Maintenance',
      penalty: 'Penalty',
      other: 'Other'
    }

    return (
      <Badge variant="outline">
        {typeLabels[type] || type}
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

  const handleCreateInvoice = () => {
    // This would typically call the API
    console.log('Creating new invoice...')
    setShowCreateDialog(false)
    // Reload invoices
    loadInvoices()
  }

  const handleViewInvoice = (invoice) => {
    setSelectedInvoice(invoice)
    setShowViewDialog(true)
  }

  const handleUpdateStatus = (invoiceId, newStatus) => {
    // This would typically call the API
    setInvoices(prev => prev.map(inv => 
      inv.id === invoiceId ? { ...inv, status: newStatus } : inv
    ))
  }

  const handleDeleteInvoice = (invoiceId) => {
    // This would typically call the API
    setInvoices(prev => prev.filter(inv => inv.id !== invoiceId))
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
          <h2 className="text-2xl font-bold">Invoice Management</h2>
          <p className="text-muted-foreground">
            Create, manage, and track invoices
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Invoice
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search invoices..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="paid">Paid</SelectItem>
                  <SelectItem value="overdue">Overdue</SelectItem>
                  <SelectItem value="canceled">Canceled</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="type">Type</Label>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="monthly_fee">Monthly Fee</SelectItem>
                  <SelectItem value="utility_bill">Utility Bill</SelectItem>
                  <SelectItem value="maintenance_fee">Maintenance</SelectItem>
                  <SelectItem value="penalty">Penalty</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button variant="outline" className="w-full">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Invoice Table */}
      <Card>
        <CardHeader>
          <CardTitle>Invoices ({filteredInvoices.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Reference</TableHead>
                <TableHead>Property</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredInvoices.map((invoice) => (
                <TableRow key={invoice.id}>
                  <TableCell className="font-medium">
                    {invoice.reference_number}
                  </TableCell>
                  <TableCell>Property #{invoice.property_id}</TableCell>
                  <TableCell>{getTypeBadge(invoice.invoice_type)}</TableCell>
                  <TableCell className="font-medium">
                    {formatCurrency(invoice.amount)}
                  </TableCell>
                  <TableCell>{formatDate(invoice.due_date)}</TableCell>
                  <TableCell>{getStatusBadge(invoice.status)}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewInvoice(invoice)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteInvoice(invoice.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Create Invoice Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Create New Invoice</DialogTitle>
            <DialogDescription>
              Create a new invoice for a property.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="property" className="text-right">
                Property
              </Label>
              <Select>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select property" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Property A-101</SelectItem>
                  <SelectItem value="2">Property A-102</SelectItem>
                  <SelectItem value="3">Property B-201</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="type" className="text-right">
                Type
              </Label>
              <Select>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="monthly_fee">Monthly Fee</SelectItem>
                  <SelectItem value="utility_bill">Utility Bill</SelectItem>
                  <SelectItem value="maintenance_fee">Maintenance</SelectItem>
                  <SelectItem value="penalty">Penalty</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="amount" className="text-right">
                Amount
              </Label>
              <Input
                id="amount"
                type="number"
                placeholder="0.00"
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="due_date" className="text-right">
                Due Date
              </Label>
              <Input
                id="due_date"
                type="date"
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">
                Description
              </Label>
              <Input
                id="description"
                placeholder="Invoice description"
                className="col-span-3"
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" onClick={handleCreateInvoice}>
              Create Invoice
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Invoice Dialog */}
      <Dialog open={showViewDialog} onOpenChange={setShowViewDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Invoice Details</DialogTitle>
            <DialogDescription>
              {selectedInvoice?.reference_number}
            </DialogDescription>
          </DialogHeader>
          {selectedInvoice && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Property</Label>
                  <p>Property #{selectedInvoice.property_id}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Type</Label>
                  <p>{getTypeBadge(selectedInvoice.invoice_type)}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Amount</Label>
                  <p className="text-lg font-bold">{formatCurrency(selectedInvoice.amount)}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Status</Label>
                  <p>{getStatusBadge(selectedInvoice.status)}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Due Date</Label>
                  <p>{formatDate(selectedInvoice.due_date)}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Issued Date</Label>
                  <p>{formatDate(selectedInvoice.issued_at)}</p>
                </div>
              </div>
              <div>
                <Label className="text-sm font-medium">Description</Label>
                <p>{selectedInvoice.description}</p>
              </div>
              {selectedInvoice.status === 'pending' && (
                <div className="flex space-x-2">
                  <Button 
                    size="sm" 
                    onClick={() => handleUpdateStatus(selectedInvoice.id, 'paid')}
                  >
                    Mark as Paid
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleUpdateStatus(selectedInvoice.id, 'canceled')}
                  >
                    Cancel
                  </Button>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default InvoiceManagement

