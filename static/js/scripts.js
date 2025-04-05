// Wait for the document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Mobile navigation toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            navbarCollapse.classList.toggle('show');
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== "#" && href.startsWith('#')) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Filter form in cars page - auto submit on change
    const filterForms = document.querySelectorAll('.search-form select, .search-form input[type="checkbox"]');
    filterForms.forEach(input => {
        input.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });

    // Form validation styles
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Image preview for car form
    const imageUrlInput = document.getElementById('image_url');
    const imagePreview = document.getElementById('image_preview');
    
    if (imageUrlInput && imagePreview) {
        imageUrlInput.addEventListener('change', function() {
            if (this.value) {
                imagePreview.src = this.value;
                imagePreview.classList.remove('d-none');
            } else {
                imagePreview.classList.add('d-none');
            }
        });
    }

    // Auto calculate price in reservation form
    const calculatePrice = function() {
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');
        const priceDisplay = document.getElementById('calculated_price');
        const dailyRateEl = document.getElementById('daily_rate');
        
        if (startDateInput && endDateInput && priceDisplay && dailyRateEl) {
            const startDate = new Date(startDateInput.value);
            const endDate = new Date(endDateInput.value);
            const dailyRate = parseFloat(dailyRateEl.textContent);
            
            if (!isNaN(startDate.getTime()) && !isNaN(endDate.getTime()) && dailyRate) {
                // Calculate days (add 1 since end date is inclusive)
                const diffTime = Math.abs(endDate - startDate);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                
                if (diffDays >= 0) {
                    const totalPrice = diffDays * dailyRate;
                    priceDisplay.textContent = `$${totalPrice.toFixed(2)}`;
                }
            }
        }
    };

    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput) {
        startDateInput.addEventListener('change', calculatePrice);
    }
    
    if (endDateInput) {
        endDateInput.addEventListener('change', calculatePrice);
    }

    // Run once on page load
    calculatePrice();

    // Initialize dark mode based on stored preference
    const initDarkMode = function() {
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        if (isDarkMode) {
            document.body.setAttribute('data-theme', 'dark');
        } else {
            document.body.removeAttribute('data-theme');
        }
    };

    // Toggle dark mode
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            if (document.body.getAttribute('data-theme') === 'dark') {
                document.body.removeAttribute('data-theme');
                localStorage.setItem('darkMode', 'false');
            } else {
                document.body.setAttribute('data-theme', 'dark');
                localStorage.setItem('darkMode', 'true');
            }
        });
    }

    // Initialize dark mode on page load
    initDarkMode();
});
