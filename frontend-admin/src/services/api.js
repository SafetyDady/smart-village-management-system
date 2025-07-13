// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  // Get auth headers
  getAuthHeaders() {
    const token = localStorage.getItem('token')
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: this.getAuthHeaders(),
      ...options
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // GET request
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `${endpoint}?${queryString}` : endpoint
    
    return this.request(url, {
      method: 'GET'
    })
  }

  // POST request
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  // PUT request
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    })
  }

  // PATCH request
  async patch(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }
}

// Invoice API
export class InvoiceAPI extends ApiService {
  // Get all invoices
  async getInvoices(params = {}) {
    return this.get('/invoices', params)
  }

  // Get single invoice
  async getInvoice(id) {
    return this.get(`/invoices/${id}`)
  }

  // Create invoice
  async createInvoice(data) {
    return this.post('/invoices', data)
  }

  // Update invoice
  async updateInvoice(id, data) {
    return this.put(`/invoices/${id}`, data)
  }

  // Delete invoice
  async deleteInvoice(id) {
    return this.delete(`/invoices/${id}`)
  }

  // Update invoice status
  async updateInvoiceStatus(id, status) {
    return this.patch(`/invoices/${id}/status`, { status })
  }

  // Get invoice summary
  async getInvoiceSummary(params = {}) {
    return this.get('/invoices/summary', params)
  }
}

// Payment API
export class PaymentAPI extends ApiService {
  // Get all payments
  async getPayments(params = {}) {
    return this.get('/payments', params)
  }

  // Get single payment
  async getPayment(id) {
    return this.get(`/payments/${id}`)
  }

  // Create payment
  async createPayment(data) {
    return this.post('/payments', data)
  }

  // Update payment
  async updatePayment(id, data) {
    return this.put(`/payments/${id}`, data)
  }

  // Delete payment
  async deletePayment(id) {
    return this.delete(`/payments/${id}`)
  }

  // Get payment allocations
  async getPaymentAllocations(id) {
    return this.get(`/payments/${id}/allocations`)
  }

  // Manual payment allocation
  async allocatePayment(id, allocations) {
    return this.post(`/payments/${id}/allocate`, { allocations })
  }
}

// Receipt API
export class ReceiptAPI extends ApiService {
  // Get all receipts
  async getReceipts(params = {}) {
    return this.get('/receipts', params)
  }

  // Get single receipt
  async getReceipt(id) {
    return this.get(`/receipts/${id}`)
  }

  // Create receipt
  async createReceipt(data) {
    return this.post('/receipts', data)
  }

  // Update receipt
  async updateReceipt(id, data) {
    return this.put(`/receipts/${id}`, data)
  }

  // Delete receipt
  async deleteReceipt(id) {
    return this.delete(`/receipts/${id}`)
  }

  // Auto-generate receipt
  async autoGenerateReceipt(paymentId, note = '') {
    const params = note ? { note } : {}
    return this.post(`/receipts/payment/${paymentId}/auto-generate`, {}, params)
  }

  // Get receipt by payment
  async getReceiptByPayment(paymentId) {
    return this.get(`/receipts/payment/${paymentId}`)
  }
}

// Mock Data Service (for development)
export class MockDataService {
  // Generate mock invoices
  static generateMockInvoices(count = 20) {
    const invoices = []
    const statuses = ['pending', 'paid', 'overdue', 'canceled']
    const types = ['monthly_fee', 'utility_bill', 'maintenance_fee', 'penalty', 'other']
    
    for (let i = 1; i <= count; i++) {
      const status = statuses[Math.floor(Math.random() * statuses.length)]
      const type = types[Math.floor(Math.random() * types.length)]
      const amount = (Math.random() * 5000 + 1000).toFixed(2)
      const dueDate = new Date()
      dueDate.setDate(dueDate.getDate() + Math.floor(Math.random() * 60) - 30)
      
      invoices.push({
        id: `inv-${i}`,
        property_id: Math.floor(Math.random() * 100) + 1,
        amount: amount,
        due_date: dueDate.toISOString().split('T')[0],
        invoice_type: type,
        status: status,
        description: `${type.replace('_', ' ')} for property ${i}`,
        reference_number: `INV-001-2024-${i.toString().padStart(4, '0')}`,
        issued_at: new Date().toISOString(),
        paid_at: status === 'paid' ? new Date().toISOString() : null,
        created_by: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        archived: false
      })
    }
    
    return invoices
  }

  // Generate mock payments
  static generateMockPayments(count = 15) {
    const payments = []
    const methods = ['bank_transfer', 'cash', 'qr_code', 'credit_card', 'mobile_banking']
    
    for (let i = 1; i <= count; i++) {
      const method = methods[Math.floor(Math.random() * methods.length)]
      const amount = (Math.random() * 5000 + 1000).toFixed(2)
      const paymentDate = new Date()
      paymentDate.setDate(paymentDate.getDate() - Math.floor(Math.random() * 30))
      
      payments.push({
        id: `pay-${i}`,
        property_id: Math.floor(Math.random() * 100) + 1,
        amount: amount,
        payment_date: paymentDate.toISOString(),
        method: method,
        note: `Payment for property ${i}`,
        reference_number: `PAY-001-2024-${i.toString().padStart(4, '0')}`,
        bank_reference: method === 'bank_transfer' ? `BANK-${Math.floor(Math.random() * 999999)}` : null,
        created_by: 1,
        created_at: paymentDate.toISOString(),
        updated_at: paymentDate.toISOString(),
        archived: false
      })
    }
    
    return payments
  }

  // Generate mock receipts
  static generateMockReceipts(count = 15) {
    const receipts = []
    
    for (let i = 1; i <= count; i++) {
      const amount = (Math.random() * 5000 + 1000).toFixed(2)
      const issuedAt = new Date()
      issuedAt.setDate(issuedAt.getDate() - Math.floor(Math.random() * 30))
      
      receipts.push({
        id: `rcp-${i}`,
        payment_id: `pay-${i}`,
        receipt_number: `RCP-001-2024-${i.toString().padStart(4, '0')}`,
        amount: amount,
        issued_at: issuedAt.toISOString(),
        note: `Receipt for payment ${i}`,
        created_by: 1,
        created_at: issuedAt.toISOString(),
        updated_at: issuedAt.toISOString(),
        archived: false
      })
    }
    
    return receipts
  }
}

// Create API instances
export const invoiceAPI = new InvoiceAPI()
export const paymentAPI = new PaymentAPI()
export const receiptAPI = new ReceiptAPI()

// Export default API service
export default ApiService

