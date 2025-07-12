import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar.jsx'
import { 
  Home, 
  CreditCard, 
  QrCode, 
  Bell, 
  User, 
  FileText, 
  Camera,
  Smartphone,
  Shield,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react'
import './App.css'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userProfile, setUserProfile] = useState(null)
  const [liffReady, setLiffReady] = useState(false)

  // Mock user data for development
  const mockUser = {
    displayName: "สมชาย ใจดี",
    pictureUrl: "",
    userId: "U1234567890",
    statusMessage: "ผู้อยู่อาศัย บ้านเลขที่ A-101"
  }

  const mockVillageData = {
    villageName: "หมู่บ้านสมาร์ทวิลเลจ",
    houseNumber: "A-101",
    monthlyFee: 2500,
    dueDate: "15 ก.พ. 2568",
    status: "paid"
  }

  const mockAnnouncements = [
    {
      id: 1,
      title: "ปิดระบบน้ำชั่วคราว",
      message: "วันที่ 20 ก.พ. 2568 เวลา 09:00-12:00 น.",
      type: "warning",
      date: "2025-02-15"
    },
    {
      id: 2,
      title: "ประชุมคณะกรรมการหมู่บ้าน",
      message: "วันเสาร์ที่ 25 ก.พ. 2568 เวลา 19:00 น.",
      type: "info",
      date: "2025-02-14"
    }
  ]

  useEffect(() => {
    // Initialize LIFF
    const initializeLiff = async () => {
      try {
        // For development, we'll simulate LIFF initialization
        // In production, replace with actual LIFF ID
        console.log('Initializing LIFF...')
        
        // Simulate LIFF initialization delay
        setTimeout(() => {
          setLiffReady(true)
          // For development, auto-login with mock data
          setIsLoggedIn(true)
          setUserProfile(mockUser)
        }, 1000)
        
        // Actual LIFF initialization code (commented for development)
        /*
        const liff = (await import('@line/liff')).default
        await liff.init({ liffId: 'YOUR_LIFF_ID' })
        setLiffReady(true)
        
        if (liff.isLoggedIn()) {
          const profile = await liff.getProfile()
          setUserProfile(profile)
          setIsLoggedIn(true)
        }
        */
      } catch (error) {
        console.error('LIFF initialization failed:', error)
        setLiffReady(true) // Still allow app to work in development
      }
    }

    initializeLiff()
  }, [])

  const handleLogin = async () => {
    try {
      // For development, simulate login
      setIsLoggedIn(true)
      setUserProfile(mockUser)
      
      // Actual LIFF login code (commented for development)
      /*
      const liff = (await import('@line/liff')).default
      if (!liff.isLoggedIn()) {
        liff.login()
      }
      */
    } catch (error) {
      console.error('Login failed:', error)
    }
  }

  const handleLogout = async () => {
    try {
      setIsLoggedIn(false)
      setUserProfile(null)
      
      // Actual LIFF logout code (commented for development)
      /*
      const liff = (await import('@line/liff')).default
      liff.logout()
      */
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const generateQRCode = () => {
    // Simulate QR code generation
    alert('QR Code สำหรับเข้าออกหมู่บ้านถูกสร้างแล้ว\nใช้ได้ภายใน 5 นาที')
  }

  const uploadPaymentSlip = () => {
    // Simulate payment slip upload
    alert('เปิดกล้องเพื่อถ่ายภาพสลิปการชำระเงิน')
  }

  if (!liffReady) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">กำลังเชื่อมต่อ LINE...</p>
        </div>
      </div>
    )
  }

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <Home className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl">Smart Village</CardTitle>
            <CardDescription>
              ระบบจัดการหมู่บ้านอัจฉริยะ
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-center text-gray-600">
              เข้าสู่ระบบด้วย LINE เพื่อเข้าถึงบริการต่างๆ ของหมู่บ้าน
            </p>
            <Button 
              onClick={handleLogin} 
              className="w-full bg-green-500 hover:bg-green-600"
              size="lg"
            >
              <Smartphone className="w-5 h-5 mr-2" />
              เข้าสู่ระบบด้วย LINE
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-md mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Avatar>
                <AvatarImage src={userProfile?.pictureUrl} />
                <AvatarFallback>
                  {userProfile?.displayName?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="font-semibold text-gray-900">
                  {userProfile?.displayName || 'ผู้ใช้'}
                </h1>
                <p className="text-sm text-gray-500">{mockVillageData.houseNumber}</p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <User className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-md mx-auto p-4">
        <Tabs defaultValue="home" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="home">
              <Home className="w-4 h-4" />
            </TabsTrigger>
            <TabsTrigger value="payment">
              <CreditCard className="w-4 h-4" />
            </TabsTrigger>
            <TabsTrigger value="access">
              <QrCode className="w-4 h-4" />
            </TabsTrigger>
            <TabsTrigger value="announcements">
              <Bell className="w-4 h-4" />
            </TabsTrigger>
          </TabsList>

          {/* Home Tab */}
          <TabsContent value="home" className="space-y-4 mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">ยินดีต้อนรับ</CardTitle>
                <CardDescription>{mockVillageData.villageName}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <Home className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                    <p className="text-sm font-medium">บ้านเลขที่</p>
                    <p className="text-lg font-bold text-blue-600">
                      {mockVillageData.houseNumber}
                    </p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
                    <p className="text-sm font-medium">สถานะ</p>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      ชำระแล้ว
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">เมนูด่วน</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-3">
                <Button 
                  variant="outline" 
                  className="h-20 flex-col"
                  onClick={generateQRCode}
                >
                  <QrCode className="w-6 h-6 mb-1" />
                  <span className="text-xs">QR เข้าออก</span>
                </Button>
                <Button 
                  variant="outline" 
                  className="h-20 flex-col"
                  onClick={uploadPaymentSlip}
                >
                  <Camera className="w-6 h-6 mb-1" />
                  <span className="text-xs">อัพโหลดสลิป</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <FileText className="w-6 h-6 mb-1" />
                  <span className="text-xs">ประวัติการชำระ</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <Shield className="w-6 h-6 mb-1" />
                  <span className="text-xs">รายงานปัญหา</span>
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Payment Tab */}
          <TabsContent value="payment" className="space-y-4 mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">ค่าบำรุงรายเดือน</CardTitle>
                <CardDescription>
                  เดือน กุมภาพันธ์ 2568
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>ค่าบำรุงหมู่บ้าน</span>
                    <span className="font-semibold">฿{mockVillageData.monthlyFee.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>กำหนดชำระ</span>
                    <span className="text-orange-600">{mockVillageData.dueDate}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>สถานะ</span>
                    <Badge className="bg-green-100 text-green-800">
                      ชำระแล้ว
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">วิธีการชำระเงิน</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={uploadPaymentSlip}
                >
                  <Camera className="w-5 h-5 mr-3" />
                  ถ่ายภาพสลิปการโอนเงิน
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <CreditCard className="w-5 h-5 mr-3" />
                  ชำระผ่านบัตรเครดิต
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Smartphone className="w-5 h-5 mr-3" />
                  ชำระผ่าน Mobile Banking
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Access Tab */}
          <TabsContent value="access" className="space-y-4 mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">QR Code เข้าออกหมู่บ้าน</CardTitle>
                <CardDescription>
                  สร้าง QR Code สำหรับเข้าออกหมู่บ้าน
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center space-y-4">
                <div className="w-48 h-48 bg-gray-100 rounded-lg flex items-center justify-center mx-auto">
                  <QrCode className="w-24 h-24 text-gray-400" />
                </div>
                <Button 
                  onClick={generateQRCode}
                  className="w-full"
                  size="lg"
                >
                  สร้าง QR Code ใหม่
                </Button>
                <p className="text-sm text-gray-500">
                  QR Code มีอายุการใช้งาน 5 นาที
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">ประวัติการเข้าออก</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <div>
                        <p className="font-medium">เข้าหมู่บ้าน</p>
                        <p className="text-sm text-gray-500">วันนี้ 08:30</p>
                      </div>
                    </div>
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <div>
                        <p className="font-medium">ออกจากหมู่บ้าน</p>
                        <p className="text-sm text-gray-500">เมื่อวาน 17:45</p>
                      </div>
                    </div>
                    <CheckCircle className="w-5 h-5 text-blue-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Announcements Tab */}
          <TabsContent value="announcements" className="space-y-4 mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">ประกาศจากหมู่บ้าน</CardTitle>
                <CardDescription>
                  ข่าวสารและประกาศสำคัญ
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {mockAnnouncements.map((announcement) => (
                  <div key={announcement.id} className="p-4 border rounded-lg">
                    <div className="flex items-start space-x-3">
                      {announcement.type === 'warning' ? (
                        <AlertCircle className="w-5 h-5 text-orange-500 mt-0.5" />
                      ) : (
                        <Bell className="w-5 h-5 text-blue-500 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <h3 className="font-medium">{announcement.title}</h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {announcement.message}
                        </p>
                        <div className="flex items-center mt-2 text-xs text-gray-500">
                          <Clock className="w-3 h-3 mr-1" />
                          {announcement.date}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

