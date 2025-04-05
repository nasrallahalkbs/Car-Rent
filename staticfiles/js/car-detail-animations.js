/**
 * Car Detail Page Animations
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add classes to elements for animations
    const carImage = document.querySelector('.car-detail-image');
    const specItems = document.querySelectorAll('.car-spec-item');
    const featureItems = document.querySelectorAll('.feature-item, .features-list li');
    const reserveButton = document.querySelector('.reserve-button');
    const priceTag = document.querySelector('.price');
    const reviewItems = document.querySelectorAll('.review-item');
    const stars = document.querySelectorAll('.rating i');

    // Apply custom animations based on scroll position
    function animateOnScroll() {
        const scrollY = window.scrollY;
        const reviewSection = document.querySelector('.review-item')?.closest('.card');
        
        if (reviewSection) {
            const reviewSectionTop = reviewSection.getBoundingClientRect().top;
            
            // Animate reviews when they come into view
            if (reviewSectionTop < window.innerHeight * 0.8) {
                reviewItems.forEach((item, index) => {
                    setTimeout(() => {
                        item.style.animationDelay = '0s';
                        item.style.opacity = '1';
                        item.classList.add('animate__animated', 'animate__fadeIn');
                    }, index * 150);
                });
            }
        }
    }

    // Add interactive effects
    function addInteractiveEffects() {
        // Hover effect for car image
        if (carImage) {
            carImage.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.02)';
                this.style.transition = 'transform 0.3s ease';
            });
            
            carImage.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        }
        
        // Reservation button effect
        if (reserveButton) {
            reserveButton.addEventListener('mouseenter', function() {
                this.classList.add('pulse-animation');
            });
            
            reserveButton.addEventListener('mouseleave', function() {
                this.classList.remove('pulse-animation');
            });
        }
        
        // Price tag animation on hover
        if (priceTag) {
            priceTag.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.1)';
                this.style.transition = 'transform 0.2s ease';
                this.style.color = '#ff6b6b';
            });
            
            priceTag.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
                this.style.color = '';
            });
        }
    }

    // Apply dark mode specific animations
    function applyDarkModeAnimations() {
        const isDarkMode = document.body.classList.contains('dark-mode');
        const animationContainer = document.querySelector('.car-detail-container');
        
        if (animationContainer) {
            if (isDarkMode) {
                animationContainer.classList.add('dark-mode-animations');
            } else {
                animationContainer.classList.remove('dark-mode-animations');
            }
        }
    }
    
    // Initialize animations
    function init() {
        // Add window scroll listener for scroll-based animations
        window.addEventListener('scroll', animateOnScroll);
        
        // Apply interactive effects
        addInteractiveEffects();
        
        // Apply dark mode animations
        applyDarkModeAnimations();
        
        // Trigger initial animation on page load
        animateOnScroll();
        
        // Listen for dark mode toggle
        document.addEventListener('dark-mode-toggled', applyDarkModeAnimations);
    }
    
    // Run init function
    init();
});
