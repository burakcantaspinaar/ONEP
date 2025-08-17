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
    
    // Sepet doğrulama - sayfa yüklendiğinde sepeti kontrol et
    fetch('/cart/validate/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache, no-store'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.changed) {
            console.log('Sepet doğrulandı ve güncellendi');
            window.location.reload();
        }
    })
    .catch(error => {
        console.log('Sepet doğrulama hatası:', error);
    });
    
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
        console.log('Updating cart totals with data:', data);
        
        if (data.toplam_tutar !== undefined) {
            // Ara toplam, KDV ve genel toplam alanlarını güncelle
            const subtotalElement = document.querySelector('.cart-summary-subtotal');
            const taxElement = document.querySelector('.cart-summary-tax');
            const totalElement = document.querySelector('.cart-summary-total');
            
            if (subtotalElement) {
                console.log('Updating subtotal:', data.toplam_tutar.toFixed(2));
                subtotalElement.textContent = `${data.toplam_tutar.toFixed(2)} ₺`;
            }
            
            if (taxElement) {
                console.log('Updating tax:', data.kdv_tutari.toFixed(2));
                taxElement.textContent = `${data.kdv_tutari.toFixed(2)} ₺`;
            }
            
            if (totalElement) {
                console.log('Updating total:', data.genel_toplam.toFixed(2));
                totalElement.textContent = `${data.genel_toplam.toFixed(2)} ₺`;
            }
            
            // Sepet sayfasındaki tüm alanları güncellediğimizden emin ol
            document.querySelectorAll('.cart-summary-subtotal').forEach(el => {
                el.textContent = `${data.toplam_tutar.toFixed(2)} ₺`;
            });
            
            document.querySelectorAll('.cart-summary-tax').forEach(el => {
                el.textContent = `${data.kdv_tutari.toFixed(2)} ₺`;
            });
            
            document.querySelectorAll('.cart-summary-total').forEach(el => {
                el.textContent = `${data.genel_toplam.toFixed(2)} ₺`;
            });
            
            console.log('All cart total elements updated!');
        } else {
            console.warn('Cart totals data is missing or undefined:', data);
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
            
            // Form URL'sini doğru şekilde al
            const formAction = form.getAttribute('action');
            if (!formAction) {
                console.error('Form action not found');
                return;
            }
            
            const urunId = form.querySelector('[name="urun_id"]')?.value;
            const urunAdi = form.dataset.urunAdi || "Ürün";
            
            fetch(formAction, {
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
            .then(response => {
                if (!response.ok) {
                    console.error(`HTTP error: ${response.status} for URL ${response.url}`);
                    return response.text().then(text => {
                        console.error('Error response text:', text.substring(0, 200));
                        throw new Error(`Server error: ${response.status} for URL ${response.url}`);
                    });
                }
                
                return response.json();
            })
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
            
            // Form URL'sini doğru şekilde al
            let formAction = form.getAttribute('action');
            
            // Eğer formAction boşsa veya bir JS objesi ise, urun_id ile URL oluştur
            if (!formAction || formAction.includes('[object')) {
                const urunId = form.dataset.urunId;
                if (urunId) {
                    formAction = `/cart/update/${urunId}/`;
                    console.log('Form action was invalid, created URL from data-urun-id attribute:', formAction);
                } else {
                    console.error('Cannot create URL: No data-urun-id attribute found');
                    button.disabled = false;
                    return;
                }
            }
            
            console.log('Form submission:', {
                url: formAction,
                action: actionInput.value
            });
            
            // AJAX isteği gönder
            fetch(formAction, {
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
                
                if (!response.ok) {
                    console.error(`HTTP error: ${response.status} for URL ${response.url}`);
                    return response.text().then(text => {
                        console.error('Error response text:', text.substring(0, 200));
                        throw new Error(`Server error: ${response.status} for URL ${response.url}`);
                    });
                }
                
                // İlk olarak response text'ini alalım
                return response.text().then(text => {
                    console.log('Response text (ilk 200 karakter):', text.substring(0, 200));
                    
                    // JSON'a çevirmeye çalış
                    try {
                        const data = JSON.parse(text);
                        console.log('Parsed response data:', data);
                        
                        // Özel durum: eğer ürün sepetten çıkarıldıysa
                        if (data.success && (data.new_quantity === 0 || data.message === 'Ürün sepetten silindi!')) {
                            data.message = 'Ürün sepetten silindi!';
                        }
                        
                        return data;
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
                    // Miktar 0 ise ürünü sepetten kaldır (aynı sepetten_sil işlemi gibi)
                    if (data.new_quantity === 0 || data.message === 'Ürün sepetten silindi!') {
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
                        
                        showToast('Ürün sepetten silindi!');
                    } else {
                        // Ürün miktarını güncelle
                        const quantityInput = form.querySelector('.quantity-input');
                        if (quantityInput && data.new_quantity !== undefined) {
                            quantityInput.value = data.new_quantity;
                        }
                        
                        // Ürün toplam fiyatını güncelle - DOM yapısında doğrudan yolu izleyerek
                        const cartItem = form.closest('.row');
                        if (cartItem) {
                            // 1. Önce birim fiyatı alalım (ilk sütundaki fiyat elementi)
                            const unitPriceEl = cartItem.querySelector('.price-column .fw-bold');
                            // 2. Ardından toplam fiyat elementini bulalım (ikinci sütundaki fiyat elementi)
                            const totalPriceEl = cartItem.querySelectorAll('.price-column .fw-bold')[1];
                            
                            if (unitPriceEl && totalPriceEl && data.new_quantity) {
                                // Birim fiyatı al (₺ işaretini ve boşlukları temizle)
                                const unitPrice = parseFloat(unitPriceEl.textContent.replace('₺', '').trim());
                                // Yeni toplam fiyatı hesapla
                                const totalPrice = unitPrice * data.new_quantity;
                                // Toplam fiyatı güncelle
                                totalPriceEl.textContent = `${totalPrice.toFixed(2)} ₺`;
                                
                                console.log('GÜNCELLEME BAŞARILI:', {
                                    birimFiyat: unitPrice,
                                    miktar: data.new_quantity,
                                    yeniToplam: totalPrice
                                });
                            } else {
                                console.error('Fiyat elementi bulunamadı veya veri eksik', {
                                    unitPriceEl, 
                                    totalPriceEl, 
                                    quantity: data.new_quantity
                                });
                            }
                        }
                        
                        showToast('Miktar güncellendi!');
                    }
                    
                    // Sepet özetini ve toplam fiyatı güncelle - öncelikli olarak bunu yap
                    if (data.toplam_tutar !== undefined) {
                        // Tüm sepet toplamlarını güncelle (genel toplam, kdv vb.)
                        updateCartTotals(data);
                        
                        // Burada toplam sepet fiyatını göstereceğimizden emin olalım
                        // Birim fiyat ve toplam fiyat alanlarını doğrudan güncelle
                        const priceElements = document.querySelectorAll('.cart-summary-total');
                        priceElements.forEach(el => {
                            el.textContent = `${data.genel_toplam.toFixed(2)} ₺`;
                            console.log('Updated cart total price element:', el);
                        });
                    }
                    
                    // Sepet sayacını güncelle
                    updateCartCount(data.cart_count || 0);
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
        
        // Sepetten sil butonu (GÜÇLENDIRILDI)
        else if (e.target.closest('.remove-cart-form button')) {
            e.preventDefault();
            const button = e.target.closest('.remove-cart-form button');
            const form = button.closest('form');
            
            if (!form) return;
            
            // Onay isteme
            if (!confirm('Bu ürünü sepetten kaldırmak istediğinizden emin misiniz?')) {
                return;
            }
            
            // Form URL'sini doğru şekilde al
            const formAction = form.getAttribute('action');
            if (!formAction) {
                console.error('Form action not found');
                return;
            }
            
            const urunAdi = form.dataset.urunAdi || "Ürün";
            const productRow = form.closest('.product-row');
            
            // Önce UI'dan kaldır (hızlı yanıt için)
            if (productRow) {
                productRow.style.opacity = 0.5;  // Siliniyor görünümü
            }
            
            fetch(formAction, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Cache-Control': 'no-cache, no-store'  // Tarayıcı cache'ini engelle
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    console.error(`HTTP error: ${response.status} for URL ${response.url}`);
                    return response.text().then(text => {
                        console.error('Error response text:', text.substring(0, 200));
                        throw new Error(`Server error: ${response.status} for URL ${response.url}`);
                    });
                }
                
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Başarılıysa
                    if (productRow) {
                        productRow.remove();  // DOM'dan tamamen kaldır
                    }
                    
                    // Cart count güncelleme
                    updateCartCount(data.cart_count || 0);
                    
                    // Sepet boşsa mesaj göster
                    const cartItems = document.querySelector('.cart-items');
                    if (data.cart_count === 0 && cartItems) {
                        cartItems.innerHTML = '<div class="alert alert-info">Sepetinizde ürün bulunmuyor.</div>';
                    }
                    
                    // Sepet özetini güncelle
                    if (data.toplam_tutar !== undefined) {
                        updateCartTotals(data);
                    }
                    
                    showToast(`${urunAdi} sepetten silindi!`);
                    
                    // Sayfayı yeniden yükle (en garanti yöntem)
                    setTimeout(() => {
                        window.location.reload();
                    }, 300);
                } else {
                    // Başarısız olursa - error mesajını göster
                    alert("Ürün silinirken bir hata oluştu: " + data.message);
                    
                    // Sayfayı yeniden yükle
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Sepet işlemi sırasında hata:', error);
                alert("İşlem sırasında bir hata oluştu. Sayfa yenileniyor...");
                window.location.reload();
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
