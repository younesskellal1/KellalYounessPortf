/**
 * Theme Toggle Functionality
 * Handles dark/light theme switching with localStorage persistence
 */

(function() {
    'use strict';
    
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeLabel = document.getElementById('themeLabel');
    const html = document.documentElement;
    
    // Get saved theme or default to dark
    const savedTheme = localStorage.getItem('portfolio-theme') || 'dark';
    
    // Apply saved theme on load
    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('portfolio-theme', theme);
        
        // Update icon and label
        if (theme === 'light') {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
            if (themeLabel) themeLabel.textContent = 'Light';
        } else {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
            if (themeLabel) themeLabel.textContent = 'Dark';
        }
    }
    
    // Initialize theme
    applyTheme(savedTheme);
    
    // Toggle theme on button click
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = html.getAttribute('data-theme') || 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
            
            // Add animation class
            html.classList.add('theme-transitioning');
            setTimeout(() => {
                html.classList.remove('theme-transitioning');
            }, 300);
        });
    }
    
    // Listen for system theme changes (optional)
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: light)');
        
        // Only apply system preference if no saved preference exists
        if (!localStorage.getItem('portfolio-theme')) {
            mediaQuery.addEventListener('change', function(e) {
                applyTheme(e.matches ? 'light' : 'dark');
            });
        }
    }
})();

