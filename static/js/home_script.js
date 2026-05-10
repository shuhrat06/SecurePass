// ============================================
// TODO PLATFORM - ZAMONAVIY JAVASCRIPT
// ============================================

(function() {
    'use strict';

    // DOM elementlarni kesh qilish
    const domElements = {};

    function cacheDOM() {
        domElements.navbar = document.querySelector('.navbar');
        domElements.backToTop = document.getElementById('backToTop');
        domElements.contactForm = document.querySelector('form[id^="contactForm"]');
        domElements.notification = document.getElementById('ContactNotification');
        domElements.allLinks = document.querySelectorAll('a[href^="#"]');
    }

    // ========== NAVBAR SCROLL EFFECT ==========
    function initNavbarScroll() {
        if (!domElements.navbar) return;
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                domElements.navbar.classList.add('scrolled');
            } else {
                domElements.navbar.classList.remove('scrolled');
            }
        });
    }

    // ========== SMOOTH SCROLLING ==========
    function initSmoothScroll() {
        domElements.allLinks.forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#' || targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    const navbarHeight = domElements.navbar?.offsetHeight || 70;
                    const targetPosition = targetElement.offsetTop - navbarHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                    
                    // URL ni yangilash (opsional)
                    history.pushState(null, null, targetId);
                }
            });
        });
    }

    // ========== BACK TO TOP BUTTON ==========
    function initBackToTop() {
        if (!domElements.backToTop) return;
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                domElements.backToTop.style.display = 'flex';
            } else {
                domElements.backToTop.style.display = 'none';
            }
        });
        
        domElements.backToTop.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // ========== NOTIFICATION SYSTEM ==========
    function initNotification() {
        if (!domElements.notification) return;
        
        // Avtomatik yopilish
        setTimeout(() => {
            hideNotification();
        }, 4000);
        
        // Tugilganda yopish
        domElements.notification.addEventListener('click', () => {
            hideNotification();
        });
    }
    
    function showNotification(message, type = 'success') {
        const notification = domElements.notification;
        if (!notification) {
            // Agar notification elementi mavjud bo'lmasa, dinamik yaratish
            createDynamicNotification(message, type);
            return;
        }
        
        notification.classList.add('show');
        
        setTimeout(() => {
            hideNotification();
        }, 4000);
    }
    
    function hideNotification() {
        const notification = domElements.notification;
        if (notification) {
            notification.classList.remove('show');
        }
    }
    
    function createDynamicNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification-toast toast-${type}`;
        notification.innerHTML = `
            <div class="toast-content">
                <i class="bi ${type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'} me-2"></i>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    // ========== FORM VALIDATION ==========
    function initFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const emailInput = this.querySelector('input[type="email"]');
                const passwordInput = this.querySelector('input[type="password"]');
                
                if (emailInput && !validateEmail(emailInput.value)) {
                    e.preventDefault();
                    showNotification('Iltimos, to\'g\'ri email manzil kiriting', 'error');
                    emailInput.classList.add('is-invalid');
                    return false;
                }
                
                if (passwordInput && passwordInput.value.length < 3) {
                    e.preventDefault();
                    showNotification('Parol kamida 3 belgidan iborat bo\'lishi kerak', 'error');
                    passwordInput.classList.add('is-invalid');
                    return false;
                }
            });
            
            // Input fokusda invalid class ni olib tashlash
            const inputs = form.querySelectorAll('input');
            inputs.forEach(input => {
                input.addEventListener('focus', () => {
                    input.classList.remove('is-invalid');
                });
            });
        });
    }
    
    function validateEmail(email) {
        const re = /^[^\s@]+@([^\s@.,]+\.)+[^\s@.,]{2,}$/;
        return re.test(email);
    }

    // ========== PASSWORD GENERATOR ENHANCEMENT ==========
    function initPasswordGenerator() {
        const generateForm = document.querySelector('#generator form');
        const lengthInput = document.querySelector('input[name="length"]');
        
        if (lengthInput) {
            lengthInput.addEventListener('change', function() {
                let value = parseInt(this.value);
                if (isNaN(value)) this.value = 8;
                if (value < 2) this.value = 2;
                if (value > 32) this.value = 32;
            });
        }
        
        // Generated passwordga qo'shimcha funksiya
        const generatedDiv = document.querySelector('.generated_password');
        if (generatedDiv && !generatedDiv.hasAttribute('data-initialized')) {
            generatedDiv.setAttribute('data-initialized', 'true');
            
            // Tooltip qo'shish
            generatedDiv.setAttribute('title', 'Nusxalash uchun bosing');
            
            // Copy funksiyasi (agar mavjud bo'lmasa)
            if (!generatedDiv._copyHandler) {
                generatedDiv._copyHandler = function() {
                    const text = this.innerText.replace('Generated Password: ', '').replace('Exception: ', '');
                    if (text && !text.includes('Exception')) {
                        navigator.clipboard.writeText(text).then(() => {
                            const originalText = this.innerText;
                            this.innerHTML = '<span>✅ Nusxalandi!</span>';
                            setTimeout(() => {
                                this.innerHTML = originalText;
                            }, 1500);
                        });
                    }
                };
                generatedDiv.addEventListener('click', generatedDiv._copyHandler);
            }
        }
    }

    // ========== PASSWORD EVALUATOR ENHANCEMENT ==========
    function initPasswordEvaluator() {
        const passwordInput = document.getElementById('password');
        const evaluatorForm = document.querySelector('#evaluation form');
        
        if (passwordInput && evaluatorForm) {
            // Parol kuchini real-time tekshirish
            passwordInput.addEventListener('input', function() {
                const strength = checkPasswordStrength(this.value);
                updatePasswordStrengthIndicator(strength);
            });
        }
    }
    
    function checkPasswordStrength(password) {
        let score = 0;
        
        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[a-z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;
        
        if (score <= 2) return 'weak';
        if (score <= 4) return 'medium';
        return 'strong';
    }
    
    function updatePasswordStrengthIndicator(strength) {
        let existingIndicator = document.querySelector('.strength-indicator');
        if (!existingIndicator) {
            existingIndicator = document.createElement('div');
            existingIndicator.className = 'strength-indicator mt-2';
            const passwordField = document.querySelector('.password-field');
            if (passwordField) passwordField.parentNode.insertBefore(existingIndicator, passwordField.nextSibling);
        }
        
        const messages = {
            weak: { text: 'Zaif parol', class: 'weak', color: '#ef476f' },
            medium: { text: 'O\'rtacha parol', class: 'medium', color: '#ffd166' },
            strong: { text: 'Kuchli parol', class: 'strong', color: '#06ffa5' }
        };
        
        const info = messages[strength];
        if (info) {
            existingIndicator.innerHTML = `<small style="color: ${info.color}">${info.text}</small>`;
            existingIndicator.className = `strength-indicator mt-2 ${info.class}`;
        }
    }

    // ========== INTERSECTION OBSERVER FOR ANIMATIONS ==========
    function initScrollAnimations() {
        const animatedElements = document.querySelectorAll('.feature-card, .how-it-works article');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '0';
                    entry.target.style.transform = 'translateY(30px)';
                    
                    setTimeout(() => {
                        entry.target.style.transition = 'all 0.6s ease';
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, 100);
                    
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: '50px' });
        
        animatedElements.forEach(el => observer.observe(el));
    }

    // ========== MOBILE MENU AUTO CLOSE ==========
    function initMobileMenu() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        if (navbarToggler && navbarCollapse) {
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    if (window.innerWidth < 992) {
                        const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                        if (bsCollapse) bsCollapse.hide();
                    }
                });
            });
        }
    }

    // ========== LOADING STATE FOR BUTTONS ==========
    function initButtonLoading() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn && !submitBtn.classList.contains('btn-loading')) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Yuklanmoqda...';
                    submitBtn.classList.add('btn-loading');
                    
                    // Form yuborilgandan keyin qayta tiklash (error bo'lsa)
                    setTimeout(() => {
                        if (submitBtn.classList.contains('btn-loading')) {
                            submitBtn.innerHTML = originalText;
                            submitBtn.classList.remove('btn-loading');
                        }
                    }, 5000);
                }
            });
        });
    }

    // ========== THEME TOGGLE (OPSIONAL) ==========
    function initThemeToggle() {
        // Toggle tugmasi mavjud emas, lekin kelajak uchun tayyor
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        const applyTheme = (isDark) => {
            if (isDark) {
                document.body.setAttribute('data-theme', 'dark');
            } else {
                document.body.removeAttribute('data-theme');
            }
        };
        
        prefersDark.addListener((e) => applyTheme(e.matches));
        applyTheme(prefersDark.matches);
    }

    // ========== COPY TEXT UTILITY ==========
    window.copyToClipboard = async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            showNotification('Nusxalandi!', 'success');
            return true;
        } catch (err) {
            console.error('Nusxalash amalga oshmadi:', err);
            showNotification('Nusxalash amalga oshmadi', 'error');
            return false;
        }
    };

    // ========== INITIALIZE ALL ==========
    document.addEventListener('DOMContentLoaded', () => {
        cacheDOM();
        initNavbarScroll();
        initSmoothScroll();
        initBackToTop();
        initNotification();
        initFormValidation();
        initPasswordGenerator();
        initPasswordEvaluator();
        initScrollAnimations();
        initMobileMenu();
        initButtonLoading();
        initThemeToggle();
        
        // Bootstrap tooltip'larni initialize qilish (agar mavjud bo'lsa)
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
        }
        
        console.log('TODO Platform initialized successfully!');
    });
})();