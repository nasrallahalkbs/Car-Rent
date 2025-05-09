/**
 * ملف JavaScript لإدارة مستكشف الأرشيف الإلكتروني
 */

// عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تفعيل FAB (زر الإضافة العائم)
    initFab();
    
    // تفعيل التبديل بين عرض الشبكة والقائمة
    initViewToggle();
    
    // تفعيل البحث داخل المحتوى
    initSearch();
});

/**
 * تهيئة زر الإضافة العائم
 */
function initFab() {
    const fabToggle = document.getElementById('fab-toggle');
    const fabMenu = document.getElementById('fab-menu');
    
    if (fabToggle && fabMenu) {
        fabToggle.addEventListener('click', function(event) {
            event.stopPropagation();
            fabMenu.classList.toggle('open');
        });
        
        // إغلاق القائمة عند النقر خارجها
        document.addEventListener('click', function() {
            fabMenu.classList.remove('open');
        });
        
        // منع إغلاق القائمة عند النقر داخلها
        fabMenu.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    }
}

/**
 * تهيئة التبديل بين طرق العرض
 */
function initViewToggle() {
    const gridViewBtn = document.getElementById('grid-view-btn');
    const listViewBtn = document.getElementById('list-view-btn');
    const filesGrid = document.querySelector('.files-grid');
    const filesTable = document.querySelector('.files-table');
    
    if (gridViewBtn && listViewBtn && filesGrid && filesTable) {
        gridViewBtn.addEventListener('click', function() {
            filesGrid.style.display = 'grid';
            filesTable.style.display = 'none';
            gridViewBtn.classList.add('active');
            listViewBtn.classList.remove('active');
        });
        
        listViewBtn.addEventListener('click', function() {
            filesGrid.style.display = 'none';
            filesTable.style.display = 'table';
            gridViewBtn.classList.remove('active');
            listViewBtn.classList.add('active');
        });
    }
}

/**
 * تهيئة وظيفة البحث
 */
function initSearch() {
    const contentSearch = document.getElementById('content-search');
    
    if (contentSearch) {
        contentSearch.addEventListener('input', function() {
            const searchText = this.value.toLowerCase();
            
            // البحث في الشبكة
            const gridItems = document.querySelectorAll('.folder-item-container, .file-item-container');
            
            gridItems.forEach(item => {
                const nameElement = item.querySelector('.folder-name, .file-name');
                if (nameElement) {
                    const name = nameElement.textContent.toLowerCase();
                    if (name.includes(searchText)) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                }
            });
            
            // البحث في القائمة
            const tableRows = document.querySelectorAll('.files-table tbody tr');
            
            tableRows.forEach(row => {
                const nameCell = row.querySelector('td:first-child span');
                if (nameCell) {
                    const name = nameCell.textContent.toLowerCase();
                    if (name.includes(searchText)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
        });
    }
}