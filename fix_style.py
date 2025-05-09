"""
إصلاح تنسيق جدول الحجوزات مباشرة
"""

import os
import time

def fix_css():
    """تطبيق التنسيق الصحيح مباشرة في ملف CSS"""
    css_path = "static/css/old-table.css"
    timestamp = int(time.time())
    
    css_content = "/* CACHE_BUSTER " + str(timestamp) + " */\n"
    css_content += """/* أنماط التصميم القديم للجدول */

/* تنسيق الأزرار الملونة كما في الصورة المرفقة */
.action-icons {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}
.action-icon {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: white !important;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}
.action-icon:hover {
    transform: scale(1.1);
    color: white !important;
    text-decoration: none;
}
.action-icon.red {
    background-color: #f44336;
}
.action-icon.blue {
    background-color: #3361ff;
}
.action-icon.yellow {
    background-color: #ffc107;
}
.action-icon.green {
    background-color: #4caf50;
}
.action-icon.purple {
    background-color: #9c27b0;
}

/* تنسيق شارات الحالة كما في الصورة المرفقة */
.status-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
    text-align: center;
}
.status-pending {
    background-color: #fff8e1;
    color: #ff9800;
}
.status-confirmed {
    background-color: #e8f5e9;
    color: #4caf50;
}
.status-completed {
    background-color: #e3f2fd;
    color: #2196f3;
}
.status-cancelled {
    background-color: #ffebee;
    color: #f44336;
}

/* تنسيق الجدول كما في الصورة المرفقة */
.reservation-table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 20px;
}

.reservation-table thead {
    background-color: #f0f5ff;
    border-bottom: 1px solid #e2e8f0;
}

.reservation-table th {
    padding: 12px 15px;
    text-align: center;
    font-weight: 600;
    color: #3361ff;
    border: none;
}

.reservation-table tr {
    border-bottom: 1px solid #eee;
}

.reservation-table td {
    padding: 12px 8px;
    text-align: center;
    vertical-align: middle;
}

/* تنسيق صف الأزرار */
.filter-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.filter-btn {
    background-color: #3361ff;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 15px;
    cursor: pointer;
    text-decoration: none;
}

.filter-btn:hover {
    background-color: #2851e3;
    color: white;
    text-decoration: none;
}

.search-box {
    position: relative;
}

.search-input {
    padding: 8px 15px 8px 40px;
    border: 1px solid #ddd;
    border-radius: 5px;
    min-width: 250px;
}

.search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #aaa;
}

/* إجراءات */
.action-btn {
  padding: 8px 15px;
  border-radius: 30px;
  display: inline-block;
  margin: 3px;
  font-weight: 500;
}

.btn-confirm {
  background-color: #0d9488;
  color: white;
  text-decoration: none;
}

.btn-pending {
  background-color: #6b7280;
  color: white;
  text-decoration: none;
}

/* السعر */
.price-display {
  color: #3b82f6;
  font-weight: bold;
  font-size: 1.15rem;
  direction: ltr;
}

/* المدة */
.duration-display {
  display: flex;
  align-items: center;
  justify-content: center;
}

.duration-day {
  background-color: #e6f2ff;
  color: #3b82f6;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 15px;
  font-size: 0.9rem;
  margin: 0 5px;
}

/* معلومات السيارة */
.car-info {
  display: flex;
  align-items: center;
  justify-content: center;
}

.car-info img {
  width: 50px;
  height: 35px;
  object-fit: cover;
  border-radius: 4px;
  margin-right: 10px;
}

[dir="rtl"] .car-info img {
  margin-right: 0;
  margin-left: 10px;
}

.car-details {
  text-align: left;
}

[dir="rtl"] .car-details {
  text-align: right;
}

.car-make-model {
  font-weight: 600;
  color: #334155;
  margin-bottom: 3px;
}

.car-year {
  font-size: 0.8rem;
  color: #64748b;
}

/* معرف الحجز */
.reservation-id {
  font-weight: 700;
  color: #3b82f6;
  text-decoration: none;
  font-size: 1.1rem;
}

/* تصميم متجاوب للشاشات الصغيرة */
@media (max-width: 767px) {
  .reservation-table thead {
    display: none;
  }
  
  .reservation-table, .reservation-table tbody, .reservation-table tr, .reservation-table td {
    display: block;
    width: 100%;
  }
  
  .reservation-table tr {
    margin-bottom: 20px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  }
  
  .reservation-table td {
    text-align: right;
    padding: 10px;
    position: relative;
    padding-left: 50%;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .reservation-table td:before {
    position: absolute;
    left: 10px;
    width: 45%;
    padding-right: 10px;
    white-space: nowrap;
    font-weight: 600;
    content: attr(data-label);
    text-align: left;
  }
  
  [dir="rtl"] .reservation-table td {
    text-align: left;
    padding-left: 10px;
    padding-right: 50%;
  }
  
  [dir="rtl"] .reservation-table td:before {
    left: auto;
    right: 10px;
    text-align: right;
    padding-right: 0;
    padding-left: 10px;
  }
  
  .car-info {
    justify-content: flex-end;
  }
  
  [dir="rtl"] .car-info {
    justify-content: flex-start;
  }
  
  .action-icons {
    justify-content: flex-start;
  }
  
  [dir="rtl"] .action-icons {
    justify-content: flex-end;
  }
}
"""
    
    with open(css_path, "w", encoding="utf-8") as file:
        file.write(css_content)
    
    print(f"✅ تم تحديث ملف CSS بالكامل")

def touch_files():
    """لمس ملفات المشروع الرئيسية لإعادة تحميل التطبيق"""
    files_to_touch = [
        "main.py",
        "templates/admin/reservations_django.html",
    ]
    
    for file_path in files_to_touch:
        if os.path.exists(file_path):
            with open(file_path, "a") as file:
                file.write(f"\n<!-- UPDATED: {int(time.time())} -->")
            print(f"✅ تم تحديث ملف {file_path}")
    
    print("✅ تم تنشيط إعادة تحميل التطبيق")

def main():
    """الدالة الرئيسية"""
    print("🔄 بدء عملية تحديث تنسيق جدول الحجوزات...")
    
    fix_css()
    touch_files()
    
    print("✅ تم الانتهاء من تحديث تنسيق جدول الحجوزات")
    print("ℹ️ قم بتحديث الصفحة بالضغط على Ctrl+F5 لمسح ذاكرة التخزين المؤقت")

if __name__ == "__main__":
    main()