/**
 * Main JavaScript for Portfolio Website
 * Handles animations, interactions, and Three.js background
 */

// ==================== LANGUAGE SWITCHER ====================
document.addEventListener('DOMContentLoaded', function() {
    const langToggle = document.getElementById('langToggle');
    const langDropdown = document.getElementById('langDropdown');
    
    if (langToggle && langDropdown) {
        langToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            langDropdown.classList.toggle('lang-dropdown-open');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!langToggle.contains(e.target) && !langDropdown.contains(e.target)) {
                langDropdown.classList.remove('lang-dropdown-open');
            }
        });
        
        // Close dropdown when selecting a language
        const langOptions = langDropdown.querySelectorAll('.lang-option');
        langOptions.forEach(option => {
            option.addEventListener('click', function() {
                langDropdown.classList.remove('lang-dropdown-open');
            });
        });
    }
});

// ==================== NAVIGATION ====================
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const navbar = document.querySelector('.navbar');
    
    // Mobile menu toggle
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }
    
    // Close mobile menu when clicking on a link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    });
    
    // Navbar scroll effect
    let lastScroll = 0;
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
    
    // Close flash messages
    const flashCloseButtons = document.querySelectorAll('.flash-close');
    flashCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const flashMessage = this.closest('.flash-message');
            flashMessage.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => {
                flashMessage.remove();
            }, 300);
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
});

// ==================== THREE.JS BACKGROUND ====================
function initThreeJSBackground() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    // Create particles
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 2000;
    const posArray = new Float32Array(particlesCount * 3);
    
    for (let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 20;
    }
    
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    
    const particlesMaterial = new THREE.PointsMaterial({
        size: 0.02,
        color: 0x00f0ff,
        transparent: true,
        opacity: 0.6,
    });
    
    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particlesMesh);
    
    camera.position.z = 5;
    
    // Animation
    function animate() {
        requestAnimationFrame(animate);
        
        particlesMesh.rotation.x += 0.0005;
        particlesMesh.rotation.y += 0.001;
        
        renderer.render(scene, camera);
    }
    
    animate();
    
    // Handle window resize
    window.addEventListener('resize', function() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// Initialize Three.js background
if (typeof THREE !== 'undefined') {
    initThreeJSBackground();
}

// ==================== 3D CARD TILT EFFECT ====================
function init3DCardTilt() {
    const cards = document.querySelectorAll('.project-card-3d, .skill-card, .cert-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            const cardInner = card.querySelector('.project-card-inner');
            if (cardInner) {
                cardInner.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const cardInner = card.querySelector('.project-card-inner');
            if (cardInner) {
                cardInner.style.transform = '';
            }
        });
    });
}

// Initialize 3D card tilt
document.addEventListener('DOMContentLoaded', init3DCardTilt);

// ==================== SMOOTH SCROLL ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==================== FORM VALIDATION ====================
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Basic validation
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const message = document.getElementById('message').value.trim();
        
        if (!name || !email || !message) {
            alert('Please fill in all required fields.');
            return;
        }
        
        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Please enter a valid email address.');
            return;
        }
        
        // In production, this would send to the backend
        alert('Thank you for your message! In a production environment, this would be sent to the server.');
        contactForm.reset();
    });
}

// ==================== INTERSECTION OBSERVER FOR ANIMATIONS ====================
// Only use Intersection Observer for elements that don't have GSAP animations
// GSAP ScrollTrigger handles most animations, so this is a fallback
document.addEventListener('DOMContentLoaded', function() {
    // Check if GSAP is available - if so, let GSAP handle animations
    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        // GSAP will handle animations, so we skip Intersection Observer
        return;
    }
    
    // Fallback: Use Intersection Observer only if GSAP is not available
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Only animate if element hasn't been animated by GSAP
                if (!entry.target.dataset.animated) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    entry.target.dataset.animated = 'true';
                    observer.unobserve(entry.target);
                }
            }
        });
    }, observerOptions);

    // Observe elements for fade-in animation (only if GSAP not available)
    const animatedElements = document.querySelectorAll('.skill-card, .project-card-3d, .timeline-item, .cert-card');
    animatedElements.forEach(el => {
        // Only set initial state if not already animated
        if (!el.dataset.animated) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        }
    });
});

