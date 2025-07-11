// API Service for Village Accounting System
const API_BASE_URL = 'https://8000-ilz5cj354gz2af8ztnznh-5b92cd07.manusvm.computer';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Chart of Accounts
  async getAccounts() {
    return this.request('/api/v1/accounting/accounts');
  }

  // Trial Balance
  async getTrialBalance() {
    return this.request('/api/v1/accounting/trial-balance');
  }

  // Journal Entries
  async getJournalEntries(limit = 5) {
    return this.request(`/api/v1/accounting/journal-entries?limit=${limit}`);
  }

  // General Ledger
  async getGeneralLedger() {
    return this.request('/api/v1/accounting/ledger');
  }

  // Financial Reports
  async getIncomeStatement() {
    return this.request('/api/v1/accounting/reports/income-statement');
  }

  async getBalanceSheet() {
    return this.request('/api/v1/accounting/reports/balance-sheet');
  }

  // Health Check
  async healthCheck() {
    return this.request('/health');
  }

  // Config
  async getConfig() {
    return this.request('/config');
  }
}

export const apiService = new ApiService();
export default apiService;

