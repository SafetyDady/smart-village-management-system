# Property Management System Documentation
## Smart Village Management System (LIFF Edition)

### 📋 สารบัญ
1. [ภาพรวมระบบ](#ภาพรวมระบบ)
2. [ฟีเจอร์หลัก](#ฟีเจอร์หลัก)
3. [คู่มือการใช้งาน](#คู่มือการใช้งาน)
4. [โครงสร้างข้อมูล](#โครงสร้างข้อมูล)
5. [รายละเอียดทางเทคนิค](#รายละเอียดทางเทคนิค)
6. [การบำรุงรักษา](#การบำรุงรักษา)

---

## 🏠 ภาพรวมระบบ

Property Management System เป็นส่วนหนึ่งของ Smart Village Management System ที่ออกแบบมาเพื่อจัดการข้อมูลทรัพย์สินในหมู่บ้านอย่างมีประสิทธิภาพ ระบบนี้ช่วยให้ผู้ดูแลหมู่บ้านสามารถติดตาม จัดการ และบำรุงรักษาข้อมูลทรัพย์สินได้อย่างครบถ้วน

### 🎯 วัตถุประสงค์
- จัดการข้อมูลทรัพย์สินในหมู่บ้านอย่างเป็นระบบ
- ติดตามสถานะการเช่าและการอยู่อาศัย
- เก็บข้อมูลเจ้าของและผู้เช่าอย่างครบถ้วน
- สร้างรายงานและสถิติการใช้งานทรัพย์สิน
- ลดความผิดพลาดในการจัดการข้อมูล

### 👥 กลุ่มผู้ใช้งาน
- **Village Admin**: ผู้ดูแลหมู่บ้านที่มีสิทธิ์เต็มในการจัดการข้อมูล
- **Property Owner**: เจ้าของทรัพย์สินที่สามารถดูข้อมูลของตนเอง
- **Tenant**: ผู้เช่าที่สามารถดูข้อมูลการเช่า

---

## ⚡ ฟีเจอร์หลัก

### 📝 CRUD Operations
ระบบรองรับการดำเนินการพื้นฐาน 4 ประการ:

#### 1. Create (เพิ่มข้อมูล)
- เพิ่มทรัพย์สินใหม่เข้าสู่ระบบ
- กรอกข้อมูลครบถ้วนผ่าน Modal Form
- ตรวจสอบความถูกต้องของข้อมูลอัตโนมัติ
- ป้องกันการเพิ่มบ้านเลขที่ซ้ำ

#### 2. Read (อ่านข้อมูล)
- แสดงรายการทรัพย์สินทั้งหมดในรูปแบบตาราง
- เรียงลำดับตามบ้านเลขที่จากน้อยไปมาก
- แสดงข้อมูลสำคัญในหน้าหลัก
- ระบบค้นหาและกรองข้อมูล

#### 3. Update (แก้ไขข้อมูล)
- แก้ไขข้อมูลทรัพย์สินที่มีอยู่
- โหลดข้อมูลเดิมเข้าฟอร์มอัตโนมัติ
- บันทึกการเปลี่ยนแปลงทันที
- ตรวจสอบความถูกต้องก่อนบันทึก

#### 4. Delete (ลบข้อมูล)
- ลบทรัพย์สินออกจากระบบ
- Modal ยืนยันการลบเพื่อป้องกันความผิดพลาด
- อัพเดทตารางทันทีหลังลบ

### 🔍 ฟีเจอร์เสริม

#### Search & Filter
- **Real-time Search**: ค้นหาข้อมูลแบบทันทีขณะพิมพ์
- **Multiple Fields**: ค้นหาได้หลายฟิลด์พร้อมกัน
- **Status Filter**: กรองตามสถานะทรัพย์สิน
- **Type Filter**: กรองตามประเภททรัพย์สิน

#### Data Validation
- **Required Fields**: ตรวจสอบฟิลด์ที่จำเป็น
- **Format Validation**: ตรวจสอบรูปแบบข้อมูล
- **Duplicate Prevention**: ป้องกันข้อมูลซ้ำ
- **Error Messages**: แสดงข้อความแจ้งเตือนที่ชัดเจน

#### User Interface
- **Responsive Design**: รองรับทุกขนาดหน้าจอ
- **Modal System**: ป๊อปอัพสำหรับการจัดการข้อมูล
- **Color Coding**: ใช้สีแยกประเภทและสถานะ
- **Loading States**: แสดงสถานะการโหลดข้อมูล

---

## 📖 คู่มือการใช้งาน

### 🚀 การเข้าถึงระบบ
1. เข้าสู่ Village Admin Dashboard
2. คลิกเมนู "Property Management" ทางด้านซ้าย
3. หน้าจอจะแสดงตารางทรัพย์สินทั้งหมด

### ➕ การเพิ่มทรัพย์สินใหม่

#### ขั้นตอนการเพิ่ม:
1. **คลิกปุ่ม "+ เพิ่มทรัพย์สินใหม่"** ที่ด้านบนของตาราง
2. **กรอกข้อมูลในฟอร์ม:**
   - **บ้านเลขที่*** (จำเป็น): เช่น 123/45
   - **ประเภททรัพย์สิน*** (จำเป็น): เลือกจาก dropdown
   - **ชื่อเจ้าของ**: ชื่อ-นามสกุลเจ้าของ
   - **เบอร์โทรเจ้าของ**: หมายเลขโทรศัพท์
   - **ชื่อผู้เช่า/ผู้อยู่อาศัย**: ถ้ามี
   - **เบอร์โทรผู้เช่า**: ถ้ามี
   - **สถานะ*** (จำเป็น): เลือกสถานะปัจจุบัน
   - **ค่าเช่า/เดือน**: จำนวนเงิน (ถ้ามี)
   - **หมายเหตุ**: ข้อมูลเพิ่มเติม
3. **คลิก "บันทึก"** เพื่อเพิ่มข้อมูล
4. **ระบบจะแสดงข้อความยืนยัน** และอัพเดทตาราง

#### ข้อมูลที่จำเป็น (Required):
- บ้านเลขที่
- ประเภททรัพย์สิน  
- สถานะ

### ✏️ การแก้ไขข้อมูล

#### ขั้นตอนการแก้ไข:
1. **ค้นหาทรัพย์สิน** ที่ต้องการแก้ไขในตาราง
2. **คลิกปุ่ม "แก้ไข"** (สีส้ม) ในคอลัมน์การดำเนินการ
3. **ฟอร์มจะเปิดขึ้น** พร้อมข้อมูลเดิม
4. **แก้ไขข้อมูล** ตามต้องการ
5. **คลิก "บันทึก"** เพื่อยืนยันการเปลี่ยนแปลง
6. **ระบบจะอัพเดทข้อมูล** ในตารางทันที

### 🗑️ การลบข้อมูล

#### ขั้นตอนการลบ:
1. **ค้นหาทรัพย์สิน** ที่ต้องการลบ
2. **คลิกปุ่ม "แก้ไข"** เพื่อเข้าสู่โหมดจัดการ
3. **คลิกปุ่ม "ลบ"** (สีแดง) ในฟอร์ม
4. **ยืนยันการลบ** ในป๊อปอัพที่ปรากฏ
5. **ระบบจะลบข้อมูล** และอัพเดทตาราง

⚠️ **คำเตือน**: การลบข้อมูลไม่สามารถยกเลิกได้

### 🔍 การค้นหาและกรองข้อมูล

#### การค้นหา:
- **พิมพ์คำค้นหา** ในช่อง "ค้นหาบ้านเลขที่, เจ้าของ, ผู้เช่า..."
- **ระบบจะกรองข้อมูล** แบบทันทีขณะพิมพ์
- **ค้นหาได้หลายฟิลด์**: บ้านเลขที่, ชื่อเจ้าของ, ชื่อผู้เช่า

#### การกรองข้อมูล:
- **กรองตามสถานะ**: เลือกสถานะจาก dropdown
- **กรองตามประเภท**: เลือกประเภททรัพย์สิน
- **รีเซ็ตการกรอง**: เลือก "ทั้งหมด" เพื่อแสดงข้อมูลทั้งหมด

---

## 🗄️ โครงสร้างข้อมูล

### 📊 Property Data Model

```javascript
Property = {
    id: Number,              // รหัสทรัพย์สิน (Auto-generated)
    number: String,          // บ้านเลขที่ (เช่น "123/45")
    type: String,            // ประเภท ("single-house", "townhouse", "condo")
    owner: {                 // ข้อมูลเจ้าของ
        name: String,        // ชื่อเจ้าของ
        phone: String        // เบอร์โทรเจ้าของ
    },
    tenant: {                // ข้อมูลผู้เช่า
        name: String,        // ชื่อผู้เช่า (อาจเป็นค่าว่าง)
        phone: String        // เบอร์โทรผู้เช่า (อาจเป็นค่าว่าง)
    },
    status: String,          // สถานะ ("occupied", "vacant", "for-rent", "maintenance")
    rent: Number,            // ค่าเช่าต่อเดือน (0 ถ้าไม่มี)
    notes: String            // หมายเหตุ (อาจเป็นค่าว่าง)
}
```

### 🏷️ ประเภททรัพย์สิน (Property Types)

| Value | Display | Description |
|-------|---------|-------------|
| `single-house` | บ้านเดี่ยว | บ้านเดี่ยวแยกหลัง |
| `townhouse` | ทาวน์เฮาส์ | บ้านแถวเชื่อมต่อกัน |
| `condo` | คอนโดมิเนียม | ห้องชุดในอาคารสูง |

### 📈 สถานะทรัพย์สิน (Property Status)

| Value | Display | Color | Description |
|-------|---------|-------|-------------|
| `occupied` | มีผู้อยู่อาศัย | เขียว | มีคนอยู่อาศัยปัจจุบัน |
| `vacant` | ว่าง | แดง | ไม่มีผู้อยู่อาศัย |
| `for-rent` | ให้เช่า | น้ำเงิน | พร้อมให้เช่า |
| `maintenance` | ปรับปรุง | เหลือง | อยู่ระหว่างซ่อมแซม |

---

## 🔧 รายละเอียดทางเทคนิค

### 🏗️ สถาปัตยกรรมระบบ

#### Frontend Architecture:
- **HTML5**: โครงสร้างหน้าเว็บ
- **CSS3**: การจัดรูปแบบและ responsive design
- **Vanilla JavaScript**: ตmantik การทำงานและ DOM manipulation
- **Modal System**: ป๊อปอัพสำหรับการจัดการข้อมูล

#### Data Storage:
- **Client-side Storage**: เก็บข้อมูลใน JavaScript variables
- **Session Storage**: ข้อมูลหายเมื่อปิดเบราว์เซอร์
- **Future Enhancement**: เชื่อมต่อกับ Database

### 📁 โครงสร้างไฟล์

```
village_admin_dashboard.html
├── HTML Structure
│   ├── Navigation Menu
│   ├── Property Management Section
│   ├── Property Table
│   ├── Add/Edit Modal
│   └── Delete Confirmation Modal
├── CSS Styles
│   ├── Layout Styles
│   ├── Table Styles
│   ├── Modal Styles
│   ├── Form Styles
│   └── Responsive Design
└── JavaScript Functions
    ├── Data Management
    ├── CRUD Operations
    ├── Modal Controls
    ├── Search & Filter
    └── Event Handlers
```

### 🎨 CSS Classes และ Styling

#### Table Classes:
- `.property-table`: ตารางหลัก
- `.property-header`: หัวตาราง
- `.property-row`: แถวข้อมูล
- `.property-cell`: เซลล์ข้อมูล

#### Modal Classes:
- `.property-modal`: คอนเทนเนอร์ modal
- `.property-modal-content`: เนื้อหา modal
- `.property-modal-header`: หัว modal
- `.property-modal-body`: เนื้อหา modal
- `.property-modal-footer`: ท้าย modal

#### Form Classes:
- `.property-form-grid`: เลย์เอาต์ฟอร์ม
- `.property-form-group`: กลุ่มฟิลด์
- `.property-form-input`: ช่องกรอกข้อมูล
- `.property-form-select`: dropdown
- `.property-form-textarea`: ช่องข้อความยาว

#### Status Classes:
- `.status-badge`: ป้ายสถานะ
- `.status-badge.occupied`: สถานะมีผู้อยู่
- `.status-badge.vacant`: สถานะว่าง
- `.status-badge.for-rent`: สถานะให้เช่า
- `.status-badge.maintenance`: สถานะปรับปรุง

### ⚙️ JavaScript Functions

#### Core Functions:
```javascript
// Data Management
initializePropertyManagement()    // เริ่มต้นระบบ
renderNewPropertiesTable()       // แสดงตาราง
sortPropertiesByNumber()         // เรียงลำดับข้อมูล

// CRUD Operations
openAddPropertyModal()           // เปิด modal เพิ่ม
editNewProperty(id)             // เปิด modal แก้ไข
saveProperty()                  // บันทึกข้อมูล
deleteNewProperty(id)           // ลบข้อมูล
confirmDeleteProperty()         // ยืนยันการลบ

// Modal Controls
closePropertyModal()            // ปิด modal เพิ่ม/แก้ไข
closeDeletePropertyModal()      // ปิด modal ลบ

// Search & Filter
searchProperties()              // ค้นหาข้อมูล
filterByStatus()               // กรองตามสถานะ
filterByType()                 // กรองตามประเภท
```

#### Event Handlers:
- **Form Submission**: จัดการการส่งฟอร์ม
- **Button Clicks**: จัดการการคลิกปุ่ม
- **Input Changes**: จัดการการเปลี่ยนแปลงข้อมูล
- **Modal Events**: จัดการการเปิด/ปิด modal

### 🔒 Data Validation

#### Client-side Validation:
```javascript
// Required Fields
if (!propertyData.number || !propertyData.type || !propertyData.status) {
    alert('กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน');
    return;
}

// Duplicate Check
const existingProperty = properties.find(p => 
    p.number === propertyData.number && p.id !== currentEditPropertyId
);
if (existingProperty) {
    alert('บ้านเลขที่นี้มีอยู่ในระบบแล้ว');
    return;
}
```

#### HTML5 Validation:
- `required` attribute สำหรับฟิลด์จำเป็น
- `type="tel"` สำหรับหมายเลขโทรศัพท์
- `type="number"` สำหรับตัวเลข
- `pattern` attribute สำหรับรูปแบบข้อมูล

---

## 🛠️ การบำรุงรักษา

### 📊 การติดตามประสิทธิภาพ

#### Metrics ที่ควรติดตาม:
- **Response Time**: เวลาตอบสนองของระบบ
- **Error Rate**: อัตราการเกิดข้อผิดพลาด
- **User Engagement**: การใช้งานของผู้ใช้
- **Data Accuracy**: ความถูกต้องของข้อมูล

#### Performance Optimization:
- **Lazy Loading**: โหลดข้อมูลเมื่อจำเป็น
- **Caching**: เก็บข้อมูลใน cache
- **Minification**: บีบอัดไฟล์ CSS/JS
- **Image Optimization**: ปรับขนาดรูปภาพ

### 🔄 การอัพเดทระบบ

#### Version Control:
- ใช้ Git สำหรับควบคุมเวอร์ชัน
- สร้าง branch แยกสำหรับฟีเจอร์ใหม่
- ทำ code review ก่อน merge
- Tag version สำหรับ release

#### Backup Strategy:
- สำรองข้อมูลประจำวัน
- เก็บ backup หลายสำเนา
- ทดสอบการ restore เป็นประจำ
- มี disaster recovery plan

### 🐛 การแก้ไขปัญหา

#### Common Issues:

**1. Modal ไม่เปิด:**
```javascript
// ตรวจสอบ JavaScript errors ใน console
// ตรวจสอบ CSS display property
// ตรวจสอบ event listeners
```

**2. ข้อมูลไม่บันทึก:**
```javascript
// ตรวจสอบ form validation
// ตรวจสอบ required fields
// ตรวจสอบ data format
```

**3. ตารางไม่แสดงผล:**
```javascript
// ตรวจสอบ data array
// ตรวจสอบ render function
// ตรวจสอบ DOM elements
```

#### Debug Tools:
- **Browser DevTools**: ตรวจสอบ HTML/CSS/JS
- **Console Logging**: แสดงข้อมูล debug
- **Network Tab**: ตรวจสอบ API calls
- **Performance Tab**: วิเคราะห์ประสิทธิภาพ

### 📈 การพัฒนาต่อยอด

#### Future Enhancements:

**1. Database Integration:**
- เชื่อมต่อกับ MySQL/PostgreSQL
- API endpoints สำหรับ CRUD operations
- Real-time data synchronization

**2. Advanced Features:**
- File upload สำหรับรูปภาพทรัพย์สิน
- Document management
- Payment tracking
- Maintenance scheduling

**3. Reporting System:**
- Property utilization reports
- Financial reports
- Occupancy statistics
- Export to PDF/Excel

**4. Mobile App:**
- React Native app
- Push notifications
- Offline capabilities
- QR code scanning

**5. Integration:**
- LINE LIFF integration
- Payment gateway
- SMS notifications
- Email alerts

---

## 📞 การสนับสนุน

### 🆘 การขอความช่วยเหลือ

#### Technical Support:
- **Email**: support@smartvillage.com
- **Phone**: 02-xxx-xxxx
- **Line**: @smartvillage
- **Hours**: จันทร์-ศุกร์ 9:00-18:00

#### Documentation:
- **User Manual**: คู่มือการใช้งานผู้ใช้
- **API Documentation**: เอกสาร API
- **Video Tutorials**: วิดีโอสอนการใช้งาน
- **FAQ**: คำถามที่พบบ่อย

### 📚 แหล่งข้อมูลเพิ่มเติม

#### Learning Resources:
- **HTML/CSS**: MDN Web Docs
- **JavaScript**: JavaScript.info
- **Responsive Design**: CSS-Tricks
- **Accessibility**: WCAG Guidelines

#### Community:
- **GitHub**: Source code repository
- **Stack Overflow**: Q&A community
- **Discord**: Developer chat
- **Blog**: Technical articles

---

## 📄 ภาคผนวก

### 🔤 อภิธานศัพท์

| คำศัพท์ | ความหมาย |
|---------|-----------|
| CRUD | Create, Read, Update, Delete - การดำเนินการพื้นฐาน 4 ประการ |
| Modal | หน้าต่างป๊อปอัพที่แสดงเนื้อหาเพิ่มเติม |
| Responsive | การออกแบบที่ปรับตัวตามขนาดหน้าจอ |
| Validation | การตรวจสอบความถูกต้องของข้อมูล |
| DOM | Document Object Model - โครงสร้างเอกสาร HTML |

### 📋 Checklist การใช้งาน

#### ก่อนเริ่มใช้งาน:
- [ ] ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
- [ ] เปิดเบราว์เซอร์ที่รองรับ (Chrome, Firefox, Safari)
- [ ] เข้าสู่ระบบ Village Admin Dashboard
- [ ] ตรวจสอบสิทธิ์การเข้าถึง Property Management

#### การเพิ่มข้อมูลใหม่:
- [ ] คลิกปุ่ม "+ เพิ่มทรัพย์สินใหม่"
- [ ] กรอกบ้านเลขที่ (จำเป็น)
- [ ] เลือกประเภททรัพย์สิน (จำเป็น)
- [ ] เลือกสถานะ (จำเป็น)
- [ ] กรอกข้อมูลเพิ่มเติมตามต้องการ
- [ ] คลิก "บันทึก"
- [ ] ตรวจสอบข้อมูลในตาราง

#### การแก้ไขข้อมูล:
- [ ] ค้นหาทรัพย์สินที่ต้องการแก้ไข
- [ ] คลิกปุ่ม "แก้ไข"
- [ ] แก้ไขข้อมูลตามต้องการ
- [ ] คลิก "บันทึก"
- [ ] ตรวจสอบการเปลี่ยนแปลงในตาราง

---

**เอกสารนี้จัดทำขึ้นเพื่อให้ผู้ใช้งานและผู้พัฒนาเข้าใจการทำงานของ Property Management System อย่างครบถ้วน หากมีข้อสงสัยหรือต้องการความช่วยเหลือเพิ่มเติม กรุณาติดต่อทีมสนับสนุน**

---
*เอกสารเวอร์ชัน 1.0 | วันที่อัพเดท: 8 กรกฎาคม 2025 | Smart Village Management System*

