import os
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder

def create_system_folders():
    """إنشاء المجلدات النظامية للأرشيف الإلكتروني"""
    print("بدء إنشاء المجلدات النظامية للأرشيف...")
    
    # المجلدات الرئيسية
    contracts_folder = ArchiveFolder.get_or_create_system_folder('العقود', 'عقود')
    print(f"- تم إنشاء مجلد {contracts_folder.name}")
    
    receipts_folder = ArchiveFolder.get_or_create_system_folder('الإيصالات', 'إيصالات')
    print(f"- تم إنشاء مجلد {receipts_folder.name}")
    
    official_docs_folder = ArchiveFolder.get_or_create_system_folder('المستندات الرسمية', 'مستندات رسمية')
    print(f"- تم إنشاء مجلد {official_docs_folder.name}")
    
    custody_folder = ArchiveFolder.get_or_create_system_folder('مستندات العهد', 'عهد')
    print(f"- تم إنشاء مجلد {custody_folder.name}")
    
    # المجلدات الفرعية للعقود
    rental_contracts = ArchiveFolder.get_or_create_system_folder('عقود الإيجار', 'عقود', contracts_folder)
    print(f"  - تم إنشاء مجلد {rental_contracts.name}")
    
    employee_contracts = ArchiveFolder.get_or_create_system_folder('عقود الموظفين', 'عقود', contracts_folder)
    print(f"  - تم إنشاء مجلد {employee_contracts.name}")
    
    # المجلدات الفرعية للإيصالات
    payment_receipts = ArchiveFolder.get_or_create_system_folder('إيصالات الدفع', 'إيصالات', receipts_folder)
    print(f"  - تم إنشاء مجلد {payment_receipts.name}")
    
    delivery_receipts = ArchiveFolder.get_or_create_system_folder('إيصالات التسليم', 'إيصالات', receipts_folder)
    print(f"  - تم إنشاء مجلد {delivery_receipts.name}")
    
    # المجلدات الفرعية للمستندات الرسمية
    car_docs = ArchiveFolder.get_or_create_system_folder('مستندات السيارات', 'مستندات رسمية', official_docs_folder)
    print(f"  - تم إنشاء مجلد {car_docs.name}")
    
    licenses = ArchiveFolder.get_or_create_system_folder('التراخيص', 'مستندات رسمية', official_docs_folder)
    print(f"  - تم إنشاء مجلد {licenses.name}")
    
    # المجلدات الفرعية للعهد
    car_custody = ArchiveFolder.get_or_create_system_folder('عهد السيارات', 'عهد', custody_folder)
    print(f"  - تم إنشاء مجلد {car_custody.name}")
    
    equipment_custody = ArchiveFolder.get_or_create_system_folder('عهد المعدات', 'عهد', custody_folder)
    print(f"  - تم إنشاء مجلد {equipment_custody.name}")
    
    print("تم إنشاء المجلدات النظامية بنجاح!")

if __name__ == "__main__":
    create_system_folders()