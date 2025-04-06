document.addEventListener('DOMContentLoaded', function() {
    // View switching (grid vs list)
    const gridViewBtn = document.getElementById('gridViewBtn');
    const listViewBtn = document.getElementById('listViewBtn');
    const gridView = document.getElementById('gridView');
    const listView = document.getElementById('listView');
    
    if (gridViewBtn && listViewBtn) {
        gridViewBtn.addEventListener('click', function() {
            gridView.classList.remove('d-none');
            listView.classList.add('d-none');
            gridViewBtn.classList.add('active');
            listViewBtn.classList.remove('active');
            localStorage.setItem('carViewPreference', 'grid');
        });
        
        listViewBtn.addEventListener('click', function() {
            listView.classList.remove('d-none');
            gridView.classList.add('d-none');
            listViewBtn.classList.add('active');
            gridViewBtn.classList.remove('active');
            localStorage.setItem('carViewPreference', 'list');
        });
        
        // Check if user has a saved preference
        const viewPreference = localStorage.getItem('carViewPreference');
        if (viewPreference === 'list') {
            listViewBtn.click();
        }
    }
    
    // Style form elements
    const selects = document.querySelectorAll('select');
    selects.forEach(function(select) {
        select.classList.add('form-select');
    });
    
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(function(input) {
        input.classList.add('form-control');
    });
    
    // Add animation to cars as they scroll into view
    const carCards = document.querySelectorAll('.car-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    carCards.forEach((card) => {
        observer.observe(card);
    });
    
    // Price range slider functionality
    const minPriceInput = document.getElementById('id_min_price');
    const maxPriceInput = document.getElementById('id_max_price');
    
    if (minPriceInput && maxPriceInput) {
        // Update max price min attribute when min price changes
        minPriceInput.addEventListener('change', function() {
            if (minPriceInput.value) {
                maxPriceInput.setAttribute('min', minPriceInput.value);
            } else {
                maxPriceInput.removeAttribute('min');
            }
        });
        
        // Update min price max attribute when max price changes
        maxPriceInput.addEventListener('change', function() {
            if (maxPriceInput.value) {
                minPriceInput.setAttribute('max', maxPriceInput.value);
            } else {
                minPriceInput.removeAttribute('max');
            }
        });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Handle category filter clicks
    const categoryButtons = document.querySelectorAll('.category-filter');
    
    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            const categorySelect = document.querySelector('#id_category');
            
            if (categorySelect) {
                categorySelect.value = category;
                document.querySelector('form').submit();
            }
        });
    });
});

// Animated counter for results count
function animateCounter(element, target, duration = 1000) {
    let start = 0;
    const increment = target > 0 ? Math.ceil(target / (duration / 16)) : 0;
    
    const timer = setInterval(() => {
        start += increment;
        element.textContent = start;
        
        if (start >= target) {
            element.textContent = target;
            clearInterval(timer);
        }
    }, 16);
}

// Initialize counter animation when the page loads
const resultsCount = document.querySelector('.results-count');
if (resultsCount) {
    const targetCount = parseInt(resultsCount.getAttribute('data-count'), 10);
    animateCounter(resultsCount, targetCount);
}
