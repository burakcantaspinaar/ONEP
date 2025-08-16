/* ONEP E-Commerce Platform - Modern UI JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modern UI features
    console.log('🚀 ONEP Modern UI başlatılıyor...');
    
    // Dark mode disabled
    // initDarkMode();
    
    // Initialize the rest with slight delay to ensure DOM is fully ready
    setTimeout(() => {
        initScrollEffects();
        initAnimations();
        initToastSystem();
        initLightbox();
        initBackToTop();
        init3DTiltEffect();
        initFormEnhancements();
        enhanceCartExperience();
        
        // Show welcome toast
        if (window.showToast) {
            window.showToast('Modern arayüz başarıyla yüklendi!', 'info', 3000);
        }
        
        console.log('✅ ONEP Modern UI başarıyla başlatıldı!');
    }, 100);
});

/* Dark Mode System disabled */
function initDarkMode() {
    try {
        localStorage.setItem('darkMode', 'disabled');
        document.body.classList.remove('dark-mode');
    } catch (e) {}
}

/* Scroll Effects */
function initScrollEffects() {
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        // Shrink navbar on scroll
        if (currentScrollY > 50) {
            navbar?.classList.add('shrink');
        } else {
            navbar?.classList.remove('shrink');
        }
        
        lastScrollY = currentScrollY;
    });
}

/* Animation System */
function initAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all cards and important elements
    document.querySelectorAll('.card, .product-card, .main-content > *').forEach(el => {
        observer.observe(el);
    });
    
    // Add stagger effect to product grids
    document.querySelectorAll('.product-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
}

/* Toast Notification System */
function initToastSystem() {
    window.showToast = function(message, type = 'success', duration = 3000) {
        const toastContainer = getOrCreateToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-header border-0 bg-transparent">
                <i class="fas fa-${getToastIcon(type)} me-2"></i>
                <strong class="me-auto">${getToastTitle(type)}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            toast.style.animation = 'fadeInUp 0.3s ease-out reverse';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
        
        // Manual close
        const closeBtn = toast.querySelector('.btn-close');
        closeBtn?.addEventListener('click', () => {
            toast.style.animation = 'fadeInUp 0.3s ease-out reverse';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        });
    };
    
    function getOrCreateToastContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }
    
    function getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    function getToastTitle(type) {
        const titles = {
            success: 'Başarılı!',
            error: 'Hata!',
            warning: 'Uyarı!',
            info: 'Bilgi'
        };
        return titles[type] || 'Bilgi';
    }
}

/* Lightbox System */
function initLightbox() {
    // Create lightbox only when needed - not initially visible
    let lightbox = null;
    
    // Function to create and show lightbox
    function showLightbox(imgSrc, imgAlt) {
        // Create lightbox if it doesn't exist
        if (!lightbox) {
            lightbox = document.createElement('div');
            lightbox.className = 'lightbox';
            lightbox.innerHTML = `
                <div class="lightbox-content">
                    <button class="close" aria-label="Close lightbox">
                        <i class="fas fa-times"></i>
                    </button>
                    <img src="" alt="">
                    <div class="lightbox-caption"></div>
                </div>
            `;
            document.body.appendChild(lightbox);
            
            // Add event listeners
            const closeBtn = lightbox.querySelector('.close');
            closeBtn.addEventListener('click', closeLightbox);
            lightbox.addEventListener('click', (e) => {
                if (e.target === lightbox) closeLightbox();
            });
            
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && lightbox.classList.contains('active')) {
                    closeLightbox();
                }
            });
        }
        
        // Set image and show lightbox
        const lightboxImg = lightbox.querySelector('img');
        const caption = lightbox.querySelector('.lightbox-caption');
        
        lightboxImg.src = imgSrc;
        lightboxImg.alt = imgAlt;
        caption.textContent = imgAlt;
        
        // Show the lightbox
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
    
    function closeLightbox() {
        if (lightbox) {
            lightbox.classList.remove('active');
            document.body.style.overflow = ''; // Restore scrolling
        }
    }
    
    // Add click listeners to product images
    document.querySelectorAll('.product-image img, .product-detail img').forEach(img => {
        img.style.cursor = 'pointer';
        img.addEventListener('click', () => {
            showLightbox(img.src, img.alt);
        });
    });
}

/* Back to Top Button */
function initBackToTop() {
    const backToTop = document.createElement('button');
    backToTop.className = 'back-to-top';
    backToTop.innerHTML = '<i class=\"fas fa-arrow-up\"></i>';
    backToTop.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTop);
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });
    
    backToTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/* 3D Tilt Effect for Product Cards */
function init3DTiltEffect() {
    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('mousemove', handleTilt);
        card.addEventListener('mouseleave', resetTilt);
    });
    
    function handleTilt(e) {
        const card = e.currentTarget;
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
    }
    
    function resetTilt(e) {
        e.currentTarget.style.transform = '';
    }
}

/* Form Enhancements */
function initFormEnhancements() {
    // Add floating label effect
    document.querySelectorAll('.form-control').forEach(input => {
        if (!input.closest('.form-floating')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'form-floating';
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);
            
            const label = document.createElement('label');
            label.textContent = input.placeholder || input.getAttribute('name');
            label.setAttribute('for', input.id || input.name);
            wrapper.appendChild(label);
            
            input.placeholder = '';
        }
    });
    
    // Enhanced form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            const inputs = form.querySelectorAll('.form-control[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('Lütfen tüm gerekli alanları doldurun.', 'error');
            }
        });
    });
}

/* Enhanced AJAX Cart Integration */
document.addEventListener('DOMContentLoaded', function() {
    // Override existing cart functions with enhanced UI
    const originalCartFunctions = window.cartAjax || {};
    
    // Enhanced add to cart with confetti effect
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const button = form.querySelector('button[type=\"submit\"]');
            const originalText = button.innerHTML;
            
            // Show loading state
            button.innerHTML = '<span class=\"spinner-border spinner-border-sm me-2\"></span>Ekleniyor...';
            button.disabled = true;
            
            // Simulate AJAX call (keeping existing functionality)
            const formData = new FormData(form);
            
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message || 'Ürün sepete eklendi!', 'success');
                    updateCartCount(data.cart_count);
                    createConfetti(button);
                } else {
                    showToast(data.message || 'Bir hata oluştu!', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Bağlantı hatası!', 'error');
            })
            .finally(() => {
                // Reset button
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                }, 1000);
            });
        });
    });
    
    function updateCartCount(count) {
        const cartCountElements = document.querySelectorAll('.cart-count');
        cartCountElements.forEach(element => {
            element.textContent = count;
            element.style.display = count > 0 ? 'inline-block' : 'none';
            if (count > 0) {
                element.classList.add('pulse-hover');
            }
        });
    }
    
    function createConfetti(button) {
        for (let i = 0; i < 10; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: absolute;
                width: 10px;
                height: 10px;
                background: hsl(${Math.random() * 360}, 100%, 50%);
                border-radius: 50%;
                pointer-events: none;
                animation: confetti 2s ease-out forwards;
                left: ${button.offsetLeft + Math.random() * button.offsetWidth}px;
                top: ${button.offsetTop}px;
                z-index: 1000;
            `;
            button.parentNode.appendChild(confetti);
            
            setTimeout(() => {
                if (confetti.parentNode) {
                    confetti.parentNode.removeChild(confetti);
                }
            }, 2000);
        }
    }
});
