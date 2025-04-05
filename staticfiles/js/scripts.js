// General Scripts for Car Rental Website

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Reservation form validation
    const reservationForm = document.getElementById('reservationForm');
    if (reservationForm) {
        reservationForm.addEventListener('submit', function(event) {
            const startDate = document.getElementById('id_start_date').value;
            const endDate = document.getElementById('id_end_date').value;
            
            if (!startDate || !endDate) {
                event.preventDefault();
                alert('Please select both pick-up and return dates.');
                return false;
            }
            
            const start = new Date(startDate);
            const end = new Date(endDate);
            
            if (end < start) {
                event.preventDefault();
                alert('Return date must be after pick-up date.');
                return false;
            }
        });
    }
    
    // Checkout form validation
    const checkoutForm = document.getElementById('checkoutForm');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(event) {
            const cardNumber = document.getElementById('id_card_number').value;
            const cardName = document.getElementById('id_card_name').value;
            const cvv = document.getElementById('id_cvv').value;
            
            if (!cardNumber || !cardName || !cvv) {
                event.preventDefault();
                alert('Please fill in all payment details.');
                return false;
            }
            
            if (!/^\d{16}$/.test(cardNumber)) {
                event.preventDefault();
                alert('Card number must be 16 digits.');
                return false;
            }
            
            if (!/^\d{3,4}$/.test(cvv)) {
                event.preventDefault();
                alert('CVV must be 3 or 4 digits.');
                return false;
            }
        });
    }
    
    // Animated scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
