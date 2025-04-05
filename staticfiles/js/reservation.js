document.addEventListener('DOMContentLoaded', function() {
    // Date inputs for reservation
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput) {
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
                
                // Enable end date selection
                endDateInput.disabled = false;
                
                // Calculate price
                calculateTotalPrice();
            }
        });
        
        // When end date changes, calculate price
        endDateInput.addEventListener('change', function() {
            if (endDateInput.value) {
                calculateTotalPrice();
            }
        });
        
        // On initial load, if start date has value, set min for end date
        if (startDateInput.value) {
            endDateInput.min = startDateInput.value;
            endDateInput.disabled = false;
        } else {
            // Disable end date until start date is selected
            endDateInput.disabled = true;
        }
        
        // Calculate total price based on selected dates and daily rate
        function calculateTotalPrice() {
            const priceElement = document.getElementById('total_price');
            const dailyRateElement = document.getElementById('daily_rate');
            
            if (priceElement && dailyRateElement && startDateInput.value && endDateInput.value) {
                const dailyRate = parseFloat(dailyRateElement.textContent);
                const startDate = new Date(startDateInput.value);
                const endDate = new Date(endDateInput.value);
                
                // Calculate number of days (add 1 because end date is inclusive)
                const timeDiff = Math.abs(endDate - startDate);
                const days = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)) + 1;
                
                // Calculate total price
                const totalPrice = dailyRate * days;
                
                // Update price display
                priceElement.textContent = `$${totalPrice.toFixed(2)}`;
                
                // Update hidden input if exists
                const totalPriceInput = document.getElementById('total_price_input');
                if (totalPriceInput) {
                    totalPriceInput.value = totalPrice.toFixed(2);
                }
            }
        }
        
        // Calculate price on page load if dates already set
        if (startDateInput.value && endDateInput.value) {
            calculateTotalPrice();
        }
    }
    
    // Remove item from cart confirmation
    const removeButtons = document.querySelectorAll('.remove-from-cart');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to remove this item from your cart?')) {
                e.preventDefault();
            }
        });
    });
    
    // Payment form validation
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            const cardNumber = document.getElementById('card_number');
            const cardName = document.getElementById('card_name');
            const cvv = document.getElementById('cvv');
            
            let isValid = true;
            
            // Validate card number (simple check for 16 digits)
            if (cardNumber && !/^\d{16}$/.test(cardNumber.value)) {
                isValid = false;
                showError(cardNumber, 'Please enter a valid 16-digit card number');
            } else if (cardNumber) {
                clearError(cardNumber);
            }
            
            // Validate card name
            if (cardName && cardName.value.trim() === '') {
                isValid = false;
                showError(cardName, 'Please enter the name on card');
            } else if (cardName) {
                clearError(cardName);
            }
            
            // Validate CVV (3-4 digits)
            if (cvv && !/^\d{3,4}$/.test(cvv.value)) {
                isValid = false;
                showError(cvv, 'Please enter a valid 3 or 4 digit CVV');
            } else if (cvv) {
                clearError(cvv);
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        function showError(inputElement, message) {
            // Clear any existing error
            clearError(inputElement);
            
            // Create and add error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = message;
            inputElement.classList.add('is-invalid');
            inputElement.parentNode.appendChild(errorDiv);
        }
        
        function clearError(inputElement) {
            inputElement.classList.remove('is-invalid');
            const errorDiv = inputElement.parentNode.querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.remove();
            }
        }
    }
});
