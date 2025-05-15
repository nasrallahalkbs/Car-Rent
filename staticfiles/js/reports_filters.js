document.addEventListener('DOMContentLoaded', function() {
    // التبديل بين التبويبات
    var ribbonTabs = document.querySelectorAll('.ribbon-tab');
    var tabPanes = document.querySelectorAll('.tab-pane');

    for (var i = 0; i < ribbonTabs.length; i++) {
        ribbonTabs[i].addEventListener('click', function() {
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
            document.getElementById(tabId + '-tab').style.display = 'block';
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
    
    // تحديث مربع الاختيار الرئيسي
    for (var i = 0; i < rowCheckboxes.length; i++) {
        rowCheckboxes[i].addEventListener('change', function() {
            var allChecked = true;
            var someChecked = false;
            
            for (var j = 0; j < rowCheckboxes.length; j++) {
                if (rowCheckboxes[j].checked) {
                    someChecked = true;
                } else {
                    allChecked = false;
                }
            }
            
            if (mainCheckbox) {
                mainCheckbox.checked = allChecked;
                mainCheckbox.indeterminate = someChecked && !allChecked;
            }
        });
    }

    // منطق فلاتر الأعمدة
    var filterIcons = document.querySelectorAll('.filter-icon');
    var filterPopupsContainer = document.getElementById('filter-popups-container');
    var activeFilterPopup = null;
    
    // الحصول على صناديق التصفية
    var textFilter = document.getElementById('text-filter');
    var dateFilter = document.getElementById('date-filter');
    var selectFilter = document.getElementById('select-filter');
    
    // التأكد من وجود صناديق التصفية
    if (!textFilter || !dateFilter || !selectFilter) {
        console.error('صناديق التصفية غير موجودة في الصفحة');
    }
    
    // إغلاق صندوق الفلتر
    function closeFilterPopup() {
        if (activeFilterPopup) {
            activeFilterPopup.classList.remove('show');
            activeFilterPopup.style.display = 'none';
            activeFilterPopup = null;
        }
    }
    
    // إغلاق أي صندوق فلتر مفتوح عند النقر في مكان آخر
    document.addEventListener('click', function(event) {
        if (activeFilterPopup && !event.target.closest('.column-filter-popup') && 
            !event.target.closest('.filter-icon')) {
            closeFilterPopup();
        }
    });

    // تفعيل أيقونات الفلتر
    for (var i = 0; i < filterIcons.length; i++) {
        filterIcons[i].addEventListener('click', function(event) {
            event.stopPropagation();
            
            // إغلاق أي صندوق فلتر مفتوح
            if (activeFilterPopup) {
                closeFilterPopup();
            }
            
            // الحصول على معلومات العمود
            var columnHeader = this.closest('.filterable');
            var columnName = columnHeader.getAttribute('data-column');
            var columnTitle = columnHeader.querySelector('span').textContent;
            
            // تحديد نوع الفلتر المناسب
            var filterType = 'text';
            if (columnName === 'reservation_date' || columnName === 'pickup_date' || columnName === 'return_date') {
                filterType = 'date';
            } else if (columnName === 'status' || columnName === 'admin') {
                filterType = 'select';
            }
            
            // تحديد الفلتر المناسب
            var filterPopup;
            if (filterType === 'date') {
                filterPopup = dateFilter;
            } else if (filterType === 'select') {
                filterPopup = selectFilter;
            } else {
                filterPopup = textFilter;
            }
            
            if (!filterPopup) {
                console.error('الفلتر غير موجود: ' + filterType);
                return;
            }
            
            // تعيين العنوان
            var titleElement = filterPopup.querySelector('.filter-title');
            if (titleElement) {
                titleElement.textContent = 'فلترة بحسب ' + columnTitle;
            }
            
            // تهيئة المحتوى حسب نوع الفلتر
            if (filterType === 'select') {
                var optionsList = filterPopup.querySelector('.filter-options-list');
                if (optionsList) {
                    // تفريغ قائمة الخيارات
                    optionsList.innerHTML = '';
                    
                    // إضافة الخيارات المناسبة
                    var options = [];
                    if (columnName === 'status') {
                        options = [
                            { value: 'confirmed', label: 'مؤكد' },
                            { value: 'pending', label: 'قيد الانتظار' },
                            { value: 'completed', label: 'مكتمل' },
                            { value: 'cancelled', label: 'ملغي' }
                        ];
                    } else if (columnName === 'admin') {
                        // هنا يمكن إضافة خيارات المسؤولين
                        options = [
                            { value: 'admin1', label: 'المسؤول 1' },
                            { value: 'admin2', label: 'المسؤول 2' }
                        ];
                    }
                    
                    // إضافة الخيارات إلى القائمة
                    for (var j = 0; j < options.length; j++) {
                        var option = options[j];
                        var optionElement = document.createElement('div');
                        optionElement.className = 'filter-option';
                        optionElement.textContent = option.label;
                        optionElement.setAttribute('data-value', option.value);
                        optionsList.appendChild(optionElement);
                        
                        // تفعيل الخيار
                        optionElement.addEventListener('click', function() {
                            this.classList.toggle('selected');
                        });
                    }
                }
            }
            
            // الاحتفاظ بمرجع للفلتر النشط
            activeFilterPopup = filterPopup;
            
            // تحديد موقع الصندوق المنبثق
            var iconRect = this.getBoundingClientRect();
            activeFilterPopup.style.top = (iconRect.bottom + window.scrollY) + 'px';
            
            // تحديد الموقع الأفقي بناءً على اتجاه النص
            var isRtl = document.documentElement.dir === 'rtl';
            if (isRtl) {
                activeFilterPopup.style.right = (window.innerWidth - iconRect.right) + 'px';
                activeFilterPopup.style.left = 'auto';
            } else {
                activeFilterPopup.style.left = iconRect.left + 'px';
                activeFilterPopup.style.right = 'auto';
            }
            
            // التأكد من أن الفلتر سيظهر بالكامل في الشاشة
            var filterWidth = 250; // العرض التقريبي للفلتر
            if ((isRtl && (window.innerWidth - iconRect.right < filterWidth)) ||
                (!isRtl && (iconRect.left + filterWidth > window.innerWidth))) {
                // تعديل الموقع إذا كان سيخرج خارج حدود الشاشة
                if (isRtl) {
                    activeFilterPopup.style.right = '10px';
                } else {
                    activeFilterPopup.style.left = (window.innerWidth - filterWidth - 10) + 'px';
                }
            }
            
            // إظهار الصندوق المنبثق
            activeFilterPopup.style.display = 'block';
            setTimeout(function() {
                activeFilterPopup.classList.add('show');
            }, 10);
            
            // إضافة حدث النقر على زر الإغلاق
            var closeBtn = activeFilterPopup.querySelector('.close-filter');
            if (closeBtn) {
                closeBtn.onclick = closeFilterPopup;
            }
            
            // إضافة أحداث الأزرار
            var resetBtn = activeFilterPopup.querySelector('.reset-filter');
            if (resetBtn) {
                resetBtn.onclick = closeFilterPopup;
            }
            
            var applyBtn = activeFilterPopup.querySelector('.apply-filter');
            if (applyBtn) {
                applyBtn.onclick = function() {
                    // هنا يمكن إضافة منطق تطبيق الفلتر
                    closeFilterPopup();
                };
            }
        });
    }
});