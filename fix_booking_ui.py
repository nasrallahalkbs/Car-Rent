"""
تحسين واجهة الحجز في صفحة تفاصيل السيارة
هذا السكربت يقوم بتبسيط واجهة الحجز وإزالة نموذج الحجز السريع
"""

import re

def process_file():
    # قراءة محتويات الملف
    with open('templates/car_detail_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن الجزء الذي نريد استبداله
    start_pattern = r'<div class="reservation-card-body">'
    end_pattern = r'{% endif %}\s+</div>\s+</div>\s+\s+<!-- Direct Booking Form -->.*?{% endif %}'
    
    # تحديد النص الذي نريد استبداله باستخدام تعبير منتظم
    pattern = start_pattern + r'(.*?)' + end_pattern
    
    # إنشاء نموذج الحجز الجديد
    replacement = '''<div class="reservation-card-body">
                    {% if car.is_available and user.is_authenticated %}
                    <form id="bookNowForm" method="post" action="{% url 'add_to_cart' %}">
                        {% csrf_token %}
                        <input type="hidden" name="car_id" value="{{ car.id }}">
                        <div class="row mb-3">
                            <div class="col-md-6 mb-3">
                                <label for="start_date" class="form-label">تاريخ الاستلام</label>
                                <input type="date" class="form-control" id="start_date" name="start_date" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="end_date" class="form-label">تاريخ التسليم</label>
                                <input type="date" class="form-control" id="end_date" name="end_date" required>
                            </div>
                        </div>
                        
                        <button type="submit" class="action-button d-block text-center text-decoration-none w-100 py-3">
                            <i class="fas fa-calendar-check ms-2"></i> طلب الحجز
                        </button>
                    </form>
                    {% elif car.is_available %}
                    <a href="{% url 'login' %}?next={% url 'car_detail' car_id=car.id %}" class="action-button d-block text-center text-decoration-none">
                        <i class="fas fa-user ms-2"></i> تسجيل الدخول للحجز
                    </a>
                    {% else %}
                    <div class="alert alert-warning mb-0">
                        <i class="fas fa-exclamation-triangle ms-2"></i> عذراً، هذه السيارة غير متاحة للحجز حالياً.
                    </div>
                    {% endif %}
                </div>
            </div>'''
    
    # استخدام re.DOTALL لمطابقة النص متعدد الأسطر
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # تحديث ملف القالب
    with open('templates/car_detail_django.html', 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    # تحديث كود JavaScript
    update_javascript(new_content)
    
    return True

def update_javascript(content):
    # البحث عن كود الـ directBookingForm وحذفه
    direct_booking_pattern = r'// Direct booking form functionality.*?const directBookingForm.*?\}\s+\}\s+\}'
    
    # استبدال كود directBookingForm بكود لنموذج الحجز الجديد
    new_js_code = '''
        // Booking form validation and date handling
        const bookNowForm = document.getElementById("bookNowForm");
        if (bookNowForm) {
            const startDateInput = bookNowForm.querySelector('input[name="start_date"]');
            const endDateInput = bookNowForm.querySelector('input[name="end_date"]');
            
            // Set min date for start date to today
            const today = new Date();
            const todayStr = today.toISOString().split('T')[0];
            startDateInput.min = todayStr;
            
            // When start date changes, set min date for end date
            startDateInput.addEventListener('change', function() {
                if (startDateInput.value) {
                    // Set minimum end date to start date
                    endDateInput.min = startDateInput.value;
                    
                    // If end date is before start date, reset it
                    if (endDateInput.value && endDateInput.value < startDateInput.value) {
                        endDateInput.value = startDateInput.value;
                    }
                }
            });
            
            // Form validation
            bookNowForm.addEventListener('submit', function(e) {
                if (!startDateInput.value || !endDateInput.value) {
                    e.preventDefault();
                    alert("يرجى تحديد تاريخ الاستلام وتاريخ التسليم");
                    return false;
                }
                
                // Check that end date is not before start date
                const startDate = new Date(startDateInput.value);
                const endDate = new Date(endDateInput.value);
                if (endDate < startDate) {
                    e.preventDefault();
                    alert("يجب أن يكون تاريخ التسليم بعد تاريخ الاستلام");
                    return false;
                }
                
                return true;
            });
        }
    '''
    
    # إزالة كود quickBookingForm
    quick_booking_pattern = r'// Quick booking form.*?const quickBookingForm.*?\}\s+\}\s+\}'
    
    # تنفيذ عمليات الاستبدال
    new_content = re.sub(direct_booking_pattern, new_js_code, content, flags=re.DOTALL)
    new_content = re.sub(quick_booking_pattern, '', new_content, flags=re.DOTALL)
    
    with open('templates/car_detail_django.html', 'w', encoding='utf-8') as file:
        file.write(new_content)

if __name__ == "__main__":
    if process_file():
        print("تم تحديث واجهة الحجز بنجاح!")
    else:
        print("حدث خطأ أثناء تحديث واجهة الحجز")