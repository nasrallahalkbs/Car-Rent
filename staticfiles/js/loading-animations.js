/**
 * Car Rental Loading Animations
 * Provides animated loading screens with car-themed transitions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Create loading overlay elements
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    
    // Create car animation elements
    const carAnimation = document.createElement('div');
    carAnimation.className = 'car-animation';
    
    // Create car parts
    const carBody = document.createElement('div');
    carBody.className = 'car-body';
    
    const carRoof = document.createElement('div');
    carRoof.className = 'car-roof';
    
    const wheelLeft = document.createElement('div');
    wheelLeft.className = 'wheel wheel-left';
    
    const wheelRight = document.createElement('div');
    wheelRight.className = 'wheel wheel-right';
    
    const road = document.createElement('div');
    road.className = 'road';
    
    const roadMarks = document.createElement('div');
    roadMarks.className = 'road-marks';
    
    // Create road markings
    for (let i = 0; i < 5; i++) {
        const roadMark = document.createElement('div');
        roadMark.className = 'road-mark';
        roadMarks.appendChild(roadMark);
    }
    
    // Create headlights
    const headlightLeft = document.createElement('div');
    headlightLeft.className = 'headlight headlight-left';
    
    const headlightRight = document.createElement('div');
    headlightRight.className = 'headlight headlight-right';
    
    const beamLeft = document.createElement('div');
    beamLeft.className = 'headlight-beam beam-left';
    
    const beamRight = document.createElement('div');
    beamRight.className = 'headlight-beam beam-right';
    
    // Create smoke effects
    for (let i = 0; i < 3; i++) {
        const smoke = document.createElement('div');
        smoke.className = 'smoke';
        carAnimation.appendChild(smoke);
    }
    
    // Add car parts to animation
    carAnimation.appendChild(carBody);
    carAnimation.appendChild(carRoof);
    carAnimation.appendChild(wheelLeft);
    carAnimation.appendChild(wheelRight);
    carAnimation.appendChild(road);
    carAnimation.appendChild(roadMarks);
    carAnimation.appendChild(headlightLeft);
    carAnimation.appendChild(headlightRight);
    carAnimation.appendChild(beamLeft);
    carAnimation.appendChild(beamRight);
    
    // Create loading text
    const loadingText = document.createElement('div');
    loadingText.className = 'loading-text';
    loadingText.textContent = 'Loading...';
    
    // Create loading progress bar
    const loadingProgress = document.createElement('div');
    loadingProgress.className = 'loading-progress';
    
    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar';
    loadingProgress.appendChild(progressBar);
    
    // Assemble loading overlay
    loadingOverlay.appendChild(carAnimation);
    loadingOverlay.appendChild(loadingText);
    loadingOverlay.appendChild(loadingProgress);
    
    // Create page transition element
    const pageTransition = document.createElement('div');
    pageTransition.className = 'page-transition';
    
    // Add elements to the document
    document.body.appendChild(loadingOverlay);
    document.body.appendChild(pageTransition);
    
    // Show loading overlay
    loadingOverlay.classList.remove('hidden');
    
    // Hide loading overlay when page is fully loaded
    window.addEventListener('load', function() {
        setTimeout(function() {
            loadingOverlay.classList.add('hidden');
        }, 500);
    });
    
    // Initialize page transitions for links
    initializePageTransitions();
});

/**
 * Initializes page transition effects for all internal links
 */
function initializePageTransitions() {
    // Get all internal links (excluding external links and anchors)
    const internalLinks = document.querySelectorAll('a[href^="/"]:not([target="_blank"])');
    
    internalLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            // Don't handle if modifier keys are pressed (for opening in new tabs)
            if (event.ctrlKey || event.metaKey || event.shiftKey) {
                return;
            }
            
            event.preventDefault();
            
            const target = this.getAttribute('href');
            const pageTransition = document.querySelector('.page-transition');
            
            // If link contains car-detail, use zoom transition
            if (target.includes('car-detail') || target.includes('car_detail')) {
                performZoomTransition(target, event);
            } else {
                // Otherwise use slide transition
                performSlideTransition(target);
            }
        });
    });
}

/**
 * Performs a slide transition to a new page
 * @param {string} target - The URL to navigate to
 */
function performSlideTransition(target) {
    const pageTransition = document.querySelector('.page-transition');
    
    // Activate transition
    pageTransition.classList.add('active');
    
    // Navigate after transition completes
    setTimeout(function() {
        window.location.href = target;
    }, 500);
}

/**
 * Performs a zoom transition specifically for car detail pages
 * @param {string} target - The URL to navigate to
 * @param {Event} event - The click event
 */
function performZoomTransition(target, event) {
    // Get the clicked car element if possible
    const clickedElement = event.currentTarget;
    const carCard = clickedElement.closest('.car-card') || clickedElement.closest('.car-item');
    
    // Create a special zoom overlay
    const zoomOverlay = document.createElement('div');
    zoomOverlay.className = 'zoom-transition';
    document.body.appendChild(zoomOverlay);
    
    // If we have a car card, create a more advanced transition
    if (carCard) {
        // Get the image from the card
        const carImage = carCard.querySelector('img');
        
        if (carImage) {
            // Create a clone of the car image for the transition
            const transitionImage = document.createElement('img');
            transitionImage.src = carImage.src;
            transitionImage.className = 'car-transition-image';
            
            // Position the transition image over the original
            const rect = carImage.getBoundingClientRect();
            transitionImage.style.position = 'fixed';
            transitionImage.style.top = rect.top + 'px';
            transitionImage.style.left = rect.left + 'px';
            transitionImage.style.width = rect.width + 'px';
            transitionImage.style.height = rect.height + 'px';
            transitionImage.style.zIndex = '9999';
            transitionImage.style.borderRadius = '4px';
            transitionImage.style.transition = 'all 0.5s ease-in-out';
            
            // Add to the document
            document.body.appendChild(transitionImage);
            
            // Force reflow
            void transitionImage.offsetWidth;
            
            // Animate to center and larger size
            transitionImage.style.top = '50%';
            transitionImage.style.left = '50%';
            transitionImage.style.transform = 'translate(-50%, -50%) scale(1.5)';
            transitionImage.style.opacity = '0';
            
            // Create car silhouette animation around the image
            const carSilhouette = document.createElement('div');
            carSilhouette.className = 'car-silhouette';
            document.body.appendChild(carSilhouette);
            
            // Add exhaust particles animation
            const exhaustContainer = document.createElement('div');
            exhaustContainer.className = 'exhaust-container';
            document.body.appendChild(exhaustContainer);
            
            for (let i = 0; i < 8; i++) {
                const particle = document.createElement('div');
                particle.className = 'exhaust-particle';
                particle.style.animationDelay = (i * 0.1) + 's';
                exhaustContainer.appendChild(particle);
            }
            
            // Navigate after transition completes
            setTimeout(function() {
                window.location.href = target;
            }, 600);
            
            return;
        }
    }
    
    // Fallback to simple zoom if no car card was found
    // Force reflow
    void zoomOverlay.offsetWidth;
    
    // Activate zoom
    zoomOverlay.classList.add('active');
    
    // Navigate after transition completes
    setTimeout(function() {
        window.location.href = target;
    }, 500);
}

/**
 * Updates loading text during loading process
 * @param {string} text - The text to display
 */
function updateLoadingText(text) {
    const loadingText = document.querySelector('.loading-text');
    if (loadingText) {
        loadingText.textContent = text;
    }
}

/**
 * Shows a custom loading overlay with specific text
 * @param {string} text - The loading text to display
 */
function showCustomLoading(text) {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        updateLoadingText(text || 'Loading...');
        loadingOverlay.classList.remove('hidden');
        
        // Reset and restart progress bar animation
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.animation = 'none';
            void progressBar.offsetWidth; // Force reflow
            progressBar.style.animation = 'progress 2s ease-in-out forwards';
        }
    }
}

/**
 * Hides the loading overlay
 */
function hideLoading() {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.add('hidden');
    }
}

// Create custom loading triggers for specific actions
document.addEventListener('DOMContentLoaded', function() {
    // Show loading during form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            // Don't show for search forms
            if (!this.classList.contains('search-form')) {
                showCustomLoading('Processing...');
            }
        });
    });
    
    // Show loading during reservation actions
    const reserveButtons = document.querySelectorAll('.reserve-button, .checkout-button');
    reserveButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            showCustomLoading('Preparing your reservation...');
        });
    });
    
    // Add special animation for car detail page
    if (window.location.href.includes('car-detail') || window.location.href.includes('car_detail')) {
        // Add a car driving in animation when the page loads
        const carDetailContainer = document.querySelector('.car-detail-container');
        if (carDetailContainer) {
            carDetailContainer.classList.add('car-detail-entrance');
        }
        
        // Add animation to the car image
        const carImage = document.querySelector('.car-detail-image');
        if (carImage) {
            carImage.addEventListener('load', function() {
                this.classList.add('car-image-loaded');
            });
            
            // If image is already loaded
            if (carImage.complete) {
                carImage.classList.add('car-image-loaded');
            }
        }
    }
});

// Export functions for use in other scripts
window.carAnimations = {
    showLoading: showCustomLoading,
    hideLoading: hideLoading,
    updateLoadingText: updateLoadingText
};
