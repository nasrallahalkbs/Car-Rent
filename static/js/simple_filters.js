// سكريبت مبسط لإظهار صناديق التصفية
document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل سكريبت التصفية البسيط");
    
    // التبديل بين التبويبات
    var ribbonTabs = document.querySelectorAll('.ribbon-tab');
    var tabPanes = document.querySelectorAll('.tab-pane');
    
    console.log("عدد التبويبات:", ribbonTabs.length);
    console.log("عدد محتويات التبويبات:", tabPanes.length);
    
    for (var i = 0; i < ribbonTabs.length; i++) {
        ribbonTabs[i].addEventListener('click', function(event) {
            event.preventDefault(); // منع السلوك الافتراضي للرابط
            
            console.log("تم النقر على التبويب:", this.getAttribute('data-tab'));
            
            // إزالة الفئة النشطة من جميع التبويبات
            for (var j = 0; j < ribbonTabs.length; j++) {
                ribbonTabs[j].classList.remove('active');
            }
            
            // إضافة الفئة النشطة للتبويب المحدد
            this.classList.add('active');
            
            // إخفاء جميع المحتويات
            for (var k = 0; k < tabPanes.length; k++) {
                tabPanes[k].style.display = 'none';
            }
            
            // عرض المحتوى المناسب
            var tabId = this.getAttribute('data-tab');
            var targetPane = document.getElementById(tabId + '-tab');
            
            if (targetPane) {
                console.log("عرض تبويب:", tabId + '-tab');
                targetPane.style.display = 'block';
            } else {
                console.error("لم يتم العثور على تبويب بهوية:", tabId + '-tab');
            }
        });
    }
    
    // التحقق من مربعات الاختيار
    var mainCheckbox = document.getElementById('select-all');
    var rowCheckboxes = document.querySelectorAll('.row-checkbox');
    
    if (mainCheckbox) {
        mainCheckbox.addEventListener('change', function() {
            for (var i = 0; i < rowCheckboxes.length; i++) {
                rowCheckboxes[i].checked = this.checked;
            }
        });
    }
    
    // منطق فلاتر الأعمدة
    // الحصول على عناصر التصفية وتفاعلاتها
    var filterIcons = document.querySelectorAll('.filter-icon');
    console.log("عدد أيقونات التصفية:", filterIcons.length);
    
    // تعريف المتغيرات العالمية للتصفية
    var activeFilterPopup = null;
    
    // إغلاق أي صندوق تصفية مفتوح
    function closeFilterPopup() {
        if (activeFilterPopup) {
            console.log("إغلاق نافذة التصفية");
            activeFilterPopup.style.display = 'none';
            activeFilterPopup = null;
        }
    }
    
    // إضافة التفاعل مع أيقونات التصفية
    for (var i = 0; i < filterIcons.length; i++) {
        filterIcons[i].addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            console.log("تم النقر على أيقونة التصفية");
            
            // الحصول على معلومات العمود
            var columnHeader = this.closest('.filterable');
            var columnName = columnHeader.getAttribute('data-column');
            var columnTitle = columnHeader.querySelector('span').textContent;
            console.log("اسم العمود:", columnName, "| العنوان:", columnTitle);
            
            // إغلاق نافذة التصفية النشطة (إن وجدت)
            if (activeFilterPopup) {
                closeFilterPopup();
                
                // إذا كنا ننقر على نفس الأيقونة، نخرج
                if (activeFilterPopup.getAttribute('data-column') === columnName) {
                    return;
                }
            }
            
            // إنشاء عنصر نافذة التصفية الجديدة
            var filterPopup = document.createElement('div');
            filterPopup.className = 'column-filter-popup';
            filterPopup.setAttribute('data-column', columnName);
            filterPopup.style.position = 'absolute';
            filterPopup.style.zIndex = '1000';
            
            // إنشاء محتوى النافذة
            var filterContent = '';
            
            // العنوان وزر الإغلاق
            filterContent += '<div class="filter-header">';
            filterContent += '<div class="filter-title">فلترة بحسب ' + columnTitle + '</div>';
            filterContent += '<i class="fas fa-times close-filter"></i>';
            filterContent += '</div>';
            
            // محتوى النافذة حسب نوع العمود
            if (columnName === 'reservation_date' || columnName === 'pickup_date' || columnName === 'return_date') {
                // نافذة تصفية التاريخ
                filterContent += '<div class="date-filter-form">';
                filterContent += '<label>من</label>';
                filterContent += '<input type="date" class="filter-input date-from">';
                filterContent += '<label>إلى</label>';
                filterContent += '<input type="date" class="filter-input date-to">';
                filterContent += '</div>';
            } else if (columnName === 'status') {
                // نافذة تصفية الحالة
                filterContent += '<input type="text" class="filter-input" placeholder="بحث...">';
                filterContent += '<div class="filter-options-list">';
                filterContent += '<div class="filter-option" data-value="confirmed">مؤكد</div>';
                filterContent += '<div class="filter-option" data-value="pending">قيد الانتظار</div>';
                filterContent += '<div class="filter-option" data-value="completed">مكتمل</div>';
                filterContent += '<div class="filter-option" data-value="cancelled">ملغي</div>';
                filterContent += '</div>';
            } else if (columnName === 'admin') {
                // نافذة تصفية المسؤول
                filterContent += '<input type="text" class="filter-input" placeholder="بحث...">';
                filterContent += '<div class="filter-options-list">';
                filterContent += '<div class="filter-option" data-value="admin1">المسؤول 1</div>';
                filterContent += '<div class="filter-option" data-value="admin2">المسؤول 2</div>';
                filterContent += '</div>';
            } else {
                // نافذة تصفية نصية عامة
                filterContent += '<input type="text" class="filter-input" placeholder="بحث...">';
                filterContent += '<div class="filter-options-list"></div>';
            }
            
            // أزرار الإجراءات
            filterContent += '<div class="filter-actions">';
            filterContent += '<button class="filter-btn reset-filter">إعادة تعيين</button>';
            filterContent += '<button class="filter-btn apply-filter">تطبيق</button>';
            filterContent += '</div>';
            
            // وضع المحتوى في العنصر
            filterPopup.innerHTML = filterContent;
            
            // إضافة النافذة إلى المستند
            document.body.appendChild(filterPopup);
            
            // تحديد موقع النافذة
            var iconRect = this.getBoundingClientRect();
            filterPopup.style.top = (iconRect.bottom + window.scrollY) + 'px';
            
            // تحديد الموقع الأفقي حسب اتجاه اللغة
            var isRtl = document.documentElement.dir === 'rtl';
            if (isRtl) {
                filterPopup.style.right = (window.innerWidth - iconRect.right) + 'px';
                filterPopup.style.left = 'auto';
            } else {
                filterPopup.style.left = iconRect.left + 'px';
                filterPopup.style.right = 'auto';
            }
            
            // إظهار النافذة
            filterPopup.style.display = 'block';
            
            // تعيين النافذة الحالية كنافذة نشطة
            activeFilterPopup = filterPopup;
            
            // إضافة التفاعلات
            // زر الإغلاق
            var closeBtn = filterPopup.querySelector('.close-filter');
            if (closeBtn) {
                closeBtn.addEventListener('click', closeFilterPopup);
            }
            
            // زر إعادة التعيين
            var resetBtn = filterPopup.querySelector('.reset-filter');
            if (resetBtn) {
                resetBtn.addEventListener('click', closeFilterPopup);
            }
            
            // زر التطبيق
            var applyBtn = filterPopup.querySelector('.apply-filter');
            if (applyBtn) {
                applyBtn.addEventListener('click', function() {
                    // هنا يمكن إضافة منطق تطبيق التصفية
                    closeFilterPopup();
                });
            }
            
            // خيارات التصفية
            var options = filterPopup.querySelectorAll('.filter-option');
            for (var j = 0; j < options.length; j++) {
                options[j].addEventListener('click', function() {
                    this.classList.toggle('selected');
                });
            }
        });
    }
    
    // إغلاق نافذة التصفية عند النقر في أي مكان آخر
    document.addEventListener('click', function(event) {
        if (activeFilterPopup && !event.target.closest('.column-filter-popup') && 
            !event.target.closest('.filter-icon')) {
            closeFilterPopup();
        }
    });
});