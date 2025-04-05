// Dark mode functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved preference in localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Apply saved theme
    document.body.setAttribute('data-theme', savedTheme);
    
    // Update toggle icon based on current theme
    updateToggleIcon(savedTheme);
    
    // Dark mode toggle click event
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            // Toggle between dark and light
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Apply new theme
            document.body.setAttribute('data-theme', newTheme);
            
            // Save preference to localStorage
            localStorage.setItem('theme', newTheme);
            
            // Update toggle icon
            updateToggleIcon(newTheme);
        });
    }
    
    function updateToggleIcon(theme) {
        const toggleIcon = document.querySelector('.dark-mode-toggle i');
        if (toggleIcon) {
            if (theme === 'dark') {
                toggleIcon.className = 'fas fa-sun';
            } else {
                toggleIcon.className = 'fas fa-moon';
            }
        }
    }
});
