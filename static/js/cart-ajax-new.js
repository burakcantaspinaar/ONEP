document.addEventListener('DOMContentLoaded', function() {
    // CSRF token ayarı
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
    
    // Sepet sayacını güncelleme yardımcı fonksiyonu
    function updateCartCount(count) {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = count;
            cartCountElement.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }
    
    // Sepet toplamlarını güncelleme yardımcı fonksiyonu
    function updateCartTotals(data) {
        if (data.toplam_tutar !== undefined) {
            const subtotalElement = document.querySelector('.cart-summary-subtotal');
            const taxElement = document.querySelector('.cart-summary-tax');
            const totalElement = document.querySelector('.cart-summary-total');
            
            if (subtotalElement) subtotalElement.textContent = `${data.toplam_tutar.toFixed(2)} ₺`;
            if (taxElement) taxElement.textContent = `${data.kdv_tutari.toFixed(2)} ₺`;
            if (totalElement) totalElement.textContent = `${data.genel_toplam.toFixed(2)} ₺`;
        }
    }
    
    // Toast mesaj gösterme fonksiyonu
    function showToast(message, type = 'success') {
        // Toast elementini oluştur (eğer yoksa)
        if (!document.getElementById('toast-container')) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
            toastContainer.style.zIndex = '11';
            document.body.appendChild(toastContainer);
        }
        
        // Rastgele ID oluştur
        const toastId = 'toast-' + Math.random().toString(36).substr(2, 9);
        
        // Toast HTML
        const toast = document.createElement('div');
        toast.className = `toast align-items-center border-0 bg-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.id = toastId;
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body text-white">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Kapat"></button>
            </div>
        `;
        
        document.getElementById('toast-container').appendChild(toast);
        
        // Toast'ı göster
        const bsToast = new bootstrap.Toast(toast, {
            animation: true,
            autohide: true,
            delay: 3000
        });
        bsToast.show();
        
        // Süre sonunda kaldır
        toast.addEventListener('hidden.bs.toast', function () {
            this.remove();
        });
    }

    // Event delegation ile tüm etkileşimleri yönet
    document.body.addEventListener('click', function(e) {
        // Sepete ekle butonu
        if (e.target.closest('.add-to-cart-form button')) {
            e.preventDefault();
            const button = e.target.closest('.add-to-cart-form button');
            const form = button.closest('form');
            
            if (!form) return;
            
            const formUrl = form.action;
            const urunId = form.querySelector('[name="urun_id"]')?.value;
            const urunAdi = form.dataset.urunAdi || "Ürün";
            
            fetch(formUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'urun_id': urunId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(`${urunAdi} sepete eklendi!`);
                    
                    // Sepet sayacını güncelle
                    updateCartCount(data.cart_count || 0);
                } else {
                    showToast(data.message || 'Bir hata oluştu', 'danger');
                }
            })
            .catch(error => {
                console.error('Hata:', error);
                showToast('Bir hata oluştu, lütfen tekrar deneyin', 'danger');
            });
        }
        
        // Artı ve Eksi butonları - miktar güncelleme
        else if (e.target.matches('button[name="increase"], button[name="decrease"], button[name="increase"] *, button[name="decrease"] *')) {
            // Tıklanan butonu bul (i tag'ine tıklanırsa butonunu bul)
            const button = e.target.closest('button');
            if (!button) return;
            
            // Buton zaten disabled ise işlemi durdur
            if (button.disabled) {
                console.log('Button is disabled, ignoring click');
                return;
            }
            
            // Butonları geçici olarak disable et
            button.disabled = true;
            
            const form = button.closest('form');
            if (!form) {
                console.error('Form not found');
                button.disabled = false;
                return;
            }
            
            const actionInput = form.querySelector('input[name="action"]');
            if (!actionInput) {
                console.error('Action input not found');
                button.disabled = false;
                return;
            }
            
            // Action değerini belirle
            actionInput.value = button.name; // "increase" veya "decrease"
            
            const formUrl = form.action;
            console.log('Form submission:', {
                url: formUrl,
                action: actionInput.value
            });
            
            // AJAX isteği gönder
            fetch(formUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'action': actionInput.value,
                    'csrfmiddlewaretoken': form.querySelector('[name=csrfmiddlewaretoken]').value
                })
            })
            .then(response => {
                console.log('Response status:', response.status);
                console.log('Response URL:', response.url);
                console.log('Response headers:', response.headers.get('content-type'));
                
                // İlk olarak response text'ini alalım
                return response.text().then(text => {
                    console.log('Response text (ilk 200 karakter):', text.substring(0, 200));
                    
                    // Eğer response OK değilse
                    if (!response.ok) {
                        console.error(`HTTP error: ${response.status} for URL ${response.url}`);
                        throw new Error(`Server error: ${response.status} - Response is not JSON`);
                    }
                    
                    // JSON'a çevirmeye çalış
                    try {
                        return JSON.parse(text);
                    } catch (e) {
                        console.error('JSON parse error:', e);
                        console.error('Raw response:', text);
                        throw new Error(`JSON parse error: ${e.message}`);
                    }
                });
            })
            .then(data => {
                console.log('Parsed response data:', data);
                
                if (data.success) {
                    // Ürün miktarını güncelle
                    const quantityInput = form.querySelector('.quantity-input');
                    if (quantityInput && data.new_quantity !== undefined) {
                        quantityInput.value = data.new_quantity;
                    }
                    
                    // Ürün toplam fiyatını güncelle
                    const row = form.closest('.row');
                    if (row) {
                        const totalPriceElement = row.querySelector('.price-column:last-of-type .fw-bold');
                        if (totalPriceElement && data.new_total) {
                            totalPriceElement.textContent = `${data.new_total.toFixed(2)} ₺`;
                        }
                    }
                    
                    // Sepet özetini güncelle
                    updateCartTotals(data);
                    
                    // Sepet sayacını güncelle
                    updateCartCount(data.cart_count || 0);
                    
                    showToast('Miktar güncellendi!');
                } else {
                    console.error('Response error:', data);
                    showToast(data.message || 'Güncelleme başarısız', 'danger');
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                showToast('Ağ hatası: ' + error.message, 'danger');
            })
            .finally(() => {
                // Butonu tekrar aktif et (500ms sonra)
                setTimeout(() => {
                    button.disabled = false;
                }, 500);
            });
        }
        
        // Sepetten sil butonu
        else if (e.target.closest('.remove-cart-form button')) {
            e.preventDefault();
            const button = e.target.closest('.remove-cart-form button');
            const form = button.closest('form');
            
            if (!form) return;
            
            // Onay isteme
            if (!confirm('Bu ürünü sepetten kaldırmak istediğinizden emin misiniz?')) {
                return;
            }
            
            const formUrl = form.action;
            const urunAdi = form.dataset.urunAdi || "Ürün";
            
            fetch(formUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Ürünü listeden kaldır
                    const row = form.closest('.row');
                    if (row) {
                        row.style.opacity = '0';
                        setTimeout(() => {
                            row.remove();
                            
                            // Eğer sepet boşaldıysa sayfayı yenile
                            if (data.cart_count === 0) {
                                location.reload();
                            }
                        }, 300);
                    }
                    
                    // Sepet sayacını güncelle
                    updateCartCount(data.cart_count || 0);
                    
                    // Sepet özetini güncelle
                    updateCartTotals(data);
                    
                    showToast(`${urunAdi} sepetten silindi!`);
                } else {
                    showToast(data.message || 'Silme işlemi başarısız', 'danger');
                }
            })
            .catch(error => {
                console.error('Hata:', error);
                showToast('Bir hata oluştu, lütfen tekrar deneyin', 'danger');
            });
        }
    });
    
    // Submit formlarını engelle
    document.body.addEventListener('submit', function(e) {
        if (e.target.classList.contains('quantity-control') || 
            e.target.classList.contains('add-to-cart-form') || 
            e.target.classList.contains('remove-cart-form')) {
            e.preventDefault();
        }
    });
});
