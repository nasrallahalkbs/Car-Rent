#!/usr/bin/env python3

with open('templates/car_detail_django.html', 'r', encoding='utf-8') as file:
    content = file.read()

# Fix the duplicate code
content = content.replace("""                    if (!data.dates || data.dates.length === 0) {
                        unavailableDatesContainer.innerHTML = '<p class="text-success mb-0 text-center py-4"><i class="fas fa-check-circle ms-2"></i>لا توجد تواريخ محجوزة حالياً!</p>';
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
                                <i class="fas fa-calendar-times date-range-icon"></i>
                                <div class="date-range-text">${formattedStartDate} - ${formattedEndDate}</div>
                            </div>`;
                        });
                        
                        unavailableDatesContainer.innerHTML = html;
                    }
                })
                .catch(error => {
                    console.error('Error fetching unavailable dates:', error);
                    const unavailableDatesContainer = document.getElementById('unavailableDates');
                    unavailableDatesContainer.innerHTML = '<p class="text-danger mb-0 text-center py-4"><i class="fas fa-exclamation-circle ms-2"></i>حدث خطأ أثناء تحميل التواريخ المحجوزة</p>';
                });
        } catch (err) {
            console.error('Error in fetch operation:', err);
            const unavailableDatesContainer = document.getElementById('unavailableDates');
            unavailableDatesContainer.innerHTML = '<p class="text-danger mb-0 text-center py-4"><i class="fas fa-exclamation-circle ms-2"></i>حدث خطأ أثناء تحميل التواريخ المحجوزة</p>';
        }""", """                })
                .catch(error => {
                    console.error("Error fetching unavailable dates:", error);
                    const unavailableDatesContainer = document.getElementById("unavailableDates");
                    unavailableDatesContainer.innerHTML = '<p class="text-danger mb-0 text-center py-4"><i class="fas fa-exclamation-circle ms-2"></i>حدث خطأ أثناء تحميل التواريخ المحجوزة</p>';
                });
        } catch (err) {
            console.error("Error in fetch operation:", err);
            const unavailableDatesContainer = document.getElementById("unavailableDates");
            unavailableDatesContainer.innerHTML = '<p class="text-danger mb-0 text-center py-4"><i class="fas fa-exclamation-circle ms-2"></i>حدث خطأ أثناء تحميل التواريخ المحجوزة</p>';
        }
        
        // Direct booking form functionality
        const directBookingForm = document.getElementById("directBookingForm");
        if (directBookingForm) {
            const directStartDate = directBookingForm.querySelector('input[name="start_date"]');
            const directEndDate = directBookingForm.querySelector('input[name="end_date"]');
            const directBookingDays = document.getElementById("direct-booking-days");
            const directBookingTotal = document.getElementById("direct-booking-total");
            
            function updateDirectBookingSummary() {
                if (directStartDate.value && directEndDate.value) {
                    const startDate = new Date(directStartDate.value);
                    const endDate = new Date(directEndDate.value);
                    
                    if (endDate >= startDate) {
                        // Calculate days difference
                        const diffTime = Math.abs(endDate - startDate);
                        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
                        
                        // Update UI
                        directBookingDays.textContent = diffDays + " أيام";
                        directBookingTotal.textContent = (diffDays * dailyRate).toFixed(2) + " د.ك";
                    } else {
                        directBookingDays.textContent = "-- أيام";
                        directBookingTotal.textContent = "-- د.ك";
                    }
                } else {
                    directBookingDays.textContent = "-- أيام";
                    directBookingTotal.textContent = "-- د.ك";
                }
            }
            
            directStartDate.addEventListener('change', updateDirectBookingSummary);
            directEndDate.addEventListener('change', updateDirectBookingSummary);
            
            // Card image preview
            const cardImageInput = directBookingForm.querySelector('input[name="card_image"]');
            if (cardImageInput) {
                cardImageInput.addEventListener('change', function(e) {
                    if (this.files && this.files[0]) {
                        // Create preview if doesn't exist
                        let previewContainer = directBookingForm.querySelector('.card-image-preview');
                        
                        if (!previewContainer) {
                            previewContainer = document.createElement('div');
                            previewContainer.className = 'card-image-preview mt-2 text-center';
                            previewContainer.innerHTML = '<p class="mb-1 text-success"><i class="fas fa-check-circle me-1"></i> تم تحميل الصورة بنجاح</p>';
                            
                            const imagePreview = document.createElement('img');
                            imagePreview.className = 'img-thumbnail';
                            imagePreview.style.maxHeight = '150px';
                            previewContainer.appendChild(imagePreview);
                            
                            cardImageInput.parentNode.appendChild(previewContainer);
                        }
                        
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            previewContainer.querySelector('img').src = e.target.result;
                        }
                        reader.readAsDataURL(this.files[0]);
                    }
                });
            }
            
            // Form validation
            directBookingForm.addEventListener('submit', function(e) {
                if (!directStartDate.value || !directEndDate.value) {
                    e.preventDefault();
                    alert("يرجى تحديد تاريخ الاستلام وتاريخ التسليم");
                    return false;
                }
                
                const startDate = new Date(directStartDate.value);
                const endDate = new Date(directEndDate.value);
                
                if (endDate < startDate) {
                    e.preventDefault();
                    alert("يجب أن يكون تاريخ التسليم بعد تاريخ الاستلام");
                    return false;
                }
                
                const cardNumber = directBookingForm.querySelector('input[name="card_number"]').value;
                const cardName = directBookingForm.querySelector('input[name="card_name"]').value;
                const expiryMonth = directBookingForm.querySelector('select[name="expiry_month"]').value;
                const expiryYear = directBookingForm.querySelector('select[name="expiry_year"]').value;
                const cvv = directBookingForm.querySelector('input[name="cvv"]').value;
                
                if (!cardNumber || !cardName || !expiryMonth || !expiryYear || !cvv) {
                    e.preventDefault();
                    alert("يرجى إدخال جميع معلومات الدفع المطلوبة");
                    return false;
                }
                
                if (!/^\d{16}$/.test(cardNumber.replace(/\s/g, ''))) {
                    e.preventDefault();
                    alert("يرجى إدخال رقم بطاقة صحيح (16 رقم)");
                    return false;
                }
                
                if (!/^\d{3,4}$/.test(cvv)) {
                    e.preventDefault();
                    alert("يرجى إدخال رمز أمان صحيح (3-4 أرقام)");
                    return false;
                }
                
                return true;
            });
        }""")

with open('templates/car_detail_django.html', 'w', encoding='utf-8') as file:
    file.write(content)

print("File fixed successfully!")
