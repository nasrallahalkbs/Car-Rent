#!/usr/bin/env python

"""
تصحيح صفحة تفاصيل السيارة وإزالة رموز JavaScript غير المتوازنة 
هذا السكربت يقوم بتنظيف كود جافا سكريبت غير مستخدم وإصلاح الأخطاء البرمجية
"""

import re
import os

def process_file():
    """Process the car detail template file"""
    template_path = "templates/car_detail_django.html"
    
    # Make sure the file exists
    if not os.path.exists(template_path):
        print(f"Error: {template_path} does not exist")
        return False
    
    # Read the file
    with open(template_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Clean up the JavaScript
    updated_content = clean_javascript(content)
    
    # Write the changes back to the file
    with open(template_path, "w", encoding="utf-8") as file:
        file.write(updated_content)
    
    print(f"Successfully updated {template_path}")
    return True

def clean_javascript(content):
    """Clean up the JavaScript code and fix unbalanced brackets"""
    # Find the script block
    script_pattern = r'{% block extra_js %}(.*?){% endblock %}'
    script_match = re.search(script_pattern, content, re.DOTALL)
    
    if not script_match:
        print("Script block not found")
        return content
    
    script_content = script_match.group(1)
    
    # Remove unbalanced brackets and unused code
    script_block = """
<script src="{% static 'js/car-detail-animations.js' %}"></script>
<script src="{% static 'js/reservation.js' %}"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Validate main booking form before submit
        const bookNowForm = document.getElementById('bookNowForm');
        if (bookNowForm) {
            const startDate = bookNowForm.querySelector('#start_date');
            const endDate = bookNowForm.querySelector('#end_date');
            
            bookNowForm.addEventListener('submit', function(e) {
                if (!startDate.value || !endDate.value) {
                    e.preventDefault();
                    alert("يرجى تحديد تاريخ الاستلام وتاريخ التسليم");
                    return false;
                }
                
                // Check that end date is not before start date
                const startDateValue = new Date(startDate.value);
                const endDateValue = new Date(endDate.value);
                if (endDateValue < startDateValue) {
                    e.preventDefault();
                    alert("يجب أن يكون تاريخ التسليم بعد تاريخ الاستلام");
                    return false;
                }
                
                return true;
            });
        }
        
        // Fetch unavailable dates
        const carId = {{ car.id |escapejs }};
        const dailyRate = {{ car.daily_rate |escapejs }};
        const unavailableDatesContainer = document.getElementById('unavailableDates');
        
        try {
            fetch(`/api/car/${carId}/unavailable-dates/`)
                .then(response => response.json())
                .then(data => {
                    if (!data.dates || data.dates.length === 0) {
                        unavailableDatesContainer.innerHTML = '<p class="text-success mb-0 text-center py-4"><i class="fas fa-check-circle ms-2"></i> لا توجد تواريخ محجوزة حالياً!</p>';
                    } else {
                        let html = '';
                        
                        data.dates.forEach(dateRange => {
                            const startDate = new Date(dateRange[0]);
                            const endDate = new Date(dateRange[1]);
                            
                            const formattedStartDate = startDate.toLocaleDateString('ar-SA', { 
                                year: 'numeric', month: 'long', day: 'numeric' 
                            });
                            const formattedEndDate = endDate.toLocaleDateString('ar-SA', { 
                                year: 'numeric', month: 'long', day: 'numeric' 
                            });
                            
                            html += `
                            <div class="date-range-item">
                                <i class="fas fa-calendar-times date-range-icon"></i>  <div class="date-range-text">${formattedStartDate} - ${formattedEndDate}</div>
                            </div>`;
                        });
                        
                        unavailableDatesContainer.innerHTML = html;
                    }
                })
                .catch(error => {
                    console.error("Error fetching unavailable dates:", error);
                    const unavailableDatesContainer = document.getElementById("unavailableDates");
                    unavailableDatesContainer.innerHTML = '<p class="text-danger mb-0 text-center py-4"><i class="fas fa-exclamation-circle ms-2"></i> حدث خطأ أثناء تحميل التواريخ المحجوزة</p>';
                });
        } catch (err) {
            console.error("Error in fetch operation:", err);
            const unavailableDatesContainer = document.getElementById("unavailableDates");
            unavailableDatesContainer.innerHTML = '<p class="text-danger mb-0 text-center py-4"><i class="fas fa-exclamation-circle ms-2"></i> حدث خطأ أثناء تحميل التواريخ المحجوزة</p>';
        }
    });
</script>"""
    
    # Replace the script block
    return content.replace(script_match.group(0), "{% block extra_js %}" + script_block + "{% endblock %}")

if __name__ == "__main__":
    process_file()
