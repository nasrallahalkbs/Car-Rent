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
    
    // إغلاق صندوق الفلتر
    function closeFilterPopup() {
        if (activeFilterPopup) {
            activeFilterPopup.classList.remove('show');
            setTimeout(function() {
                filterPopupsContainer.innerHTML = '';
                activeFilterPopup = null;
            }, 200);
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
            
            // إنشاء القالب المناسب بناءً على نوع العمود
            var templateId = 'text-filter-template';
            if (columnName === 'reservation_date' || columnName === 'pickup_date' || columnName === 'return_date') {
                templateId = 'date-filter-template';
            } else if (columnName === 'status' || columnName === 'admin') {
                templateId = 'select-filter-template';
            }
            
            var template = document.getElementById(templateId);
            if (!template) {
                console.error('Template not found: ' + templateId);
                return;
            }
            
            // استنساخ القالب
            var filterPopupContent = template.content.cloneNode(true);
            
            // تعيين العنوان
            var titleElement = filterPopupContent.querySelector('.filter-title');
            if (titleElement) {
                titleElement.textContent = 'فلترة بحسب ' + columnTitle;
            }
            
            // إذا كان النوع هو قائمة اختيارات
            if (columnName === 'status') {
                var optionsList = filterPopupContent.querySelector('.filter-options-list');
                if (optionsList) {
                    var options = [
                        { value: 'confirmed', label: 'مؤكد' },
                        { value: 'pending', label: 'قيد الانتظار' },
                        { value: 'completed', label: 'مكتمل' },
                        { value: 'cancelled', label: 'ملغي' }
                    ];
                    
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
            
            // إضافة الصندوق المنبثق إلى المستند
            filterPopupsContainer.innerHTML = '';
            filterPopupsContainer.appendChild(filterPopupContent);
            
            // الحصول على مرجع للصندوق المنبثق بعد إضافته
            activeFilterPopup = filterPopupsContainer.querySelector('.column-filter-popup');
            
            // تحديد موقع الصندوق المنبثق
            var iconRect = this.getBoundingClientRect();
            activeFilterPopup.style.top = (iconRect.bottom + window.scrollY) + 'px';
            
            // تحديد الموقع الأفقي بناءً على اتجاه النص
            var isRtl = document.documentElement.dir === 'rtl';
            if (isRtl) {
                activeFilterPopup.style.right = (window.innerWidth - iconRect.right) + 'px';
            } else {
                activeFilterPopup.style.left = iconRect.left + 'px';
            }
            
            // إظهار الصندوق المنبثق
            activeFilterPopup.classList.add('show');
            
            // إضافة حدث النقر على زر الإغلاق
            var closeBtn = activeFilterPopup.querySelector('.close-filter');
            if (closeBtn) {
                closeBtn.addEventListener('click', closeFilterPopup);
            }
            
            // إضافة أحداث الأزرار
            var resetBtn = activeFilterPopup.querySelector('.reset-filter');
            if (resetBtn) {
                resetBtn.addEventListener('click', closeFilterPopup);
            }
            
            var applyBtn = activeFilterPopup.querySelector('.apply-filter');
            if (applyBtn) {
                applyBtn.addEventListener('click', closeFilterPopup);
            }
        });
    }
});