/**
 * Fixed Navigation JavaScript
 * This script helps to keep the sidebar and top navigation fixed and prevents them from refreshing
 */

document.addEventListener('DOMContentLoaded', function() {
    // Function to ensure the sidebar stays in position when clicking links
    const sidebarLinks = document.querySelectorAll('.admin-sidebar .nav-link');
    
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
        if (document.querySelector('.admin-sidebar')) {
            sessionStorage.setItem('sidebarScrollPosition', 
                document.querySelector('.admin-sidebar').scrollTop);
        }
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
});