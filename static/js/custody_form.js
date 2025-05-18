// سكريبت التحكم في نموذج العهدة
document.addEventListener('DOMContentLoaded', function() {
    // الحصول على عناصر النموذج
    var guaranteeTypeField = document.getElementById('id_guarantee_type');
    var valueField = document.getElementById('id_value');
    var valueFormGroup = valueField ? valueField.closest('.form-group') : null;
    var creditCardField = document.getElementById('id_credit_card_info');
    var creditCardFormGroup = creditCardField ? creditCardField.closest('.form-group') : null;
    var propertyField = document.getElementById('id_property_description');
    var propertyFormGroup = propertyField ? propertyField.closest('.form-group') : null;
    var insuranceField = document.getElementById('id_insurance_policy_number');
    var insuranceFormGroup = insuranceField ? insuranceField.closest('.form-group') : null;
    
    // طباعة حالة العناصر للتصحيح
    console.log("تم العثور على حقل القيمة:", valueFormGroup !== null);
    console.log("تم العثور على حقل البطاقة الائتمانية:", creditCardFormGroup !== null);
    console.log("تم العثور على حقل وصف الممتلكات:", propertyFormGroup !== null);
    console.log("تم العثور على حقل رقم التأمين:", insuranceFormGroup !== null);
    
    // تحديث إظهار/إخفاء الحقول بناءً على نوع العهدة
    function updateFieldsVisibility() {
        if (!guaranteeTypeField) return;
        
        var guaranteeType = guaranteeTypeField.value;
        console.log("نوع العهدة المختار:", guaranteeType);
        
        // إخفاء جميع الحقول المخصصة أولاً
        if (creditCardFormGroup) creditCardFormGroup.style.display = 'none';
        if (propertyFormGroup) propertyFormGroup.style.display = 'none';
        if (insuranceFormGroup) insuranceFormGroup.style.display = 'none';
        
        // أنواع العهدات التي تتطلب حقل القيمة
        var typesRequiringValue = ['cash', 'bank_deposit', 'other'];
        
        // إظهار/إخفاء حقل القيمة
        if (valueFormGroup) {
            if (typesRequiringValue.includes(guaranteeType)) {
                valueFormGroup.style.display = '';
                console.log("تم إظهار حقل القيمة");
            } else {
                valueFormGroup.style.display = 'none';
                if (valueField) valueField.value = '0';
                console.log("تم إخفاء حقل القيمة وتعيينه إلى 0");
            }
        }
        
        // إظهار الحقل المناسب حسب نوع العهدة
        switch (guaranteeType) {
            case 'credit_card':
                if (creditCardFormGroup) {
                    creditCardFormGroup.style.display = '';
                    console.log("تم إظهار حقل معلومات البطاقة الائتمانية");
                }
                break;
            case 'property':
                if (propertyFormGroup) {
                    propertyFormGroup.style.display = '';
                    console.log("تم إظهار حقل وصف الممتلكات العقارية");
                }
                break;
            case 'insurance':
                if (insuranceFormGroup) {
                    insuranceFormGroup.style.display = '';
                    console.log("تم إظهار حقل رقم بوليصة التأمين");
                }
                break;
        }
    }
    
    // تسجيل المستمع للاستماع إلى تغييرات نوع العهدة
    if (guaranteeTypeField) {
        guaranteeTypeField.addEventListener('change', updateFieldsVisibility);
        // تنفيذ الدالة عند تحميل الصفحة
        updateFieldsVisibility();
    }
    
    // تحديث بيانات الحجز عند تغيير الحجز
    var reservationField = document.getElementById('id_reservation');
    if (reservationField) {
        reservationField.addEventListener('change', function() {
            console.log("تم تغيير الحجز إلى:", this.value);
            // يمكن إضافة أي منطق إضافي هنا عند الحاجة
        });
    }
});