/**
 * Static Navigation Plugin
 * Prevents navigation elements from refreshing when changing pages
 */

(function($) {
    // Create a new jQuery plugin
    $.fn.staticNavigation = function(options) {
        // Default settings
        var settings = $.extend({
            sidebarSelector: '.admin-sidebar',
            topNavSelector: '.navbar.sticky-top',
            contentSelector: '.admin-content',
            activeClass: 'active',
            storagePrefix: 'staticNav_'
        }, options);
        
        return this.each(function() {
            var $this = $(this);
            
            // Store current state initially
            storeCurrentState();
            
            // Handle clicks on navigation links
            $(settings.sidebarSelector).find('a').on('click', function(e) {
                // Skip external links or ctrl/cmd+click (new tab)
                if (e.ctrlKey || e.metaKey || !isInternalLink($(this).attr('href'))) {
                    return true;
                }
                
                // Save state before navigation
                storeCurrentState();
                
                // Mark this link as the one that was clicked
                sessionStorage.setItem(settings.storagePrefix + 'clickedLink', $(this).attr('href'));
            });
            
            // On page load, restore previous state
            restoreState();
            
            // Functions
            function storeCurrentState() {
                // Save sidebar state
                if ($(settings.sidebarSelector).length) {
                    // Store HTML structure
                    sessionStorage.setItem(settings.storagePrefix + 'sidebarHTML', $(settings.sidebarSelector).html());
                    
                    // Store scroll position
                    sessionStorage.setItem(settings.storagePrefix + 'sidebarScroll', $(settings.sidebarSelector).scrollTop());
                    
                    // Store active links
                    var activeLinks = [];
                    $(settings.sidebarSelector).find('.' + settings.activeClass).each(function() {
                        activeLinks.push($(this).attr('href'));
                    });
                    sessionStorage.setItem(settings.storagePrefix + 'activeLinks', JSON.stringify(activeLinks));
                }
                
                // Save top navigation state
                if ($(settings.topNavSelector).length) {
                    sessionStorage.setItem(settings.storagePrefix + 'navbarHTML', $(settings.topNavSelector).html());
                }
            }
            
            function restoreState() {
                // Restore sidebar state if exists
                var storedSidebarScroll = sessionStorage.getItem(settings.storagePrefix + 'sidebarScroll');
                if (storedSidebarScroll && $(settings.sidebarSelector).length) {
                    $(settings.sidebarSelector).scrollTop(parseInt(storedSidebarScroll));
                }
                
                // Restore active state based on current URL
                var currentPath = window.location.pathname;
                $(settings.sidebarSelector).find('a').each(function() {
                    var linkHref = $(this).attr('href');
                    if (linkHref) {
                        // Convert to path if it's a full URL
                        if (linkHref.indexOf('://') > -1) {
                            var url = new URL(linkHref);
                            linkHref = url.pathname;
                        }
                        
                        // Check if this link matches current path
                        if (currentPath === linkHref || currentPath.indexOf(linkHref) === 0) {
                            $(this).addClass(settings.activeClass);
                        }
                    }
                });
            }
            
            function isInternalLink(href) {
                if (!href) return false;
                
                // Check if it's a relative path or same origin
                return href.startsWith('/') || 
                       href.startsWith(window.location.origin) || 
                       !href.startsWith('http');
            }
        });
    };
})(jQuery);