import { useState, useEffect } from 'react'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  DollarSign,
  FileText,
  Calendar,
  Settings,
  Menu,
  X,
  Download,
  Users,
  CreditCard,
  PieChart,
  Building2,
  RefreshCw
} from 'lucide-react'
import apiService from './services/api'
import './App.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Data states
  const [dashboardData, setDashboardData] = useState({
    totalAssets: 0,
    totalRevenue: 0,
    totalExpenses: 0,
    netIncome: 0
  })
  const [recentTransactions, setRecentTransactions] = useState([])
  const [chartOfAccounts, setChartOfAccounts] = useState([])
  const [trialBalance, setTrialBalance] = useState([])

  // Load data from API
  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load trial balance for dashboard stats
      const trialBalanceData = await apiService.getTrialBalance()
      if (trialBalanceData && trialBalanceData.accounts) {
        calculateDashboardStats(trialBalanceData.accounts)
        setTrialBalance(trialBalanceData.accounts)
      }

      // Load recent journal entries
      const journalEntries = await apiService.getJournalEntries(5)
      if (journalEntries && journalEntries.entries) {
        setRecentTransactions(journalEntries.entries)
      }

      // Load chart of accounts
      const accounts = await apiService.getAccounts()
      if (accounts && accounts.accounts) {
        setChartOfAccounts(accounts.accounts)
      }

    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      setError('ไม่สามารถโหลดข้อมูลได้ กรุณาลองใหม่อีกครั้ง')
      // Use mock data as fallback
      loadMockData()
    } finally {
      setLoading(false)
    }
  }

  const calculateDashboardStats = (accounts) => {
    let totalAssets = 0
    let totalRevenue = 0
    let totalExpenses = 0

    accounts.forEach(account => {
      const balance = parseFloat(account.balance || 0)
      
      if (account.account_type === 'ASSET') {
        totalAssets += balance
      } else if (account.account_type === 'REVENUE') {
        totalRevenue += balance
      } else if (account.account_type === 'EXPENSE') {
        totalExpenses += balance
      }
    })

    const netIncome = totalRevenue - totalExpenses

    setDashboardData({
      totalAssets,
      totalRevenue,
      totalExpenses,
      netIncome
    })
  }

  const loadMockData = () => {
    setDashboardData({
      totalAssets: 8450000,
      totalRevenue: 125000,
      totalExpenses: 89000,
      netIncome: 36000
    })
    
    setRecentTransactions([
      { id: 1, description: 'ค่าส่วนกลางเดือนมกราคม', amount: 25000, date: '2025-01-15', type: 'รายรับ' },
      { id: 2, description: 'ค่าไฟฟ้าส่วนกลาง', amount: -12000, date: '2025-01-14', type: 'รายจ่าย' },
      { id: 3, description: 'ค่าน้ำประปา', amount: -8500, date: '2025-01-13', type: 'รายจ่าย' },
      { id: 4, description: 'ค่าส่วนกลางเดือนธันวาคม', amount: 28000, date: '2025-01-10', type: 'รายรับ' },
      { id: 5, description: 'ค่าดูแลสวนส่วนกลาง', amount: -15000, date: '2025-01-08', type: 'รายจ่าย' }
    ])
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('th-TH', {
      style: 'currency',
      currency: 'THB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('th-TH', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'transactions', label: 'รายการเคลื่อนไหว', icon: FileText },
    { id: 'accounts', label: 'ผังบัญชี', icon: PieChart },
    { id: 'reports', label: 'รายงานทางการเงิน', icon: Calendar },
    { id: 'payments', label: 'การรับชำระ', icon: CreditCard },
    { id: 'settings', label: 'ตั้งค่าระบบ', icon: Settings }
  ]

  const StatCard = ({ title, value, icon: Icon, trend, bgColor }) => (
    <div className="stat-card">
      <div className={`icon ${bgColor}`}>
        <Icon />
      </div>
      <div className="info">
        <h3>{formatCurrency(value)}</h3>
        <p>{title}</p>
        {trend && (
          <div className={`flex items-center mt-1 text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
    </div>
  )

  const renderDashboard = () => (
    <div>
      <div className="page-header">
        <h1 className="page-title">ภาพรวมระบบบัญชีหมู่บ้าน</h1>
        <p className="page-subtitle">ระบบบัญชีครบวงจร สำหรับการจัดการการเงินหมู่บ้าน</p>
      </div>

      {error && (
        <div className="error">
          <strong>เกิดข้อผิดพลาด:</strong> {error}
        </div>
      )}

      <div className="stats-grid">
        <StatCard 
          title="สินทรัพย์รวม" 
          value={dashboardData.totalAssets} 
          icon={Building2} 
          trend={12.5}
          bgColor="bg-blue-500"
        />
        <StatCard 
          title="รายรับรวม" 
          value={dashboardData.totalRevenue} 
          icon={TrendingUp} 
          trend={8.2}
          bgColor="bg-green-500"
        />
        <StatCard 
          title="รายจ่ายรวม" 
          value={dashboardData.totalExpenses} 
          icon={TrendingDown} 
          trend={-3.1}
          bgColor="bg-red-500"
        />
        <StatCard 
          title="กำไรสุทธิ" 
          value={dashboardData.netIncome} 
          icon={DollarSign} 
          trend={15.8}
          bgColor="bg-purple-500"
        />
      </div>

      <div className="content-section">
        <div className="section-title">
          <FileText />
          รายการเคลื่อนไหวล่าสุด
        </div>
        {loading ? (
          <div className="loading">กำลังโหลดข้อมูล...</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>รายการ</th>
                <th>ประเภท</th>
                <th>จำนวนเงิน</th>
                <th>วันที่</th>
              </tr>
            </thead>
            <tbody>
              {recentTransactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td>{transaction.description}</td>
                  <td>
                    <span className={`px-2 py-1 rounded text-xs ${
                      transaction.type === 'รายรับ' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {transaction.type}
                    </span>
                  </td>
                  <td className={transaction.amount > 0 ? 'text-green-600' : 'text-red-600'}>
                    {formatCurrency(Math.abs(transaction.amount))}
                  </td>
                  <td>{formatDate(transaction.date)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )

  const renderTransactions = () => (
    <div>
      <div className="page-header">
        <h1 className="page-title">รายการเคลื่อนไหวทั้งหมด</h1>
        <p className="page-subtitle">ประวัติการเคลื่อนไหวทางการเงินของหมู่บ้าน</p>
      </div>
      <div className="content-section">
        <div className="section-title">
          <FileText />
          Journal Entries
        </div>
        <p className="text-gray-600">รายการ Journal Entry ทั้งหมดจะแสดงที่นี่</p>
      </div>
    </div>
  )

  const renderAccounts = () => (
    <div>
      <div className="page-header">
        <h1 className="page-title">ผังบัญชี</h1>
        <p className="page-subtitle">รายการบัญชีทั้งหมดในระบบ</p>
      </div>
      <div className="content-section">
        <div className="section-title">
          <PieChart />
          Chart of Accounts
        </div>
        {loading ? (
          <div className="loading">กำลังโหลดข้อมูล...</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>รหัสบัญชี</th>
                <th>ชื่อบัญชี</th>
                <th>ประเภท</th>
                <th>ยอดคงเหลือ</th>
              </tr>
            </thead>
            <tbody>
              {chartOfAccounts.slice(0, 10).map((account) => (
                <tr key={account.id}>
                  <td>{account.account_code}</td>
                  <td>{account.account_name}</td>
                  <td>{account.account_type}</td>
                  <td>{formatCurrency(account.balance || 0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )

  const renderReports = () => (
    <div>
      <div className="page-header">
        <h1 className="page-title">รายงานทางการเงิน</h1>
        <p className="page-subtitle">รายงานสำหรับการวิเคราะห์ทางการเงิน</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="content-section">
          <div className="section-title">
            <Calendar />
            Trial Balance
          </div>
          <p className="text-gray-600 mb-4">งบทดลอง</p>
          <button className="btn btn-primary">
            <Download className="w-4 h-4" />
            ดาวน์โหลด PDF
          </button>
        </div>
        <div className="content-section">
          <div className="section-title">
            <BarChart3 />
            Income Statement
          </div>
          <p className="text-gray-600 mb-4">งบกำไรขาดทุน</p>
          <button className="btn btn-primary">
            <Download className="w-4 h-4" />
            ดาวน์โหลด PDF
          </button>
        </div>
        <div className="content-section">
          <div className="section-title">
            <Building2 />
            Balance Sheet
          </div>
          <p className="text-gray-600 mb-4">งบดุล</p>
          <button className="btn btn-primary">
            <Download className="w-4 h-4" />
            ดาวน์โหลด PDF
          </button>
        </div>
      </div>
    </div>
  )

  const renderPayments = () => (
    <div>
      <div className="page-header">
        <h1 className="page-title">การรับชำระ</h1>
        <p className="page-subtitle">จัดการการรับชำระเงินจากลูกบ้าน</p>
      </div>
      <div className="content-section">
        <div className="section-title">
          <CreditCard />
          Payment Management
        </div>
        <p className="text-gray-600">ระบบการรับชำระเงินจะแสดงที่นี่</p>
      </div>
    </div>
  )

  const renderSettings = () => (
    <div>
      <div className="page-header">
        <h1 className="page-title">ตั้งค่าระบบ</h1>
        <p className="page-subtitle">การตั้งค่าระบบบัญชี</p>
      </div>
      <div className="content-section">
        <div className="section-title">
          <Settings />
          ตั้งค่าระบบบัญชี
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-medium">ระบบบัญชีอัตโนมัติ</h3>
              <p className="text-sm text-gray-600">สร้าง Journal Entry อัตโนมัติเมื่อมีการรับชำระ</p>
            </div>
            <div className="w-12 h-6 bg-green-500 rounded-full relative">
              <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
            </div>
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-medium">สกุลเงิน</h3>
              <p className="text-sm text-gray-600">บาท (THB)</p>
            </div>
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-medium">ปีงบประมาณ</h3>
              <p className="text-sm text-gray-600">2025</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard': return renderDashboard()
      case 'transactions': return renderTransactions()
      case 'accounts': return renderAccounts()
      case 'reports': return renderReports()
      case 'payments': return renderPayments()
      case 'settings': return renderSettings()
      default: return renderDashboard()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="smart-village-header">
        <div className="header-left">
          <button 
            className="menu-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu />
          </button>
          <div className="logo">
            <div className="logo-icon">
              <BarChart3 />
            </div>
            <span className="logo-text">Village Accounting</span>
          </div>
        </div>
        <div className="header-right">
          <button 
            onClick={loadDashboardData}
            className="btn btn-secondary"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'กำลังโหลด...' : 'รีเฟรชข้อมูล'}
          </button>
          <div className="user-info">
            <div className="user-avatar">A</div>
            <div className="user-details">
              <div className="user-name">ระบบบัญชีหมู่บ้าน</div>
              <div className="user-role">Admin</div>
            </div>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <nav className={`smart-village-sidebar ${sidebarOpen ? '' : 'collapsed'}`}>
        <ul className="sidebar-menu">
          {menuItems.map((item) => (
            <li key={item.id}>
              <a
                href="#"
                className={activeTab === item.id ? 'active' : ''}
                onClick={(e) => {
                  e.preventDefault()
                  setActiveTab(item.id)
                  if (window.innerWidth < 768) setSidebarOpen(false)
                }}
              >
                <item.icon />
                <span className="menu-text">{item.label}</span>
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* Main Content */}
      <main className={`smart-village-main ${sidebarOpen ? '' : 'expanded'}`}>
        {renderContent()}
      </main>
    </div>
  )
}

export default App

