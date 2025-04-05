// Dark Mode Toggle Script

document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        
        // Check for saved dark mode preference
        const isDarkMode = document.body.classList.contains('dark-mode');
        
        // Update toggle button UI
        updateToggleUI(isDarkMode);
        
        // Add event listener for toggle button
        darkModeToggle.addEventListener('click', function() {
            // Toggle dark mode by sending a request to the server
            // The actual toggle is handled on the server-side
            // The page will be reloaded with the new theme
        });
    }
    
    // Function to update the toggle button appearance
    function updateToggleUI(isDarkMode) {
        const icon = darkModeToggle.querySelector('i');
        
        if (isDarkMode) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
            darkModeToggle.setAttribute('title', 'Switch to Light Mode');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
            darkModeToggle.setAttribute('title', 'Switch to Dark Mode');
        }
    }
});
