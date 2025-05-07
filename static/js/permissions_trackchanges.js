/**
 * سكريبت لتتبع تغييرات الصلاحيات بدقة وحفظ التغييرات فقط
 * يتم تضمينه بعد permissions_redesign.js
 */

// المتغيرات العامة لتتبع التغييرات
var initialPermissionState = {}; // حالة الصلاحيات الأولية
var changedPermissionsOnly = {}; // الصلاحيات التي تم تغييرها فقط
var hasChanges = false; // هل هناك تغييرات؟

// تتبع التغييرات على الصلاحيات بشكل دقيق
$(document).ready(function() {
    // حفظ الحالة الأولية للصلاحيات
    captureInitialPermissionState();
    
    // إلغاء تعريف دالة saveAllPermissions الأصلية واستبدالها
    var originalSaveFunction = window.saveAllPermissions;
    window.saveAllPermissions = function() {
        return saveChangedPermissionsOnly();
    };
    
    // إضافة مستمع أحداث على كل بطاقة صلاحية
    $('.permission-card').on('click', function() {
        var sectionId = $(this).closest('.permissions-section').attr('id').replace('section-', '');
        var permName = $(this).find('.permission-title').data('perm-name') || 
                       $(this).find('.permission-title').text().trim().toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
        
        // تسجيل التغيير في مصفوفة التغييرات
        if (!changedPermissionsOnly[sectionId]) {
            changedPermissionsOnly[sectionId] = [];
        }
        
        // تحديث حالة التغيير
        var wasActive = initialPermissionState[sectionId] && initialPermissionState[sectionId].includes(permName);
        var isNowActive = $(this).hasClass('active');
        
        if (wasActive !== isNowActive) {
            // إضافة أو إزالة من قائمة التغييرات
            if (!changedPermissionsOnly[sectionId].includes(permName)) {
                changedPermissionsOnly[sectionId].push(permName);
                console.log(`تم تسجيل تغيير للصلاحية: ${sectionId}_${permName}`);
            }
        } else {
            // إزالة من قائمة التغييرات إذا تم إلغاء التغيير
            var index = changedPermissionsOnly[sectionId].indexOf(permName);
            if (index > -1) {
                changedPermissionsOnly[sectionId].splice(index, 1);
                console.log(`تم إلغاء تغيير الصلاحية: ${sectionId}_${permName}`);
            }
            
            // إزالة المصفوفة الفرعية إذا أصبحت فارغة
            if (changedPermissionsOnly[sectionId].length === 0) {
                delete changedPermissionsOnly[sectionId];
            }
        }
        
        // تحديث حالة التغييرات
        hasChanges = Object.keys(changedPermissionsOnly).length > 0;
        
        // تحديث عداد التغييرات وحالة زر الحفظ
        updateChangesCounter();
    });
});

/**
 * حفظ الحالة الأولية للصلاحيات
 */
function captureInitialPermissionState() {
    $('.permissions-section').each(function() {
        var sectionId = $(this).attr('id').replace('section-', '');
        initialPermissionState[sectionId] = [];
        
        // فحص جميع بطاقات الصلاحيات النشطة
        $(this).find('.permission-card.active').each(function() {
            var permName = $(this).find('.permission-title').data('perm-name') || 
                          $(this).find('.permission-title').text().trim().toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
            
            initialPermissionState[sectionId].push(permName);
        });
    });
    
    console.log('تم حفظ الحالة الأولية للصلاحيات:', initialPermissionState);
}

/**
 * تحديث عداد التغييرات
 */
function updateChangesCounter() {
    // حساب إجمالي التغييرات
    var totalChanges = 0;
    for (var section in changedPermissionsOnly) {
        totalChanges += changedPermissionsOnly[section].length;
    }
    
    // تحديث العداد
    $('#changes-counter').text(totalChanges);
    
    // تحديث حالة زر الحفظ
    if (totalChanges > 0) {
        $('#save-all-permissions-btn').addClass('has-changes').find('span').text(`حفظ التغييرات (${totalChanges})`);
    } else {
        $('#save-all-permissions-btn').removeClass('has-changes').find('span').text('حفظ التغييرات');
    }
}

/**
 * حفظ الصلاحيات المتغيرة فقط
 */
function saveChangedPermissionsOnly() {
    // التحقق من وجود تغييرات
    if (!hasChanges) {
        showNotification('تنبيه', 'لم يتم إجراء أي تغييرات على الصلاحيات', 'warning');
        return false;
    }
    
    console.log('التغييرات التي سيتم حفظها:', changedPermissionsOnly);
    
    // تغيير حالة الزر إلى جاري الحفظ
    $('#save-all-permissions-btn').addClass('loading').find('span').text('جاري الحفظ...');
    
    // إضافة الحقول المخفية للصلاحيات المتغيرة فقط
    addChangedPermissionsFields();
    
    // إضافة علامة التغييرات
    $('<input>').attr({
        type: 'hidden',
        name: 'save_changes_only',
        value: 'true'
    }).appendTo('#permissions-form');
    
    // إرسال النموذج
    $('#permissions-form').submit();
    
    // عرض إشعار الحفظ
    showNotification('جاري الحفظ', 'يتم الآن حفظ التغييرات التي أجريتها فقط', 'info');
    
    return false;
}

/**
 * إضافة حقول مخفية للصلاحيات المتغيرة فقط
 */
function addChangedPermissionsFields() {
    // حذف الحقول المخفية السابقة
    $('#permissions-form input[type="hidden"][name^="checkbox_"]').remove();
    $('#permissions-form input[type="hidden"][name^="perm_"]').remove();
    $('#permissions-form input[type="hidden"][name$="_view"]').remove();
    $('#permissions-form input[type="hidden"][name$="_edit"]').remove();
    $('#permissions-form input[type="hidden"][name$="_create"]').remove();
    $('#permissions-form input[type="hidden"][name$="_delete"]').remove();
    
    // إضافة معرف المسؤول كحقل مخفي
    const adminId = $('#admin-id').val() || $('form').data('admin-id');
    const adminIdInput = $('<input>').attr({
        type: 'hidden',
        name: 'admin_id',
        value: adminId
    });
    $('#permissions-form').append(adminIdInput);
    
    // إضافة حقول مخفية للصلاحيات المتغيرة
    $('.permissions-section').each(function() {
        const sectionId = $(this).attr('id').replace('section-', '');
        
        // إذا كان هناك تغييرات لهذا القسم
        if (changedPermissionsOnly[sectionId] && changedPermissionsOnly[sectionId].length > 0) {
            // حفظ الحالة الحالية لكل صلاحية متغيرة
            $(this).find('.permission-card').each(function() {
                const permTitle = $(this).find('.permission-title').text().trim();
                const permName = $(this).find('.permission-title').data('perm-name') || 
                               permTitle.toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
                
                // التحقق إذا كانت هذه الصلاحية في قائمة التغييرات
                if (changedPermissionsOnly[sectionId].includes(permName)) {
                    // إضافة حقل يحدد الحالة الجديدة (نشطة أم لا)
                    const isActive = $(this).hasClass('active');
                    
                    // إضافة الحقل بتنسيق يفهمه الخادم
                    const stateField = $('<input>').attr({
                        type: 'hidden',
                        name: `${sectionId}_${permName}_changed`,
                        value: isActive ? 'on' : 'off'
                    });
                    $('#permissions-form').append(stateField);
                    
                    // إذا كانت الصلاحية نشطة، أضف حقل مماثل بتنسيق on
                    if (isActive) {
                        const activeField = $('<input>').attr({
                            type: 'hidden',
                            name: `${sectionId}_${permName}`,
                            value: 'on'
                        });
                        $('#permissions-form').append(activeField);
                    }
                    
                    console.log(`تم إضافة حقل للصلاحية المتغيرة: ${sectionId}_${permName} = ${isActive ? 'on' : 'off'}`);
                }
            });
        }
    });
    
    // إضافة حقل JSON يحتوي على كل التغييرات
    const changesField = $('<input>').attr({
        type: 'hidden',
        name: 'changes_json',
        value: JSON.stringify(changedPermissionsOnly)
    });
    $('#permissions-form').append(changesField);
    
    console.log('تم إضافة حقول مخفية للتغييرات:', changedPermissionsOnly);
}