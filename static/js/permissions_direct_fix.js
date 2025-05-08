/**
 * إصلاح مباشر وبسيط جداً لمشكلة تحديد الصلاحيات
 * 
 * هذا الملف يستخدم jQuery مباشرة لتنفيذ السلوك المطلوب
 * دون الاعتماد على الملفات السابقة
 */

$(document).ready(function() {
    console.log("⚡ تم تحميل نظام الصلاحيات المحسن");

    // إضافة معرفات واضحة للبطاقات وسمات البيانات
    console.log("🔧 إضافة معرفات وسمات البيانات إلى بطاقات الصلاحيات...");
    $('.permissions-section').each(function() {
        const sectionId = $(this).attr('id').replace('section-', '');
        
        // مر على كل بطاقة في هذا القسم
        $(this).find('.permission-card').each(function(index) {
            // إنشاء معرّف فريد للبطاقة
            const cardId = `perm-card-${sectionId}-${index}`;
            // إضافة المعرّف للبطاقة
            $(this).attr('id', cardId);
            
            // إضافة سمة data-section إذا لم تكن موجودة
            if (!$(this).data('section')) {
                $(this).attr('data-section', sectionId);
            }
            
            // إضافة سمة data-permission إذا لم تكن موجودة
            if (!$(this).data('permission')) {
                // محاولة استخراج اسم الصلاحية من العنوان
                const titleText = $(this).find('.permission-title').text().trim();
                if (titleText) {
                    // تحويل النص العربي إلى معرّف صالح للصلاحية
                    let permId = '';
                    if (titleText.includes('عرض') || titleText.includes('الاطلاع')) {
                        permId = 'view_' + (sectionId.endsWith('s') ? sectionId.slice(0, -1) : sectionId);
                    } else if (titleText.includes('إضافة') || titleText.includes('إنشاء')) {
                        permId = 'create_' + (sectionId.endsWith('s') ? sectionId.slice(0, -1) : sectionId);
                    } else if (titleText.includes('تعديل')) {
                        permId = 'edit_' + (sectionId.endsWith('s') ? sectionId.slice(0, -1) : sectionId);
                    } else if (titleText.includes('حذف')) {
                        permId = 'delete_' + (sectionId.endsWith('s') ? sectionId.slice(0, -1) : sectionId);
                    } else {
                        // استخدام الموقع في القسم
                        permId = sectionId + '_perm_' + index;
                    }
                    
                    $(this).attr('data-permission', permId);
                }
            }
        });
    });
    console.log("✅ تم إضافة المعرفات وسمات البيانات إلى البطاقات");

    // تخزين الحالة الأولية للصلاحيات
    let initialPermissions = {};
    try {
        const savedJson = $('#saved_permissions_json').val();
        initialPermissions = JSON.parse(savedJson || '{}');
        console.log('✅ تم تحميل الصلاحيات الأولية:', initialPermissions);
    } catch (e) {
        console.error('❌ خطأ في تحميل الصلاحيات الأولية:', e);
    }

    // تحديث البطاقات بناءً على الصلاحيات المحفوظة
    function updateCardsFromPermissions(permissions) {
        // قبل البدء، سجل عدد البطاقات النشطة للمقارنة
        const activeBefore = $('.permission-card.active').length;
        console.log(`📊 قبل التحديث: ${activeBefore} بطاقة نشطة`);
        
        // إزالة جميع الفئات النشطة أولاً
        $('.permission-card').removeClass('active');
        
        console.log("🔄 تحديث البطاقات من الصلاحيات:", permissions);

        // تحديث المتغير العام للوصول إليه من أي مكان
        window.savedPermissions = permissions;
        
        // حفظ الصلاحيات في الحقل المخفي لضمان استمراريتها
        $('#saved_permissions_json').val(JSON.stringify(permissions));

        // تأكد من إزالة الفئة النشطة من جميع البطاقات
        $('.permission-card').removeClass('active');
        
        // طرق متعددة لضمان تحديث جميع البطاقات:
        
        // الطريقة 1: دورة خاصة بكل قسم وصلاحية (الطريقة المفضلة)
        for (const section in permissions) {
            if (Array.isArray(permissions[section])) {
                permissions[section].forEach(permission => {
                    console.log(`🔍 تنشيط الصلاحية: ${section}.${permission}`);
                    
                    // 1.أ. باستخدام سمات البيانات
                    const cardsByData = $(`.permission-card[data-section="${section}"][data-permission="${permission}"]`);
                    if (cardsByData.length) {
                        cardsByData.addClass('active');
                        console.log(`✓ تم تفعيل ${cardsByData.length} بطاقة باستخدام السمات`);
                    }
                    
                    // 1.ب. باستخدام المحتوى النصي للعنوان
                    const titleCards = $(`.permission-card .permission-title[data-perm-name="${permission}"]`).closest('.permission-card');
                    if (titleCards.length) {
                        titleCards.addClass('active');
                    }
                    
                    // 1.ج. البحث المباشر في القسم
                    $(`#section-${section} .permission-card`).each(function() {
                        if ($(this).data('permission') === permission) {
                            $(this).addClass('active');
                        }
                    });
                });
            }
        }
        
        // الطريقة 2: تنفيذ تعليم إضافي لكافة البطاقات
        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            if (permissions[sectionId] && Array.isArray(permissions[sectionId])) {
                const sectionPerms = permissions[sectionId];
                
                $(this).find('.permission-card').each(function() {
                    // أ. تحقق من خاصية data-permission
                    const permData = $(this).data('permission');
                    if (permData && sectionPerms.includes(permData)) {
                        $(this).addClass('active');
                    }
                    
                    // ب. تحقق من عنوان البطاقة
                    const titleElement = $(this).find('.permission-title');
                    if (titleElement.length) {
                        const permName = titleElement.data('perm-name');
                        if (permName && sectionPerms.includes(permName)) {
                            $(this).addClass('active');
                        }
                    }
                });
            }
        });
        
        // حساب عدد البطاقات النشطة بعد التحديث
        const activeAfter = $('.permission-card.active').length;
        console.log(`📊 بعد التحديث: ${activeAfter} بطاقة نشطة (تغيير: ${activeAfter - activeBefore})`);

        // تحديث عدادات الأقسام والتبويبات
        updateAllCounters();
        
        console.log("✅ تم الانتهاء من تحديث البطاقات بنجاح");
        
        // بعد التحديث، تأكد أن عدد البطاقات النشطة يتطابق مع عدد الصلاحيات المحفوظة
        let totalPermissionsCount = 0;
        for (const section in permissions) {
            if (Array.isArray(permissions[section])) {
                totalPermissionsCount += permissions[section].length;
            }
        }
        
        console.log(`📊 إحصائيات: ${activeAfter} بطاقة نشطة، ${totalPermissionsCount} صلاحية محفوظة`);
        if (activeAfter < totalPermissionsCount) {
            console.warn(`⚠️ تحذير: بعض الصلاحيات (${totalPermissionsCount - activeAfter}) لم يتم تفعيل بطاقاتها`);
        }
    }

    // جمع الصلاحيات النشطة
    function collectActivePermissions() {
        const permissions = {};

        // تهيئة جميع الأقسام بمصفوفات فارغة
        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            permissions[sectionId] = [];
        });

        // جمع الصلاحيات النشطة من البطاقات
        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            
            $(this).find('.permission-card.active').each(function() {
                // عدة طرق للحصول على اسم الصلاحية
                
                // 1. من خاصية data-permission
                let permissionName = $(this).data('permission');
                
                // 2. من عنوان الصلاحية data-perm-name
                if (!permissionName) {
                    const title = $(this).find('.permission-title');
                    if (title.length && title.data('perm-name')) {
                        permissionName = title.data('perm-name');
                    }
                }
                
                // 3. من نص العنوان كحل أخير
                if (!permissionName) {
                    const titleText = $(this).find('.permission-title').text().trim();
                    if (titleText) {
                        // تحليل النص للحصول على مفتاح الصلاحية
                        if (titleText.includes('عرض') || titleText.includes('الاطلاع')) {
                            permissionName = 'view_' + sectionId;
                        } else if (titleText.includes('إضافة') || titleText.includes('إنشاء')) {
                            permissionName = 'create_' + sectionId.replace(/s$/, '');
                        } else if (titleText.includes('تعديل')) {
                            permissionName = 'edit_' + sectionId.replace(/s$/, '');
                        } else if (titleText.includes('حذف')) {
                            permissionName = 'delete_' + sectionId.replace(/s$/, '');
                        } else {
                            // استخراج كلمات المفتاح من النص
                            permissionName = titleText.toLowerCase()
                                .replace(/[\u0600-\u06FF]/g, '') // إزالة الحروف العربية
                                .replace(/[^\w\s]/gi, '') // إزالة العلامات
                                .trim()
                                .replace(/\s+/g, '_'); // استبدال المسافات بشرطات سفلية
                            
                            // إذا كان المفتاح فارغاً بعد المعالجة، استخدم نوعاً افتراضياً
                            if (!permissionName) {
                                permissionName = 'perm_' + Math.floor(Math.random() * 1000);
                            }
                        }
                    }
                }

                // إضافة الصلاحية للقسم إذا كانت صالحة ولم تتم إضافتها من قبل
                if (permissionName && !permissions[sectionId].includes(permissionName)) {
                    permissions[sectionId].push(permissionName);
                    console.log(`📌 تم جمع الصلاحية "${permissionName}" في قسم "${sectionId}"`);
                }
            });
        });

        console.log("📝 الصلاحيات المجمعة من واجهة المستخدم:", permissions);
        return permissions;
    }

    // معالج حفظ الصلاحيات
    $('#permissionsForm').on('submit', function(e) {
        e.preventDefault();
        savePermissions();
    });

    function savePermissions() {
        const formData = new FormData($('#permissionsForm')[0]);
        const activePermissions = collectActivePermissions();

        // إضافة الصلاحيات النشطة للنموذج
        formData.append('permissions', JSON.stringify(activePermissions));

        // عرض مؤشر التحميل
        const loadingOverlay = $('<div id="loadingOverlay">').css({
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0,0,0,0.5)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white'
        }).html(`
            <div class="text-center">
                <div class="spinner-border mb-2" role="status"></div>
                <p>جاري حفظ الصلاحيات...</p>
            </div>
        `);

        $('body').append(loadingOverlay);

        // إرسال الطلب
        $.ajax({
            url: $('#permissionsForm').attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log("👉 استجابة الخادم:", response);
                
                // تحقق من نوع الاستجابة (قد تكون JSON أو نص HTML)
                let responseData = response;
                if (typeof response === 'string') {
                    // إذا كانت الاستجابة نصية تحتوي على HTML (صفحة كاملة)
                    console.log("⚠️ الاستجابة نصية HTML - سنقوم باستخراج permissions_json منها");
                    
                    try {
                        // محاولة استخراج permissions_json من صفحة HTML باستخدام عدة أنماط
                        console.log("🔍 جاري البحث عن نمط permissions_json في استجابة HTML...");
                        
                        // محاولة النمط الأول: value='...'
                        const jsonMatch1 = response.match(/id="saved_permissions_json" value='(.+?)'/);
                        if (jsonMatch1 && jsonMatch1[1]) {
                            const extractedJson = jsonMatch1[1];
                            responseData = { status: 'success', permissions: JSON.parse(extractedJson) };
                            console.log("✅ تم استخراج الصلاحيات من HTML (النمط 1):", responseData.permissions);
                        } 
                        // محاولة النمط الثاني: value="..."
                        else {
                            const jsonMatch2 = response.match(/id="saved_permissions_json" value="(.+?)"/);
                            if (jsonMatch2 && jsonMatch2[1]) {
                                const extractedJson = jsonMatch2[1];
                                responseData = { status: 'success', permissions: JSON.parse(extractedJson) };
                                console.log("✅ تم استخراج الصلاحيات من HTML (النمط 2):", responseData.permissions);
                            }
                            // محاولة النمط الثالث: id="saved_permissions_json" أي نمط
                            else {
                                // استخراج جزء من HTML حول العنصر المطلوب
                                const elementSection = response.match(/id="saved_permissions_json"[^>]*>/)
                                if (elementSection) {
                                    console.log("🔍 تم العثور على العنصر، ولكن نحتاج استخراج القيمة:", elementSection[0]);
                                    
                                    // محاولة استخراج البيانات من أي نوع من السمات
                                    const valueMatch = elementSection[0].match(/value=["'](.+?)["']/);
                                    if (valueMatch && valueMatch[1]) {
                                        const extractedJson = valueMatch[1];
                                        responseData = { status: 'success', permissions: JSON.parse(extractedJson) };
                                        console.log("✅ تم استخراج الصلاحيات من HTML (النمط 3):", responseData.permissions);
                                    } else {
                                        throw new Error("تم العثور على العنصر ولكن لا توجد قيمة به");
                                    }
                                } else {
                                    throw new Error("لم نتمكن من العثور على عنصر saved_permissions_json في الاستجابة");
                                }
                            }
                        }
                    } catch (e) {
                        console.error("❌ خطأ في معالجة الاستجابة:", e);
                        console.log("🔍 محتوى استجابة الخادم (جزء):", response.substring(0, 200) + "...");
                        
                        // إضافة بعض معلومات التشخيص الإضافية
                        if (response.includes("<html")) {
                            console.log("ℹ️ الاستجابة تبدو كصفحة HTML");
                            
                            // محاولة معرفة نوع الصفحة
                            if (response.includes("login") || response.includes("تسجيل الدخول")) {
                                console.error("⚠️ يبدو أن الاستجابة هي صفحة تسجيل الدخول، قد تكون الجلسة منتهية");
                            } else if (response.includes("error") || response.includes("خطأ")) {
                                console.error("⚠️ يبدو أن الاستجابة تحتوي على صفحة خطأ");
                            }
                        }
                        
                        // البحث عن أي بيانات JSON في الاستجابة
                        const jsonObjects = response.match(/\{[^\}]+\}/g);
                        if (jsonObjects && jsonObjects.length) {
                            console.log("🔍 وجدنا بعض كائنات JSON في الاستجابة:", jsonObjects.slice(0, 3));
                            
                            // محاولة تحليل وتخمين الصلاحيات
                            try {
                                for (const jsonStr of jsonObjects) {
                                    const jsonObject = JSON.parse(jsonStr);
                                    if (jsonObject && (jsonObject.permissions || jsonObject.status)) {
                                        console.log("✅ وجدنا كائن JSON محتمل:", jsonObject);
                                        if (jsonObject.permissions) {
                                            responseData = jsonObject;
                                            console.log("🎯 استخدام الكائن المكتشف للصلاحيات");
                                            break;
                                        }
                                    }
                                }
                            } catch (jsonError) {
                                console.error("❌ فشلت محاولة تخمين JSON:", jsonError);
                            }
                        }
                        
                        // إعادة تحميل الصفحة كملاذ أخير إذا لم نتمكن من استخراج الصلاحيات
                        if (!responseData.permissions) {
                            console.warn("⚠️ لا يمكن استخراج الصلاحيات، جاري إعادة تحميل الصفحة...");
                            window.location.reload();
                            return;
                        }
                    }
                }
                
                // الخطوة 1: تحديث المتغيرات العامة أولاً
                let updatedPermissions = {};
                
                // الحصول على الصلاحيات المحدثة من الاستجابة أو محلياً
                if (responseData.permissions) {
                    // استخدام الصلاحيات من استجابة الخادم
                    updatedPermissions = responseData.permissions;
                    console.log("📄 تم استلام الصلاحيات من الخادم:", updatedPermissions);
                } else {
                    // استخدام الصلاحيات المحلية كبديل
                    updatedPermissions = collectActivePermissions();
                    console.log("⚠️ استخدام الصلاحيات المحلية كبديل:", updatedPermissions);
                    
                    if (Object.keys(updatedPermissions).length === 0) {
                        console.warn("⚠️ الصلاحيات المحلية فارغة - سنحاول استخدام القيم المحفوظة مسبقاً");
                        
                        // محاولة استخدام الصلاحيات المحفوظة مسبقاً
                        try {
                            const savedJson = $('#saved_permissions_json').val();
                            if (savedJson) {
                                updatedPermissions = JSON.parse(savedJson);
                                console.log("🔄 استخدام الصلاحيات المحفوظة مسبقاً:", updatedPermissions);
                            }
                        } catch (e) {
                            console.error("❌ فشل استرداد الصلاحيات المحفوظة:", e);
                        }
                    }
                }
                
                // الخطوة 2: تحديث الأشياء الثابتة
                
                // حفظ الصلاحيات في متغير عام
                window.savedPermissions = updatedPermissions;
                
                // حفظ في الحقل المخفي
                $('#saved_permissions_json').val(JSON.stringify(updatedPermissions));
                
                // الخطوة 3: مباشرة بالتحديث الفعلي لواجهة المستخدم
                try {
                    console.log("🔄 جاري تحديث واجهة المستخدم مع الصلاحيات الجديدة...");
                    
                    // التحديث بطريقة مباشرة ومحسنة
                    updatePermissionCardsDirectly(updatedPermissions);
                    
                    console.log("✅ تم تحديث واجهة المستخدم بنجاح");
                    showNotification('تم', 'تم حفظ الصلاحيات بنجاح وتحديث الواجهة', 'success');
                } catch (error) {
                    console.error("❌ خطأ أثناء تحديث واجهة المستخدم:", error);
                    
                    // المحاولة بطريقة بديلة قبل إعادة التحميل
                    try {
                        console.log("🔄 محاولة تحديث بطريقة بديلة...");
                        
                        // إعادة تعيين البطاقات
                        $('.permission-card').removeClass('active');
                        
                        // تنفيذ تعليم البطاقات (الطريقة الاحتياطية)
                        markActiveCards();
                        
                        console.log("✓ تم استخدام الطريقة البديلة بنجاح");
                        showNotification('تنبيه', 'تم الحفظ وتم استخدام طريقة بديلة للتحديث', 'warning');
                    } catch (fallbackError) {
                        console.error("❌ فشلت الطريقة البديلة أيضاً:", fallbackError);
                        showNotification('تحذير', 'تم الحفظ ولكن فشل تحديث الواجهة - جاري إعادة التحميل', 'warning');
                        
                        // إعادة تحميل الصفحة كملاذ أخير
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ خطأ في الحفظ:', xhr, status, error);
                showNotification('خطأ', 'حدث خطأ في الاتصال بالخادم: ' + error, 'error');
                
                // إعادة تحميل الصفحة بعد فترة كملاذ أخير
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            },
            complete: function() {
                $('#loadingOverlay').remove();
            }
        });
    }

    // معالج النقر على البطاقات
    $('.permission-card').on('click', function(e) {
        if (!$(e.target).is('a, button') && !$(e.target).parents('a, button').length) {
            $(this).toggleClass('active');
            updateAllCounters();
        }
    });

    // معالج زر تحديد الكل
    $('.select-all').on('click', function(e) {
        e.preventDefault();
        const section = $(this).data('section');
        $(`#section-${section} .permission-card`).addClass('active');
        updateAllCounters();
    });

    // تحديث عدادات الصلاحيات
    function updateAllCounters() {
        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            const totalCards = $(this).find('.permission-card').length;
            const activeCards = $(this).find('.permission-card.active').length;

            // تحديث العداد في التبويب
            $(`.tab-item[data-section="${sectionId}"] .tab-count`)
                .text(activeCards)
                .toggleClass('active', activeCards > 0);

            // تحديث عداد القسم
            $(this).find('.section-count').text(`${activeCards} / ${totalCards}`);
        });
    }

    // تهيئة الواجهة
    updateCardsFromPermissions(initialPermissions);

    // إضافة دالة إظهار الإشعارات المحسنة إذا لم تكن موجودة
    if (typeof showNotification !== 'function') {
        window.showNotification = function(title, message, type = 'success') {
            // تحديد لون خلفية الإشعار
            let bgColor, color, icon;
            switch (type) {
                case 'success':
                    bgColor = '#d1e7dd';
                    color = '#0f5132';
                    icon = 'fas fa-check-circle';
                    break;
                case 'warning':
                    bgColor = '#fff3cd';
                    color = '#856404';
                    icon = 'fas fa-exclamation-triangle';
                    break;
                case 'error':
                    bgColor = '#f8d7da';
                    color = '#842029';
                    icon = 'fas fa-times-circle';
                    break;
                default:
                    bgColor = '#cfe2ff';
                    color = '#084298';
                    icon = 'fas fa-info-circle';
            }
            
            // إنشاء عنصر الإشعار
            const notificationId = 'notification-' + Date.now();
            const notification = `
                <div id="${notificationId}" class="notification" style="
                    position: fixed;
                    top: 20px;
                    left: 20px;
                    max-width: 350px;
                    background-color: ${bgColor};
                    color: ${color};
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    z-index: 1000;
                    display: flex;
                    align-items: flex-start;
                    gap: 10px;
                    transform: translateX(-100%);
                    opacity: 0;
                    transition: all 0.3s ease;
                ">
                    <div style="font-size: 1.2rem;"><i class="${icon}"></i></div>
                    <div style="flex-grow: 1;">
                        <div style="font-weight: 600; margin-bottom: 5px;">${title}</div>
                        <div style="font-size: 0.9rem;">${message}</div>
                    </div>
                    <button onclick="document.getElementById('${notificationId}').remove()" style="
                        background: none;
                        border: none;
                        cursor: pointer;
                        color: inherit;
                        opacity: 0.7;
                        font-size: 1.2rem;
                        padding: 0;
                        margin-left: 10px;
                    ">×</button>
                </div>
            `;
            
            // إضافة الإشعار إلى الصفحة
            $('body').append(notification);
            
            // تفعيل الإشعار
            setTimeout(() => {
                $(`#${notificationId}`).css({
                    transform: 'translateX(0)',
                    opacity: 1
                });
                
                // إخفاء الإشعار تلقائياً بعد 5 ثوان
                setTimeout(() => {
                    $(`#${notificationId}`).css({
                        transform: 'translateX(-100%)',
                        opacity: 0
                    });
                    
                    // إزالة الإشعار من DOM بعد انتهاء الانتقال
                    setTimeout(() => {
                        $(`#${notificationId}`).remove();
                    }, 300);
                }, 5000);
            }, 100);
        }
    }

    // معالج زر الحفظ
    $('#savePermissionsBtn').on('click', function(e) {
        e.preventDefault();
        savePermissions();
    });

    // إضافة معالج نقر للتبويبات
    $('.tab-item').on('click', function(e) {
        e.preventDefault();

        // تجاهل إذا كان زر فتح الكل
        if ($(this).hasClass('utility')) {
            return;
        }

        const targetSection = $(this).data('section');

        // تحديث حالة التبويبات
        $('.tab-item').removeClass('active');
        $(this).addClass('active');

        // إظهار القسم المطلوب
        $('.permissions-section').removeClass('active');
        $('#section-' + targetSection).addClass('active');

        // إظهار البطاقات في القسم
        $('#section-' + targetSection + ' .section-body').show();

        // تحديث العدادات
        updateAllCounters();
    });

    // معالج فتح/إغلاق الأقسام
    $('.toggle-section').on('click', function(e) {
        e.preventDefault();
        const sectionBody = $(this).closest('.permissions-section').find('.section-body');
        sectionBody.slideToggle();

        // تغيير اتجاه السهم
        const icon = $(this).find('i');
        icon.toggleClass('fa-chevron-down fa-chevron-up');
    });

    // زر فتح جميع الأقسام
    $('#expand-all').on('click', function() {
        $('.section-body').slideDown();
        $('.toggle-section i').removeClass('fa-chevron-down').addClass('fa-chevron-up');
    });

    // تحسين زر تحديد الكل
    $('.select-all').on('click', function(e) {
        e.preventDefault();
        const section = $(this).data('section');
        const cards = $(`#section-${section} .permission-card`);

        // تحديد/إلغاء تحديد البطاقات
        cards.each(function() {
            $(this).addClass('active');
        });

        // تحديث العدادات فقط دون حفظ
        updateAllCounters();
    });


    // دالة تحديث مباشر للبطاقات
    function updatePermissionCardsDirectly(permissions) {
        console.log("🎯 بدء التحديث المباشر للبطاقات باستخدام:", permissions);
        
        // 1. تفريغ حالة البطاقات أولاً
        $('.permission-card').removeClass('active');
        
        // 2. حلقة مباشرة على كل البطاقات
        $('.permission-card').each(function() {
            const card = $(this);
            const section = card.data('section');
            const permission = card.data('permission');
            
            // التحقق من وجود سمات البيانات
            if (!section || !permission) {
                console.log(`⚠️ البطاقة تفتقد إلى سمات البيانات id=${card.attr('id')}`);
                return; // تخطي هذه البطاقة
            }
            
            // التحقق من وجود الصلاحية في المصفوفة
            if (permissions[section] && 
                Array.isArray(permissions[section]) && 
                permissions[section].includes(permission)) {
                // تنشيط البطاقة
                card.addClass('active');
                console.log(`✓ تم تنشيط البطاقة: ${section}.${permission}`);
            }
        });
        
        // 3. تحديث العدادات
        updateAllCounters();
        
        // 4. إحصائيات للمتابعة
        const activeCount = $('.permission-card.active').length;
        const totalCount = $('.permission-card').length;
        console.log(`📊 إحصائيات التحديث المباشر: ${activeCount} بطاقة نشطة من أصل ${totalCount}`);
        
        // 5. التحقق من مجموع العدادات
        let permissionSum = 0;
        for (const section in permissions) {
            if (Array.isArray(permissions[section])) {
                permissionSum += permissions[section].length;
            }
        }
        
        // مقارنة الأرقام
        if (activeCount < permissionSum) {
            console.warn(`⚠️ تحذير: ${permissionSum - activeCount} صلاحية لم يتم العثور على بطاقاتها`);
        } else if (activeCount > permissionSum) {
            console.warn(`⚠️ تحذير: ${activeCount - permissionSum} بطاقة زائدة تم تنشيطها`);
        } else {
            console.log(`✅ تطابق تام: ${permissionSum} صلاحية مع ${activeCount} بطاقة نشطة`);
        }
    }

    // تنفيذ تعليم البطاقات النشطة عند تحميل الصفحة
    markActiveCards();
    $('.tab-item:not(.utility)').first().click(); //trigger first tab click after page load

});

// تعليم البطاقات النشطة بناءً على الصلاحيات المحفوظة
function markActiveCards() {
    // قبل التنفيذ سجل المعلومات للمتابعة
    const activeBefore = $('.permission-card.active').length;
    console.log(`⏱️ بدء تعليم البطاقات - العدد الحالي: ${activeBefore} بطاقة نشطة`);
    
    // إعادة تعيين حالة جميع البطاقات
    $('.permission-card').removeClass('active');

    // تأكد من وجود الصلاحيات المحفوظة
    if (!window.savedPermissions) {
        try {
            // محاولة استخراج الصلاحيات من الحقل المخفي
            const savedJson = $('#saved_permissions_json').val();
            if (savedJson) {
                window.savedPermissions = JSON.parse(savedJson);
                console.log("✅ تم استعادة الصلاحيات من الحقل المخفي:", window.savedPermissions);
            } else {
                console.warn("⚠️ لا توجد صلاحيات محفوظة في الحقل المخفي");
                window.savedPermissions = {}; // تعيين كائن فارغ افتراضي
                return; // توقف إذا لم تكن هناك صلاحيات
            }
        } catch (e) {
            console.error("❌ خطأ في تحليل الصلاحيات المحفوظة:", e);
            return; // توقف إذا كان هناك خطأ
        }
    }

    console.log("🔍 تعليم البطاقات النشطة باستخدام:", window.savedPermissions);

    // تنفيذ عدة آليات للتعليم لضمان عمل البطاقات حتى مع هيكل HTML مختلف

    // 1. تعيين علامات البطاقات باستخدام الاختيارات المباشرة
    let totalMarked = 0;
    for (const section in window.savedPermissions) {
        if (Array.isArray(window.savedPermissions[section])) {
            window.savedPermissions[section].forEach(permission => {
                let markedCount = 0;
                
                console.log(`🔸 تعليم الصلاحية: ${section}.${permission}`);
                
                // 1.أ. باستخدام سمات البيانات المباشرة - الطريقة الأكثر دقة
                const directCards = $(`.permission-card[data-section="${section}"][data-permission="${permission}"]`);
                if (directCards.length) {
                    directCards.addClass('active');
                    markedCount += directCards.length;
                }

                // 1.ب. تحديد البطاقات في القسم المناسب
                const sectionCards = $(`#section-${section} .permission-card`);
                sectionCards.each(function() {
                    // تحقق مما إذا كانت البطاقة تطابق الصلاحية
                    const cardPerm = $(this).data('permission');
                    if (cardPerm === permission && !$(this).hasClass('active')) {
                        $(this).addClass('active');
                        markedCount++;
                    }
                    
                    // تحقق من عنوان البطاقة
                    const titleEl = $(this).find('.permission-title');
                    if (titleEl.length) {
                        const permName = titleEl.data('perm-name');
                        if (permName === permission && !$(this).hasClass('active')) {
                            $(this).addClass('active');
                            markedCount++;
                        }
                    }
                });

                // 1.ج. البحث عن طريق عنوان الصلاحية - احتياطي
                const titleCards = $(`.permission-card .permission-title[data-perm-name="${permission}"]`).closest('.permission-card');
                if (titleCards.length) {
                    titleCards.addClass('active');
                    markedCount += titleCards.length;
                }
                
                totalMarked += markedCount;
                console.log(`  ┗ تم تعليم ${markedCount} بطاقة للصلاحية ${permission}`);
            });
        }
    }
    
    // 2. من أجل البطاقات التي لا تحتوي على سمات بيانات كاملة، استخدم الطريقة الاحتياطية
    $('.permissions-section').each(function() {
        const sectionId = $(this).attr('id').replace('section-', '');
        const sectionPerms = window.savedPermissions[sectionId] || [];
        
        if (Array.isArray(sectionPerms) && sectionPerms.length > 0) {
            $(this).find('.permission-card:not(.active)').each(function() {
                // محاولة استنتاج الصلاحية من نص البطاقة
                const titleText = $(this).find('.permission-title').text().trim();
                const permDesc = $(this).find('.permission-desc').text().trim();
                
                // مطابقة أي من الصلاحيات المحفوظة للقسم
                sectionPerms.forEach(permission => {
                    // محاولة مطابقة الصلاحية بالنص
                    if ((titleText && permission.includes(titleText.toLowerCase())) || 
                        (permDesc && permission.includes(permDesc.toLowerCase()))) {
                        $(this).addClass('active');
                        totalMarked++;
                    }
                });
            });
        }
    });
    
    // حساب التغييرات
    const activeAfter = $('.permission-card.active').length;
    console.log(`⏱️ انتهاء تعليم البطاقات - النتيجة: ${activeAfter} بطاقة نشطة (تغيير: ${activeAfter - activeBefore})`);
    
    // تحديث عدادات الصلاحيات في كل قسم وتبويب
    if (typeof updateAllCounters === 'function') {
        updateAllCounters();
    } else {
        console.warn("⚠️ الدالة updateAllCounters غير معرفة! تأكد من تضمين ملف permissions_counters.js");
    }
    
    // حساب إجمالي عدد الصلاحيات المحفوظة
    let totalPermissionsCount = 0;
    for (const section in window.savedPermissions) {
        if (Array.isArray(window.savedPermissions[section])) {
            totalPermissionsCount += window.savedPermissions[section].length;
        }
    }
    
    // التحقق من تطابق عدد البطاقات النشطة مع عدد الصلاحيات
    if (activeAfter < totalPermissionsCount) {
        console.warn(`⚠️ تحذير: ${totalPermissionsCount - activeAfter} صلاحية لم يتم تفعيل بطاقاتها`);
    } else if (activeAfter > totalPermissionsCount) {
        console.warn(`⚠️ تحذير: ${activeAfter - totalPermissionsCount} بطاقة زائدة تم تفعيلها`);
    } else {
        console.log(`✅ تمت مطابقة جميع الصلاحيات (${totalPermissionsCount}) مع البطاقات النشطة`);
    }
}

// تعريف متغير عام على مستوى النافذة
window.savedPermissions = {};

// تهيئة المتغير العام
$(document).ready(function() {
    try {
        const permissionsJson = $('#saved_permissions_json').val();
        if (permissionsJson) {
            window.savedPermissions = JSON.parse(permissionsJson);
            console.log("✅ تم تحميل الصلاحيات المحفوظة العامة:", window.savedPermissions);
        }
    } catch (error) {
        console.error("❌ خطأ في تحليل الصلاحيات المحفوظة:", error);
    }
    
    // تشخيص سمات بطاقات الصلاحيات
    setTimeout(function() {
        console.log("🔍 تشخيص بنية بطاقات الصلاحيات...");
        console.log(`📊 عدد البطاقات الكلي: ${$('.permission-card').length}`);
        console.log(`📊 عدد البطاقات النشطة: ${$('.permission-card.active').length}`);
        
        // فحص سمات البطاقات
        const cardAttributes = {};
        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            cardAttributes[sectionId] = [];
            
            $(this).find('.permission-card').each(function(index) {
                const card = $(this);
                const cardData = {
                    index,
                    active: card.hasClass('active'),
                    dataSection: card.data('section'),
                    dataPermission: card.data('permission'),
                    titleText: card.find('.permission-title').text().trim(),
                    titlePerm: card.find('.permission-title').data('perm-name')
                };
                
                // إذا كانت البطاقة نشطة، أضف معلومات إضافية
                if (cardData.active) {
                    cardData.activeStyle = true;
                }
                
                // إذا كانت السمات غير متطابقة مع القسم
                if (cardData.dataSection !== sectionId) {
                    cardData.sectionMismatch = true;
                }
                
                cardAttributes[sectionId].push(cardData);
            });
        });
        
        console.log("📝 معلومات بطاقات الصلاحيات حسب الأقسام:", cardAttributes);
        
        // طباعة البطاقات التي تفتقد إلى سمات
        const missingAttributes = $('.permission-card').filter(function() {
            return !$(this).data('permission') || !$(this).data('section');
        });
        
        if (missingAttributes.length) {
            console.warn(`⚠️ توجد ${missingAttributes.length} بطاقة بدون سمات بيانات كاملة`);
            
            missingAttributes.each(function(index) {
                console.log(`  بطاقة #${index} بدون سمات كاملة:`, {
                    title: $(this).find('.permission-title').text().trim(),
                    dataSection: $(this).data('section'),
                    dataPermission: $(this).data('permission')
                });
            });
        } else {
            console.log("✅ جميع البطاقات تحتوي على سمات البيانات المطلوبة");
        }
    }, 1000);
});