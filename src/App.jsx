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
  RefreshCw,
  Activity,
  Target
} from 'lucide-react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import * as XLSX from 'xlsx'
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
  
  // Chart data states
  const [monthlyTrend, setMonthlyTrend] = useState([])
  const [accountTypeDistribution, setAccountTypeDistribution] = useState([])
  const [cashFlowData, setCashFlowData] = useState([])
  
  // Multi-tenant states
  const [selectedVillage, setSelectedVillage] = useState(() => {
    return localStorage.getItem('selectedVillage') || 'village-1'
  })
  const [villages] = useState([
    { id: 'village-1', name: 'หมู่บ้านสวนสน', code: 'SWS' },
    { id: 'village-2', name: 'หมู่บ้านบางกะปิ', code: 'BKP' },
    { id: 'village-3', name: 'หมู่บ้านลาดพร้าว', code: 'LPW' },
    { id: 'village-4', name: 'หมู่บ้านรามคำแหง', code: 'RKH' },
    { id: 'village-5', name: 'หมู่บ้านสุขุมวิท', code: 'SKV' }
  ])

  // Load data from API
  useEffect(() => {
    loadDashboardData()
  }, [selectedVillage]) // Reload when village changes

  const handleVillageChange = (villageId) => {
    setSelectedVillage(villageId)
    localStorage.setItem('selectedVillage', villageId)
    setLoading(true)
    loadDashboardData()
  }

  const getCurrentVillage = () => {
    return villages.find(v => v.id === selectedVillage) || villages[0]
  }

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

  const loadMockData = (villageId = selectedVillage) => {
    const village = villages.find(v => v.id === villageId) || villages[0]
    
    // Different data for each village
    const villageData = {
      'village-1': { // หมู่บ้านสวนสน
        totalAssets: 8450000,
        totalRevenue: 125000,
        totalExpenses: 89000,
        netIncome: 36000,
        multiplier: 1
      },
      'village-2': { // หมู่บ้านบางกะปิ
        totalAssets: 12300000,
        totalRevenue: 185000,
        totalExpenses: 142000,
        netIncome: 43000,
        multiplier: 1.4
      },
      'village-3': { // หมู่บ้านลาดพร้าว
        totalAssets: 6750000,
        totalRevenue: 98000,
        totalExpenses: 71000,
        netIncome: 27000,
        multiplier: 0.8
      },
      'village-4': { // หมู่บ้านรามคำแหง
        totalAssets: 15600000,
        totalRevenue: 220000,
        totalExpenses: 178000,
        netIncome: 42000,
        multiplier: 1.7
      },
      'village-5': { // หมู่บ้านสุขุมวิท
        totalAssets: 22100000,
        totalRevenue: 315000,
        totalExpenses: 245000,
        netIncome: 70000,
        multiplier: 2.5
      }
    }
    
    const data = villageData[villageId] || villageData['village-1']
    
    setDashboardData({
      totalAssets: data.totalAssets,
      totalRevenue: data.totalRevenue,
      totalExpenses: data.totalExpenses,
      netIncome: data.netIncome
    })
    
    setRecentTransactions([
      { id: 1, description: `ค่าส่วนกลางเดือนมกราคม - ${village.name}`, amount: Math.round(25000 * data.multiplier), date: '2025-01-15', type: 'รายรับ' },
      { id: 2, description: `ค่าไฟฟ้าส่วนกลาง - ${village.name}`, amount: -Math.round(12000 * data.multiplier), date: '2025-01-14', type: 'รายจ่าย' },
      { id: 3, description: `ค่าน้ำประปา - ${village.name}`, amount: -Math.round(8500 * data.multiplier), date: '2025-01-13', type: 'รายจ่าย' },
      { id: 4, description: `ค่าส่วนกลางเดือนธันวาคม - ${village.name}`, amount: Math.round(28000 * data.multiplier), date: '2025-01-10', type: 'รายรับ' },
      { id: 5, description: `ค่าดูแลสวนส่วนกลาง - ${village.name}`, amount: -Math.round(15000 * data.multiplier), date: '2025-01-08', type: 'รายจ่าย' }
    ])

    // Monthly trend data (last 6 months) - scaled by village
    setMonthlyTrend([
      { month: 'ส.ค. 67', revenue: Math.round(98000 * data.multiplier), expenses: Math.round(75000 * data.multiplier), netIncome: Math.round(23000 * data.multiplier) },
      { month: 'ก.ย. 67', revenue: Math.round(105000 * data.multiplier), expenses: Math.round(82000 * data.multiplier), netIncome: Math.round(23000 * data.multiplier) },
      { month: 'ต.ค. 67', revenue: Math.round(112000 * data.multiplier), expenses: Math.round(88000 * data.multiplier), netIncome: Math.round(24000 * data.multiplier) },
      { month: 'พ.ย. 67', revenue: Math.round(118000 * data.multiplier), expenses: Math.round(91000 * data.multiplier), netIncome: Math.round(27000 * data.multiplier) },
      { month: 'ธ.ค. 67', revenue: Math.round(128000 * data.multiplier), expenses: Math.round(95000 * data.multiplier), netIncome: Math.round(33000 * data.multiplier) },
      { month: 'ม.ค. 68', revenue: Math.round(125000 * data.multiplier), expenses: Math.round(89000 * data.multiplier), netIncome: Math.round(36000 * data.multiplier) }
    ])

    // Account type distribution - scaled by village
    setAccountTypeDistribution([
      { name: 'สินทรัพย์', value: data.totalAssets, color: '#1A2B48' },
      { name: 'หนี้สิน', value: Math.round(data.totalAssets * 0.25), color: '#4A90E2' },
      { name: 'ทุน', value: Math.round(data.totalAssets * 0.75), color: '#28A745' }
    ])

    // Cash flow data (weekly) - scaled by village
    setCashFlowData([
      { week: 'สัปดาห์ 1', inflow: Math.round(35000 * data.multiplier), outflow: Math.round(22000 * data.multiplier), net: Math.round(13000 * data.multiplier) },
      { week: 'สัปดาห์ 2', inflow: Math.round(28000 * data.multiplier), outflow: Math.round(25000 * data.multiplier), net: Math.round(3000 * data.multiplier) },
      { week: 'สัปดาห์ 3', inflow: Math.round(42000 * data.multiplier), outflow: Math.round(28000 * data.multiplier), net: Math.round(14000 * data.multiplier) },
      { week: 'สัปดาห์ 4', inflow: Math.round(38000 * data.multiplier), outflow: Math.round(24000 * data.multiplier), net: Math.round(14000 * data.multiplier) }
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

  // Export Functions
  const exportToPDF = async (reportType = 'dashboard') => {
    try {
      const pdf = new jsPDF('p', 'mm', 'a4')
      
      // Add Thai font support (basic)
      pdf.setFont('helvetica')
      
      // Header
      pdf.setFontSize(20)
      pdf.text('Village Accounting System', 20, 20)
      pdf.setFontSize(14)
      pdf.text(`รายงาน${reportType === 'dashboard' ? 'ภาพรวม' : reportType}`, 20, 30)
      pdf.text(`วันที่: ${new Date().toLocaleDateString('th-TH')}`, 20, 40)
      
      let yPosition = 60
      
      if (reportType === 'dashboard') {
        // Dashboard Summary
        pdf.setFontSize(16)
        pdf.text('สรุปภาพรวมทางการเงิน', 20, yPosition)
        yPosition += 20
        
        pdf.setFontSize(12)
        pdf.text(`สินทรัพย์รวม: ${formatCurrency(dashboardData.totalAssets)}`, 20, yPosition)
        yPosition += 10
        pdf.text(`รายรับรวม: ${formatCurrency(dashboardData.totalRevenue)}`, 20, yPosition)
        yPosition += 10
        pdf.text(`รายจ่ายรวม: ${formatCurrency(dashboardData.totalExpenses)}`, 20, yPosition)
        yPosition += 10
        pdf.text(`กำไรสุทธิ: ${formatCurrency(dashboardData.netIncome)}`, 20, yPosition)
        yPosition += 20
        
        // Recent Transactions
        pdf.setFontSize(16)
        pdf.text('รายการเคลื่อนไหวล่าสุด', 20, yPosition)
        yPosition += 15
        
        pdf.setFontSize(10)
        recentTransactions.forEach((transaction, index) => {
          if (yPosition > 250) {
            pdf.addPage()
            yPosition = 20
          }
          pdf.text(`${index + 1}. ${transaction.description}`, 20, yPosition)
          pdf.text(`${formatCurrency(Math.abs(transaction.amount))}`, 120, yPosition)
          pdf.text(`${transaction.type}`, 160, yPosition)
          yPosition += 8
        })
      }
      
      // Save PDF with village name
      const village = getCurrentVillage()
      pdf.save(`${village.code}-accounting-${reportType}-${new Date().toISOString().split('T')[0]}.pdf`)
      
    } catch (error) {
      console.error('PDF Export Error:', error)
      alert('เกิดข้อผิดพลาดในการส่งออก PDF')
    }
  }

  const exportChartsToImage = async () => {
    try {
      const chartsContainer = document.querySelector('.charts-container')
      if (!chartsContainer) return
      
      const canvas = await html2canvas(chartsContainer, {
        backgroundColor: '#ffffff',
        scale: 2,
        useCORS: true
      })
      
      const village = getCurrentVillage()
      const link = document.createElement('a')
      link.download = `${village.code}-accounting-charts-${new Date().toISOString().split('T')[0]}.png`
      link.href = canvas.toDataURL()
      link.click()
      
    } catch (error) {
      console.error('Chart Export Error:', error)
      alert('เกิดข้อผิดพลาดในการส่งออกกราฟ')
    }
  }

  const exportToExcel = (dataType = 'transactions') => {
    try {
      let data = []
      let filename = ''
      
      if (dataType === 'transactions') {
        data = recentTransactions.map(t => ({
          'รายการ': t.description,
          'ประเภท': t.type,
          'จำนวนเงิน': t.amount,
          'วันที่': formatDate(t.date)
        }))
        filename = 'village-accounting-transactions'
      } else if (dataType === 'accounts') {
        data = chartOfAccounts.map(a => ({
          'รหัสบัญชี': a.account_code,
          'ชื่อบัญชี': a.account_name,
          'ประเภท': a.account_type,
          'ยอดคงเหลือ': a.balance || 0
        }))
        filename = 'village-accounting-accounts'
      } else if (dataType === 'summary') {
        data = [
          { 'รายการ': 'สินทรัพย์รวม', 'จำนวนเงิน': dashboardData.totalAssets },
          { 'รายการ': 'รายรับรวม', 'จำนวนเงิน': dashboardData.totalRevenue },
          { 'รายการ': 'รายจ่ายรวม', 'จำนวนเงิน': dashboardData.totalExpenses },
          { 'รายการ': 'กำไรสุทธิ', 'จำนวนเงิน': dashboardData.netIncome }
        ]
        filename = 'village-accounting-summary'
      }
      
      const ws = XLSX.utils.json_to_sheet(data)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
      
      const village = getCurrentVillage()
      XLSX.writeFile(wb, `${village.code}-${filename}-${new Date().toISOString().split('T')[0]}.xlsx`)
      
    } catch (error) {
      console.error('Excel Export Error:', error)
      alert('เกิดข้อผิดพลาดในการส่งออก Excel')
    }
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

      {/* Export Buttons */}
      <div className="content-section mb-6">
        <div className="section-title">
          <Download />
          ส่งออกข้อมูล
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button 
            onClick={() => exportToPDF('dashboard')}
            className="btn btn-primary"
          >
            <Download className="w-4 h-4" />
            ส่งออก PDF Dashboard
          </button>
          <button 
            onClick={exportChartsToImage}
            className="btn btn-secondary"
          >
            <Download className="w-4 h-4" />
            ส่งออกกราฟเป็นรูป
          </button>
          <button 
            onClick={() => exportToExcel('summary')}
            className="btn btn-outline"
          >
            <Download className="w-4 h-4" />
            ส่งออก Excel สรุป
          </button>
        </div>
      </div>

      {/* Charts & Analytics Section */}
      <div className="charts-container">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Monthly Trend Chart */}
        <div className="content-section">
          <div className="section-title">
            <Activity />
            แนวโน้มรายรับ-รายจ่าย (6 เดือนล่าสุด)
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="month" 
                tick={{ fontSize: 12, fill: '#6c757d' }}
                axisLine={{ stroke: '#dee2e6' }}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#6c757d' }}
                axisLine={{ stroke: '#dee2e6' }}
                tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
              />
              <Tooltip 
                formatter={(value, name) => [formatCurrency(value), name === 'revenue' ? 'รายรับ' : name === 'expenses' ? 'รายจ่าย' : 'กำไรสุทธิ']}
                labelStyle={{ color: '#333' }}
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #dee2e6',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="revenue" 
                stroke="#28A745" 
                strokeWidth={3}
                dot={{ fill: '#28A745', strokeWidth: 2, r: 4 }}
                name="รายรับ"
              />
              <Line 
                type="monotone" 
                dataKey="expenses" 
                stroke="#dc3545" 
                strokeWidth={3}
                dot={{ fill: '#dc3545', strokeWidth: 2, r: 4 }}
                name="รายจ่าย"
              />
              <Line 
                type="monotone" 
                dataKey="netIncome" 
                stroke="#1A2B48" 
                strokeWidth={3}
                dot={{ fill: '#1A2B48', strokeWidth: 2, r: 4 }}
                name="กำไรสุทธิ"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Account Type Distribution */}
        <div className="content-section">
          <div className="section-title">
            <PieChart />
            การกระจายตัวของสินทรัพย์
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <RechartsPieChart>
              <Pie
                data={accountTypeDistribution}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                labelLine={false}
              >
                {accountTypeDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value) => [formatCurrency(value), 'มูลค่า']}
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #dee2e6',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                }}
              />
            </RechartsPieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cash Flow Chart */}
      <div className="content-section mb-6">
        <div className="section-title">
          <Target />
          กระแสเงินสดรายสัปดาห์ (เดือนปัจจุบัน)
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={cashFlowData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="week" 
              tick={{ fontSize: 12, fill: '#6c757d' }}
              axisLine={{ stroke: '#dee2e6' }}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#6c757d' }}
              axisLine={{ stroke: '#dee2e6' }}
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
            />
            <Tooltip 
              formatter={(value, name) => [
                formatCurrency(value), 
                name === 'inflow' ? 'เงินเข้า' : name === 'outflow' ? 'เงินออก' : 'สุทธิ'
              ]}
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #dee2e6',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend />
            <Bar dataKey="inflow" fill="#28A745" name="เงินเข้า" radius={[4, 4, 0, 0]} />
            <Bar dataKey="outflow" fill="#dc3545" name="เงินออก" radius={[4, 4, 0, 0]} />
            <Bar dataKey="net" fill="#1A2B48" name="สุทธิ" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
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
          {/* Village Selector */}
          <div className="village-selector">
            <select 
              value={selectedVillage}
              onChange={(e) => handleVillageChange(e.target.value)}
              className="village-select"
            >
              {villages.map(village => (
                <option key={village.id} value={village.id}>
                  {village.name} ({village.code})
                </option>
              ))}
            </select>
          </div>
          
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

