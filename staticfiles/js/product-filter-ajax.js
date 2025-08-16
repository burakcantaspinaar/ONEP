// static/js/product-filter-ajax.js

document.addEventListener('DOMContentLoaded', function () {
    const productGrid = document.getElementById('productsGrid');
    const categoryLinks = document.querySelectorAll('.category-filter .filter-btn');
    const sortSelect = document.querySelector('.sort-dropdown');

    function fetchProducts(url) {
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            // Gelen HTML'i geçici bir elemente yükle ve sadece ürün grid'ini al
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newGrid = doc.getElementById('productsGrid');
            const newPagination = doc.querySelector('.pagination-container');

            if (newGrid) {
                productGrid.innerHTML = newGrid.innerHTML;
            }
            
            // Sayfalamayı güncelle
            const paginationContainer = document.querySelector('.pagination-container');
            if (paginationContainer && newPagination) {
                paginationContainer.innerHTML = newPagination.innerHTML;
            } else if (paginationContainer) {
                paginationContainer.innerHTML = ''; // Sonuç yoksa sayfalamayı temizle
            }

            // URL'yi tarayıcı geçmişine ekle
            history.pushState(null, '', url);
        })
        .catch(error => console.error('Filtreleme hatası:', error));
    }

    // Kategori linklerine event listener ekle
    categoryLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.href;
            
            // Aktif class'ını yönet
            categoryLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            fetchProducts(url);
        });
    });

    // Sıralama seçeneğine event listener ekle
    if (sortSelect) {
        sortSelect.addEventListener('change', function () {
            const url = new URL(window.location.href);
            url.searchParams.set('siralama', this.value);
            fetchProducts(url.toString());
        });
    }
    
    // Sayfalama linklerini dinamik olarak yönet
    document.body.addEventListener('click', function(e) {
        if (e.target.closest('.pagination a')) {
            e.preventDefault();
            const link = e.target.closest('.pagination a');
            fetchProducts(link.href);
        }
    });
});
