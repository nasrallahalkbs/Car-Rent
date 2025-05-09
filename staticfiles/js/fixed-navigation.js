/**
 * Fixed Navigation JavaScript
 * This script helps to keep the sidebar and top navigation fixed and prevents them from refreshing
 */

document.addEventListener('DOMContentLoaded', function() {
    // Function to ensure the sidebar stays in position when clicking links
    const sidebarLinks = document.querySelectorAll('.admin-sidebar .nav-link');
    
    // Capture the initial state of sidebar and navigation
    const captureInitialState = () => {
        if (document.querySelector('.admin-sidebar')) {
            // Store structure of sidebar (for potential restoration)
            sessionStorage.setItem('sidebarHTML', document.querySelector('.admin-sidebar').innerHTML);
            
            // Store current scroll position
            sessionStorage.setItem('sidebarScrollPosition', 
                document.querySelector('.admin-sidebar').scrollTop);
            
            // Store active states
            document.querySelectorAll('.admin-sidebar .nav-link.active').forEach((activeLink, index) => {
                sessionStorage.setItem(`activeLink_${index}`, activeLink.getAttribute('href'));
            });
        }
        
        // Store top navigation state
        if (document.querySelector('.navbar.sticky-top')) {
            sessionStorage.setItem('navbarHTML', document.querySelector('.navbar.sticky-top').innerHTML);
        }
    };
    
    // Capture initial state when page loads
    captureInitialState();
    
    // Apply click handlers to all sidebar links
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Only apply to links in the same site (not external)
            if (link.getAttribute('href').startsWith('/') || 
                link.getAttribute('href').startsWith(window.location.origin)) {
                
                // Store current scroll position of sidebar
                sessionStorage.setItem('sidebarScrollPosition', 
                    document.querySelector('.admin-sidebar').scrollTop);
                
                // Store the active link
                sessionStorage.setItem('activeNavLink', link.getAttribute('href'));
                
                // Prevent default navigation for internal links
                // This forces AJAX-like navigation without page refresh
                if (e.ctrlKey || e.metaKey) {
                    // Allow normal behavior for ctrl/cmd+click (new tab)
                    return true;
                }
                
                // Capture current state before navigation
                captureInitialState();
            }
        });
    });
    
    // Restore sidebar scroll position
    const storedScrollPosition = sessionStorage.getItem('sidebarScrollPosition');
    if (storedScrollPosition) {
        const sidebar = document.querySelector('.admin-sidebar');
        if (sidebar) {
            sidebar.scrollTop = parseInt(storedScrollPosition);
        }
    }
    
    // Fix for Firefox which might reload the page and lose the styles
    window.addEventListener('beforeunload', function() {
        // Save current sidebar state before page reloads
        captureInitialState();
    });
    
    // Fix issues with browser back button
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            // Page was restored from cache (browser back/forward)
            const sidebar = document.querySelector('.admin-sidebar');
            const storedPosition = sessionStorage.getItem('sidebarScrollPosition');
            
            if (sidebar && storedPosition) {
                sidebar.scrollTop = parseInt(storedPosition);
            }
        }
    });
    
    // Apply custom class to help prevent refreshing
    document.querySelectorAll('.admin-sidebar, .navbar.sticky-top').forEach(el => {
        el.classList.add('fixed-no-refresh');
    });
});