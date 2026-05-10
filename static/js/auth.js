// Toast elementi va xatolik xabari uchun referanslar
let errorToast;
let toastInstance;
let progressBar = null;

// DOM elementlari yuklangandan so'ng ishga tushirish
document.addEventListener('DOMContentLoaded', function() {
    // Toast elementini olish va Bootstrap toast instance'ini yaratish
    const toastElement = document.getElementById('errorToast');
    if (!toastElement) return;
    
    errorToast = toastElement;
    
    // Bootstrap toast instance'ini yaratish
    toastInstance = new bootstrap.Toast(toastElement, {
        autohide: false
    });
    
    // Progress bar qo'shish
    addProgressBar();
    
    // Qaysi sahifada ekanligimizni aniqlash
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleLogin();
        });
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleRegister();
        });
    }
});

// Progress bar qo'shish
function addProgressBar() {
    if (!errorToast) return;
    
    const oldProgress = errorToast.querySelector('.toast-progress');
    if (oldProgress) {
        oldProgress.remove();
    }
    
    progressBar = document.createElement('div');
    progressBar.className = 'toast-progress';
    errorToast.style.position = 'relative';
    errorToast.style.overflow = 'hidden';
    errorToast.appendChild(progressBar);
}

// Xatolik oynasini ko'rsatish
function showError(message) {
    if (!errorToast) return;
    
    const errorMessageSpan = document.getElementById('errorMessage');
    if (errorMessageSpan) {
        errorMessageSpan.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${message}`;
    }
    
    // Rangni qizil qilish
    errorToast.classList.remove('bg-success');
    errorToast.classList.add('bg-danger');
    
    addProgressBar();
    toastInstance.show();
    
    if (progressBar) {
        const handleAnimationEnd = () => {
            hideErrorToast();
            progressBar.removeEventListener('animationend', handleAnimationEnd);
        };
        progressBar.addEventListener('animationend', handleAnimationEnd);
        
        setTimeout(() => {
            if (errorToast && errorToast.classList.contains('show')) {
                hideErrorToast();
            }
        }, 3000);
    } else {
        setTimeout(() => {
            if (errorToast && errorToast.classList.contains('show')) {
                hideErrorToast();
            }
        }, 3000);
    }
}

// Xatolik oynasini yashirish
function hideErrorToast() {
    if (toastInstance && errorToast && errorToast.classList.contains('show')) {
        toastInstance.hide();
    }
}

// Muvaffaqiyatli xabar
function showSuccess(message) {
    if (!errorToast) return;
    
    const errorMessageSpan = document.getElementById('errorMessage');
    if (errorMessageSpan) {
        errorMessageSpan.innerHTML = `<i class="fas fa-check-circle me-2"></i>${message}`;
    }
    
    errorToast.classList.remove('bg-danger');
    errorToast.classList.add('bg-success');
    
    addProgressBar();
    toastInstance.show();
    
    setTimeout(() => {
        if (errorToast.classList.contains('show')) {
            hideErrorToast();
        }
    }, 3000);
}

// Input maydoniga xatolik border animatsiyasi
function addErrorBorderAnimation(inputElement) {
    if (!inputElement) return;
    
    inputElement.style.transition = 'all 0.2s';
    inputElement.style.borderColor = '#ef4444';
    
    setTimeout(() => {
        if (inputElement) {
            inputElement.style.borderColor = '';
        }
    }, 1000);
}

// Login funksiyasi
function handleLogin() {
    const username = document.getElementById('loginUsername');
    const password = document.getElementById('loginPassword');
    
    if (!username.value.trim()) {
        showError('Username yoki email manzilni kiriting!');
        addErrorBorderAnimation(username);
        return;
    }
    
    if (!password.value) {
        showError('Parolni kiriting!');
        addErrorBorderAnimation(password);
        return;
    }
    
    // Simulyatsiya qilingan backend tekshiruvi
    const existingUsers = {
        'john_doe': 'password123',
        'jane_smith': 'qwerty123',
        'testuser': 'test123',
        'john@example.com': 'password123',
        'jane@example.com': 'qwerty123',
        'test@example.com': 'test123'
    };
    
    const inputValue = username.value.trim().toLowerCase();
    const userPassword = existingUsers[inputValue];
    
    if (!userPassword) {
        showError('Username yoki email topilmadi!');
        addErrorBorderAnimation(username);
        return;
    }
    
    if (password.value !== userPassword) {
        showError('Parol noto\'g\'ri!');
        addErrorBorderAnimation(password);
        return;
    }
    
    showSuccess('Tizimga muvaffaqiyatli kirdingiz!');
    
    // 2 sekunddan keyin bosh sahifaga yo'naltirish (demo)
    setTimeout(() => {
        alert('Demo: Dashboard sahifasiga o\'tildi');
        // window.location.href = 'dashboard.html';
    }, 2000);
}

// Register funksiyasi
function handleRegister() {
    const username = document.getElementById('regUsername');
    const email = document.getElementById('regEmail');
    const password = document.getElementById('regPassword');
    const confirmPassword = document.getElementById('regConfirmPassword');
    const termsCheckbox = document.getElementById('termsCheckbox');
    
    if (!username.value.trim()) {
        showError('Username kiriting!');
        addErrorBorderAnimation(username);
        return;
    }
    
    if (username.value.trim().length < 3) {
        showError('Username kamida 3 belgidan iborat bo\'lishi kerak!');
        addErrorBorderAnimation(username);
        return;
    }
    
    if (!email.value.trim()) {
        showError('Email manzilni kiriting!');
        addErrorBorderAnimation(email);
        return;
    }
    
    const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    if (!emailRegex.test(email.value.trim())) {
        showError('Email manzil noto\'g\'ri formatda!');
        addErrorBorderAnimation(email);
        return;
    }
    
    if (!password.value) {
        showError('Parolni kiriting!');
        addErrorBorderAnimation(password);
        return;
    }
    
    if (password.value.length < 6) {
        showError('Parol kamida 6 belgidan iborat bo\'lishi kerak!');
        addErrorBorderAnimation(password);
        return;
    }
    
    if (!confirmPassword.value) {
        showError('Parolni tasdiqlang!');
        addErrorBorderAnimation(confirmPassword);
        return;
    }
    
    if (password.value !== confirmPassword.value) {
        showError('Parollar bir-biriga mos kelmadi!');
        addErrorBorderAnimation(confirmPassword);
        return;
    }
    
    if (!termsCheckbox.checked) {
        showError('Foydalanish shartlariga rozilik bildirishingiz kerak!');
        addErrorBorderAnimation(termsCheckbox);
        return;
    }
    
    // Simulyatsiya qilingan username va email bandligi tekshiruvi
    const existingUsernames = ['john_doe', 'jane_smith', 'testuser', 'admin'];
    const existingEmails = ['john@example.com', 'jane@example.com', 'test@example.com'];
    
    if (existingUsernames.includes(username.value.trim().toLowerCase())) {
        showError('Username band! Iltimos, boshqa username tanlang.');
        addErrorBorderAnimation(username);
        return;
    }
    
    if (existingEmails.includes(email.value.trim().toLowerCase())) {
        showError('Email band! Bu email allaqachon ro\'yxatdan o\'tgan.');
        addErrorBorderAnimation(email);
        return;
    }
    
    showSuccess('Ro\'yxatdan o\'tish muvaffaqiyatli! Endi tizimga kirishingiz mumkin.');
    
    // 2 sekunddan keyin login sahifasiga yo'naltirish
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 2000);
}