import re

with open("templates/car_detail_django.html", 'r', encoding='utf-8') as file:
    content = file.read()

update_summary_code = """
        // Quick booking form calculations
        const directBookingForm = document.getElementById("directBookingForm");
        if (directBookingForm) {
            const directStartDate = directBookingForm.querySelector('input[name="start_date"]');
            const directEndDate = directBookingForm.querySelector('input[name="end_date"]');
            const directBookingDays = document.getElementById("direct-booking-days");
            const directBookingTotal = document.getElementById("direct-booking-total");
            
            // Set min date for start date to today
            const today = new Date();
            const todayStr = today.toISOString().split('T')[0];
            directStartDate.min = todayStr;
            
            function updateDirectBookingSummary() {
                if (directStartDate.value && directEndDate.value) {
                    const startDate = new Date(directStartDate.value);
                    const endDate = new Date(directEndDate.value);
                    
                    // Calculate number of days (add 1 because end date is inclusive)
                    const timeDiff = Math.abs(endDate - startDate);
                    const days = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)) + 1;
                    
                    // Update days display
                    directBookingDays.textContent = days + " يوم";
                    
                    // Calculate total price
                    const totalPrice = dailyRate * days;
                    
                    // Update total price display
                    directBookingTotal.textContent = totalPrice.toFixed(2) + " د.ك";
                }
            }
            
            // When start date changes, set min date for end date
            directStartDate.addEventListener('change', function() {
                if (directStartDate.value) {
                    // Set minimum end date to start date
                    directEndDate.min = directStartDate.value;
                    
                    // If end date is before start date, reset it
                    if (directEndDate.value && directEndDate.value < directStartDate.value) {
                        directEndDate.value = directStartDate.value;
                    }
                    
                    // Calculate price
                    updateDirectBookingSummary();
                }
            });
            
            // When end date changes, calculate price
            directEndDate.addEventListener('change', function() {
                if (directEndDate.value) {
                    updateDirectBookingSummary();
                }
            });
            
            // Calculate on page load if both dates already set
            if (directStartDate.value && directEndDate.value) {
                updateDirectBookingSummary();
            }
        }"""

# Find the right position to insert, right after document.addEventListener('DOMContentLoaded'...
pattern = r'document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s+'
match = re.search(pattern, content)

if match:
    # Insert after the opening of the event listener function
    insert_position = match.end()
    new_content = content[:insert_position] + update_summary_code + content[insert_position:]
    
    with open("templates/car_detail_django.html", 'w', encoding='utf-8') as file:
        file.write(new_content)
    print("Successfully added quick booking summary calculation code")
else:
    print("Could not find the DOM content loaded event listener")
