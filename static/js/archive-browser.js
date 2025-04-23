/**
 * مكتبة متكاملة لتصفح الأرشيف بشكل تفاعلي وعملي
 */

// بيانات المجلدات والملفات
const archiveData = {
    folders: {
        'root': {
            id: 'root',
            name: 'الرئيسية',
            parentId: null,
            children: ['folder1', 'folder2', 'folder3', 'folder4', 'folder5']
        },
        'folder1': {
            id: 'folder1',
            name: 'رسوم (1)',
            parentId: 'root',
            children: []
        },
        'folder2': {
            id: 'folder2',
            name: 'حضور (2)',
            parentId: 'root',
            children: []
        },
        'folder3': {
            id: 'folder3',
            name: 'حسابات (3)',
            parentId: 'root',
            children: []
        },
        'folder4': {
            id: 'folder4',
            name: 'محفوظات (4)',
            parentId: 'root', 
            children: []
        },
        'folder5': {
            id: 'folder5',
            name: 'توكيلات (5)',
            parentId: 'root',
            children: []
        }
    },
    
    files: {
        'folder1': [
            { name: 'رسم_بياني_1.pdf', type: 'pdf', size: '854 KB', date: '21/04/2025' },
            { name: 'رسم_بياني_2.pdf', type: 'pdf', size: '1.1 MB', date: '21/04/2025' }
        ],
        'folder2': [
            { name: 'سجل_الحضور_ابريل.xlsx', type: 'xls', size: '655 KB', date: '19/04/2025' },
            { name: 'سجل_الحضور_مارس.xlsx', type: 'xls', size: '578 KB', date: '01/04/2025' },
            { name: 'تقرير_الحضور.docx', type: 'doc', size: '325 KB', date: '20/04/2025' }
        ],
        'folder3': [
            { name: 'ميزانية_2025.xlsx', type: 'xls', size: '982 KB', date: '15/04/2025' },
            { name: 'تقرير_مالي_سنوي.pdf', type: 'pdf', size: '1.5 MB', date: '18/04/2025' },
            { name: 'فواتير_مارس.pdf', type: 'pdf', size: '750 KB', date: '10/04/2025' }
        ],
        'folder4': [
            { name: 'أرشيف_2024.zip', type: 'zip', size: '15.7 MB', date: '05/01/2025' },
            { name: 'سجلات_قديمة.pdf', type: 'pdf', size: '3.2 MB', date: '12/02/2025' }
        ],
        'folder5': [
            { name: 'نموذج_توكيل_رسمي.docx', type: 'doc', size: '245 KB', date: '20/04/2025' },
            { name: 'توكيل_محمد_احمد.pdf', type: 'pdf', size: '508 KB', date: '19/04/2025' },
            { name: 'توكيل_خالد_محمود.pdf', type: 'pdf', size: '512 KB', date: '18/04/2025' },
            { name: 'توكيل_عمر_سعيد.pdf', type: 'pdf', size: '495 KB', date: '17/04/2025' }
        ],
        'root': [
            { name: 'دليل_استخدام_الأرشيف.pdf', type: 'pdf', size: '1.2 MB', date: '22/04/2025' }
        ]
    }
};

// العناصر الأساسية في واجهة الأرشيف
let currentFolder = 'root';
let folderHistory = ['root'];
let historyPosition = 0;

// بمجرد تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل صفحة الأرشيف والبدء في التهيئة');
    
    // تهيئة عناصر واجهة المستخدم
    initializeArchiveUI();
    
    // عرض محتويات المجلد الرئيسي
    displayFolderContents('root');
});

// تهيئة واجهة المستخدم للأرشيف
function initializeArchiveUI() {
    console.log('تهيئة واجهة الأرشيف');
    
    // التحقق من وجود عناصر واجهة المستخدم الضرورية
    const archiveContainer = document.getElementById('archive-container');
    
    if (!archiveContainer) {
        console.error('لم يتم العثور على حاوية الأرشيف!');
        // إنشاء حاوية الأرشيف إذا لم تكن موجودة
        createArchiveUI();
    }
    
    // إضافة أحداث النقر للأزرار
    attachButtonEvents();
}

// إنشاء واجهة المستخدم للأرشيف
function createArchiveUI() {
    console.log('إنشاء واجهة المستخدم للأرشيف');
    
    // إنشاء الحاوية الرئيسية
    const mainContent = document.querySelector('.container-fluid') || document.body;
    
    const archiveContainer = document.createElement('div');
    archiveContainer.id = 'archive-container';
    archiveContainer.className = 'archive-container mt-3';
    
    // إنشاء شريط التنقل
    const navBar = document.createElement('div');
    navBar.className = 'archive-navbar p-2 mb-3 bg-light rounded d-flex align-items-center';
    navBar.innerHTML = `
        <button id="back-btn" class="btn btn-sm btn-outline-secondary me-2">
            <i class="fas fa-arrow-right"></i>
        </button>
        <button id="forward-btn" class="btn btn-sm btn-outline-secondary me-2">
            <i class="fas fa-arrow-left"></i>
        </button>
        <button id="up-btn" class="btn btn-sm btn-outline-secondary me-2">
            <i class="fas fa-arrow-up"></i>
        </button>
        <button id="home-btn" class="btn btn-sm btn-outline-primary me-2">
            <i class="fas fa-home"></i>
        </button>
        <div class="archive-path-container flex-grow-1 ms-3 p-2 bg-white rounded">
            <span id="current-path">الرئيسية</span>
        </div>
    `;
    
    // إنشاء عنوان المجلد الحالي
    const folderTitle = document.createElement('div');
    folderTitle.className = 'folder-title mb-3';
    folderTitle.innerHTML = `<h4 id="folder-name">الرئيسية</h4>`;
    
    // إنشاء مساحة لعرض محتوى المجلد
    const folderContent = document.createElement('div');
    folderContent.id = 'folder-content';
    folderContent.className = 'folder-content d-flex flex-wrap gap-4';
    
    // ترتيب العناصر
    archiveContainer.appendChild(navBar);
    archiveContainer.appendChild(folderTitle);
    archiveContainer.appendChild(folderContent);
    
    // إضافة نمط CSS
    addArchiveStyles();
    
    // إضافة الحاوية للصفحة
    if (mainContent) {
        mainContent.appendChild(archiveContainer);
    } else {
        document.body.appendChild(archiveContainer);
    }
}

// إضافة أنماط CSS للأرشيف
function addArchiveStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .archive-container {
            margin-bottom: 30px;
        }
        
        .folder-content {
            min-height: 300px;
        }
        
        .folder-item, .file-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 120px;
            height: 130px;
            padding: 15px 10px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
        }
        
        .folder-item:hover, .file-item:hover {
            background-color: #f8f9fa;
            border-color: #dee2e6;
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .folder-item:active, .file-item:active {
            transform: translateY(0);
        }
        
        .folder-icon {
            font-size: 40px;
            color: #ffc107;
            margin-bottom: 10px;
        }
        
        .file-icon {
            font-size: 40px;
            margin-bottom: 10px;
        }
        
        .file-icon.pdf {
            color: #dc3545;
        }
        
        .file-icon.doc {
            color: #0d6efd;
        }
        
        .file-icon.xls {
            color: #198754;
        }
        
        .file-icon.zip {
            color: #fd7e14;
        }
        
        .folder-name, .file-name {
            text-align: center;
            font-size: 14px;
        }
        
        .archive-navbar button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        #current-path {
            font-weight: 500;
        }
    `;
    
    document.head.appendChild(style);
}

// إرفاق أحداث النقر بأزرار التنقل
function attachButtonEvents() {
    console.log('إضافة أحداث النقر للأزرار');
    
    // تأجيل إضافة الأحداث للتأكد من وجود العناصر
    setTimeout(function() {
        // زر العودة للخلف
        const backBtn = document.getElementById('back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', navigateBack);
        }
        
        // زر الانتقال للأمام
        const forwardBtn = document.getElementById('forward-btn');
        if (forwardBtn) {
            forwardBtn.addEventListener('click', navigateForward);
        }
        
        // زر الانتقال للأعلى
        const upBtn = document.getElementById('up-btn');
        if (upBtn) {
            upBtn.addEventListener('click', navigateUp);
        }
        
        // زر العودة للرئيسية
        const homeBtn = document.getElementById('home-btn');
        if (homeBtn) {
            homeBtn.addEventListener('click', navigateHome);
        }
        
        // تحديث حالة الأزرار
        updateButtonStates();
    }, 500);
}

// عرض محتويات المجلد
function displayFolderContents(folderId) {
    console.log('عرض محتويات المجلد:', folderId);
    
    // تحديث المجلد الحالي
    currentFolder = folderId;
    
    // الحصول على بيانات المجلد
    const folder = archiveData.folders[folderId];
    if (!folder) {
        console.error('لم يتم العثور على المجلد:', folderId);
        return;
    }
    
    // تحديث عنوان المجلد
    const folderNameElement = document.getElementById('folder-name');
    if (folderNameElement) {
        folderNameElement.textContent = folder.name;
    }
    
    // تحديث مسار المجلد
    updatePath(folderId);
    
    // تحديث حالة أزرار التنقل
    updateButtonStates();
    
    // الحصول على عنصر محتوى المجلد
    const folderContentElement = document.getElementById('folder-content');
    if (!folderContentElement) {
        console.error('لم يتم العثور على عنصر محتوى المجلد!');
        return;
    }
    
    // مسح المحتوى الحالي
    folderContentElement.innerHTML = '';
    
    // إضافة المجلدات الفرعية
    let hasContent = false;
    
    if (folder.children && folder.children.length > 0) {
        hasContent = true;
        folder.children.forEach(childId => {
            const childFolder = archiveData.folders[childId];
            if (childFolder) {
                const folderElement = createFolderElement(childFolder);
                folderContentElement.appendChild(folderElement);
            }
        });
    }
    
    // إضافة الملفات
    const files = archiveData.files[folderId];
    if (files && files.length > 0) {
        hasContent = true;
        files.forEach(file => {
            const fileElement = createFileElement(file);
            folderContentElement.appendChild(fileElement);
        });
    }
    
    // عرض رسالة إذا كان المجلد فارغا
    if (!hasContent) {
        folderContentElement.innerHTML = `
            <div class="w-100 text-center py-5">
                <i class="fas fa-folder-open text-muted" style="font-size: 60px;"></i>
                <h5 class="mt-3 text-muted">هذا المجلد فارغ</h5>
            </div>
        `;
    }
}

// إنشاء عنصر مجلد
function createFolderElement(folder) {
    const folderElement = document.createElement('div');
    folderElement.className = 'folder-item';
    folderElement.setAttribute('data-id', folder.id);
    folderElement.innerHTML = `
        <div class="folder-icon">
            <i class="fas fa-folder"></i>
        </div>
        <div class="folder-name">${folder.name}</div>
    `;
    
    // إضافة حدث النقر
    folderElement.addEventListener('click', function() {
        navigateToFolder(folder.id);
    });
    
    return folderElement;
}

// إنشاء عنصر ملف
function createFileElement(file) {
    // تحديد الأيقونة بناء على نوع الملف
    let fileIconClass = 'fa-file';
    let fileColorClass = '';
    
    switch(file.type) {
        case 'pdf':
            fileIconClass = 'fa-file-pdf';
            fileColorClass = 'pdf';
            break;
        case 'doc':
            fileIconClass = 'fa-file-word';
            fileColorClass = 'doc';
            break;
        case 'xls':
            fileIconClass = 'fa-file-excel';
            fileColorClass = 'xls';
            break;
        case 'zip':
            fileIconClass = 'fa-file-archive';
            fileColorClass = 'zip';
            break;
    }
    
    const fileElement = document.createElement('div');
    fileElement.className = 'file-item';
    fileElement.innerHTML = `
        <div class="file-icon ${fileColorClass}">
            <i class="fas ${fileIconClass}"></i>
        </div>
        <div class="file-name">${file.name}</div>
    `;
    
    // إضافة حدث النقر
    fileElement.addEventListener('click', function() {
        alert(`تم النقر على الملف: ${file.name}`);
    });
    
    return fileElement;
}

// تحديث مسار المجلد
function updatePath(folderId) {
    console.log('تحديث مسار المجلد:', folderId);
    
    const pathElement = document.getElementById('current-path');
    if (!pathElement) {
        console.error('لم يتم العثور على عنصر المسار!');
        return;
    }
    
    // إنشاء مسار المجلد
    const path = buildPath(folderId);
    pathElement.innerHTML = path;
}

// بناء مسار المجلد
function buildPath(folderId) {
    const pathParts = [];
    let currentId = folderId;
    
    // استخراج المسار من المجلد الحالي وصولا للجذر
    while (currentId && currentId !== 'null') {
        const folder = archiveData.folders[currentId];
        if (!folder) break;
        
        pathParts.unshift({
            id: folder.id,
            name: folder.name
        });
        
        currentId = folder.parentId;
    }
    
    // بناء HTML للمسار
    let pathHTML = '';
    pathParts.forEach((part, index) => {
        if (index > 0) {
            pathHTML += ' / ';
        }
        
        if (index === pathParts.length - 1) {
            pathHTML += `<span class="fw-bold">${part.name}</span>`;
        } else {
            pathHTML += `<a href="#" onclick="navigateToFolder('${part.id}'); return false;">${part.name}</a>`;
        }
    });
    
    return pathHTML;
}

// الانتقال إلى مجلد
function navigateToFolder(folderId) {
    console.log('الانتقال إلى المجلد:', folderId);
    
    // إذا كان المجلد الحالي موجودا في التاريخ، فقم بقطع التاريخ عند ذلك المجلد
    if (historyPosition < folderHistory.length - 1) {
        folderHistory = folderHistory.slice(0, historyPosition + 1);
    }
    
    // أضف المجلد الجديد إلى التاريخ
    folderHistory.push(folderId);
    historyPosition = folderHistory.length - 1;
    
    // عرض محتويات المجلد
    displayFolderContents(folderId);
}

// العودة للخلف
function navigateBack() {
    console.log('العودة للخلف');
    
    if (historyPosition > 0) {
        historyPosition--;
        const prevFolderId = folderHistory[historyPosition];
        displayFolderContents(prevFolderId);
    }
}

// الانتقال للأمام
function navigateForward() {
    console.log('الانتقال للأمام');
    
    if (historyPosition < folderHistory.length - 1) {
        historyPosition++;
        const nextFolderId = folderHistory[historyPosition];
        displayFolderContents(nextFolderId);
    }
}

// الانتقال للأعلى
function navigateUp() {
    console.log('الانتقال للأعلى');
    
    const folder = archiveData.folders[currentFolder];
    if (folder && folder.parentId) {
        navigateToFolder(folder.parentId);
    }
}

// العودة للرئيسية
function navigateHome() {
    console.log('العودة للرئيسية');
    navigateToFolder('root');
}

// تحديث حالة أزرار التنقل
function updateButtonStates() {
    // زر العودة للخلف
    const backBtn = document.getElementById('back-btn');
    if (backBtn) {
        backBtn.disabled = historyPosition <= 0;
    }
    
    // زر الانتقال للأمام
    const forwardBtn = document.getElementById('forward-btn');
    if (forwardBtn) {
        forwardBtn.disabled = historyPosition >= folderHistory.length - 1;
    }
    
    // زر الانتقال للأعلى
    const upBtn = document.getElementById('up-btn');
    if (upBtn) {
        const folder = archiveData.folders[currentFolder];
        upBtn.disabled = !folder || !folder.parentId;
    }
}

// دالة عامة للتصدير يمكن استدعاؤها مباشرة
window.navigateToFolder = navigateToFolder;
window.navigateBack = navigateBack;
window.navigateForward = navigateForward;
window.navigateUp = navigateUp;
window.navigateHome = navigateHome;