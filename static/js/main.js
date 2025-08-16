// ONEP E-Commerce Platform - Main JavaScript File
document.addEventListener('DOMContentLoaded', function() {
    console.log('ONEP Platform loaded successfully!');
    
    // Alert close functionality (if needed)
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Auto hide alerts after 5 seconds
        setTimeout(() => {
            if (alert && alert.classList.contains('show')) {
                alert.classList.remove('show');
                alert.classList.add('fade');
                setTimeout(() => {
                    if (alert.parentElement) {
                        alert.remove();
                    }
                }, 150);
            }
        }, 5000);
    });
    
    // Form validation helper
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Only add basic loading state, not prevent submission
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                submitButton.disabled = true;
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>İşleniyor...';
                
                // Re-enable after 3 seconds to prevent infinite disable
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }, 3000);
            }
        });
    });
});