# ONEP E-Commerce Platform - AI Coding Instructions

## Project Overview
ONEP is a **FULLY FUNCTIONAL** Turkish Django-based e-commerce platform with PostgreSQL backend. Both frontend and backend are complete and operational.

## Current Implementation Status ✅ COMPLETE

### ✅ Frontend (Turkish E-Commerce UI)
- **Templates**: 11 HTML templates in `onep/templates/` including AJAX partials (`_product_grid.html`)
- **Styling**: Complete CSS system in `static/css/style.css` with Bootstrap 5.3.0 integration
- **JavaScript**: AJAX-powered cart operations in `static/js/cart-ajax.js` with CSRF protection
- **UI Components**: Responsive design with custom gradients and Turkish navigation

### ✅ Backend (Django Implementation)
- **Project Structure**: `ONEP_ORG/` (Django project) + `onep/` (Django app)
- **Database**: PostgreSQL with fully migrated Turkish models (Urun, Siparis, SiparisKalemi, Yorum)
- **Authentication**: Complete Django auth system with Turkish forms
- **Features**: Product management, session-based cart, order processing, review system, AJAX operations

## Architecture & Critical Structure

### Django Project Structure (IMPORTANT!)
```
ONEP/
├── manage.py                    # Entry point
├── ONEP_ORG/                   # Django PROJECT directory
│   ├── settings.py             # DJANGO_SETTINGS_MODULE='ONEP_ORG.settings'
│   ├── urls.py                 # Main URL config
│   ├── wsgi.py/asgi.py        # Deployment configs
├── onep/                       # Django APP directory
│   ├── models.py               # Turkish models (Urun, Siparis, etc.)
│   ├── views.py                # Function-based views
│   ├── urls.py                 # App URLs (no app_name!)
│   ├── context_processors.py   # Global cart context
│   ├── templates/              # 11 Turkish HTML templates + AJAX partials
│   └── migrations/             # Database migrations
└── static/                     # CSS/JS assets
    ├── css/style.css           # Bootstrap 5.3.0 + custom styling
    └── js/cart-ajax.js         # AJAX cart operations with CSRF
```

### Session-Based Cart Architecture (Critical Pattern)
- **No cart database model** - uses Django sessions exclusively
- **Global context**: `onep.context_processors.cart_context` provides `cart_count` to all templates
- **AJAX operations**: Real-time cart updates via `static/js/cart-ajax.js`
- **Price calculations**: Server-side in `views.sepet_hesapla()` with KDV (18% Turkish tax)

### Turkish Naming Convention (Project-Specific)
- **Models**: Turkish class names (`Urun`, `Siparis`, `SiparisKalemi`, `Yorum`)
- **Fields**: Turkish snake_case (`urun_adi`, `siparis_durumu`, `olusturulma_tarihi`)
- **Views**: Mixed Turkish/English (`sepete_ekle`, `sepet_guncelle`, `product_list_view`)
- **URLs**: Turkish function names (`sepete_ekle`, `sepetten_sil`, `sepet_bosalt`)

### Database Configuration (PostgreSQL)
```python
# ONEP_ORG/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'onep_db',
        'USER': 'postgres',
        'PASSWORD': 'Selam.235689.',  # Current setup
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

## Development Workflow

### Essential Commands
```bash
# Start development server
python manage.py runserver

# Database operations
python manage.py makemigrations onep
python manage.py migrate
python manage.py createsuperuser

# Access points
# Frontend: http://127.0.0.1:8000/
# Admin: http://127.0.0.1:8000/admin/
```

### Key URL Patterns (NO app_name namespace)
```python
# onep/urls.py - Direct URL names (no 'onep:' prefix)
urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('product/<int:id>/', views.product_detail_view, name='product_detail'),
    path('login/', views.login_view, name='login'),
    path('cart/', views.sepet_goruntule, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    # Turkish function names for cart operations
    path('cart/add/<int:urun_id>/', views.sepete_ekle, name='sepete_ekle'),
    path('cart/update/<int:urun_id>/', views.sepet_guncelle, name='sepet_guncelle'),
    path('cart/remove/<int:urun_id>/', views.sepetten_sil, name='sepetten_sil'),
]
```

### AJAX Cart Operations (Critical Pattern)
```javascript
// static/js/cart-ajax.js - CSRF-protected AJAX requests
const csrftoken = getCookie('csrftoken');
fetch(form.getAttribute('action'), {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
})
```

## Session-Based Cart System (Key Pattern)

### Cart Operations in Views
```python
# onep/views.py - Session cart pattern
def sepete_ekle(request, urun_id):
    sepet = request.session.get('sepet', {})
    sepet[str(urun_id)] = sepet.get(str(urun_id), 0) + 1
    request.session['sepet'] = sepet
    return JsonResponse({'success': True, 'cart_count': sum(sepet.values())})

def sepet_guncelle(request, urun_id):
    if request.method == 'POST':
        miktar = int(request.POST.get('miktar', 1))
        sepet = request.session.get('sepet', {})
        
        if miktar <= 0:
            # Remove item if quantity is 0 or less
            sepet.pop(str(urun_id), None)
        else:
            sepet[str(urun_id)] = miktar
            
        request.session['sepet'] = sepet
        totals = sepet_hesapla(sepet)
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(sepet.values()),
            'new_total': totals['toplam_tutar'],
            **totals
        })

def sepet_hesapla(sepet):
    """Calculate cart totals with 18% Turkish VAT (KDV)"""
    toplam_tutar = Decimal('0.00')
    for urun_id, miktar in sepet.items():
        try:
            urun = Urun.objects.get(id=urun_id)
            toplam_tutar += urun.fiyat * miktar
        except Urun.DoesNotExist:
            pass
    
    kdv_orani = Decimal('0.18')  # 18% Turkish VAT
    kdv_tutari = (toplam_tutar * kdv_orani).quantize(Decimal('0.01'))
    genel_toplam = (toplam_tutar + kdv_tutari).quantize(Decimal('0.01'))
    
    return {
        'toplam_tutar': float(toplam_tutar),
        'kdv_tutari': float(kdv_tutari),
        'genel_toplam': float(genel_toplam)
    }
```

### Global Cart Context
```python
# onep/context_processors.py - Available in all templates
def cart_context(request):
    sepet = request.session.get('sepet', {})
    cart_count = sum(sepet.values()) if sepet else 0
    return {'cart_count': cart_count, 'cart_items': sepet}
```

## Turkish Model Architecture (Critical Pattern)

### Core Models with Turkish Field Names
```python
# onep/models.py - Turkish naming convention
class Urun(models.Model):
    urun_adi = models.CharField(max_length=200, verbose_name="Ürün Adı")
    aciklama = models.TextField(verbose_name="Açıklama")
    fiyat = models.DecimalField(max_digits=10, decimal_places=2, 
                               validators=[MinValueValidator(Decimal('0.01'))])
    stok_adedi = models.PositiveIntegerField(default=0)
    kategori = models.CharField(max_length=100, blank=True)
    resim_url = models.URLField(blank=True, null=True)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

class Siparis(models.Model):
    SIPARIS_DURUMLARI = [
        ('beklemede', 'Beklemede'),
        ('onaylandi', 'Onaylandı'),
        ('kargolandi', 'Kargolandı'),
        ('teslim_edildi', 'Teslim Edildi'),
        ('iptal_edildi', 'İptal Edildi'),
    ]
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    toplam_tutar = models.DecimalField(max_digits=10, decimal_places=2)
    siparis_durumu = models.CharField(max_length=20, choices=SIPARIS_DURUMLARI, default='beklemede')
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

class SiparisKalemi(models.Model):
    siparis = models.ForeignKey(Siparis, on_delete=models.CASCADE, related_name='kalemler')
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE)
    miktar = models.PositiveIntegerField()
    birim_fiyat = models.DecimalField(max_digits=10, decimal_places=2)

class Yorum(models.Model):
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE, related_name='yorumlar')
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    yorum_metni = models.TextField()
    puan = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
```

## Template Integration (Critical)

### URL Template Usage
```html
<!-- All templates use direct URL names (no namespace) -->
<a href="{% url 'product_list' %}">Ana Sayfa</a>
<a href="{% url 'cart' %}">Sepet</a>
<form action="{% url 'sepete_ekle' urun.id %}" method="post">
```

### AJAX Partial Templates
- `_product_grid.html`: Partial template for AJAX product loading
- Used for search/filter updates without full page reload
- Loaded via `X-Requested-With: XMLHttpRequest` header detection

### Context Requirements
- `product_list.html`: `urunler` (paginated), `categories`, search/filter params
- `product_detail.html`: `product`, `reviews`, `related_products`, `yorum_formu`
- `cart.html`: session cart items, `toplam_fiyat`, quantity controls with data attributes
- `base.html`: global `cart_count` via context processor

### Form Patterns
```python
# onep/forms.py - Turkish form labels
class KullaniciKayitFormu(UserCreationForm):
    email = forms.EmailField(label="E-posta")
    ad = forms.CharField(max_length=30, label="Ad")
    soyad = forms.CharField(max_length=30, label="Soyad")

class YorumFormu(forms.ModelForm):
    class Meta:
        model = Yorum
        fields = ['yorum_metni', 'puan']
        labels = {'yorum_metni': 'Yorumunuz', 'puan': 'Puanınız'}
```

## Troubleshooting & Common Issues

### URL Reverse Errors
- **Problem**: `NoReverseMatch` for URL names
- **Solution**: Remove `app_name` from `onep/urls.py` (currently correct)
- **Check**: Templates use direct names: `{% url 'product_list' %}` not `{% url 'onep:product_list' %}`

### AJAX Cart Issues
- **CSRF Protection**: Always include `X-CSRFToken` header in AJAX requests
- **Form URLs**: Use `form.getAttribute('action')` not `form.action` for correct URL handling
- **Response Handling**: Backend returns JSON with `success`, `cart_count`, and pricing data
- **DOM Updates**: Target specific elements for price updates: `.cart-summary-total`, `.product-row-total`

### PostgreSQL Connection
- **Database**: `onep_db` must exist in PostgreSQL
- **User**: `postgres` with password `Selam.235689.`
- **Test**: `psql -U postgres -d onep_db -h 127.0.0.1`

### Static Files
- **Development**: `STATIC_URL = '/static/'`
- **Files**: CSS in `static/css/style.css`, JS in `static/js/cart-ajax.js`
- **Templates**: `{% load static %}` and `{% static 'css/style.css' %}`

## Turkish Conventions (Project-Specific)

### Naming Patterns
- **Models**: Turkish class names (`Urun`, `Siparis`, `Yorum`)
- **Fields**: Turkish snake_case (`urun_adi`, `siparis_durumu`, `olusturulma_tarihi`)
- **Views**: Mixed Turkish/English (`sepete_ekle`, `product_list_view`)
- **Templates**: Turkish content, English template tags

## Integration Points

### Admin Interface
- Turkish verbose names in models
- Custom admin configuration in `onep/admin.py`
- Access: `/admin/` with superuser credentials

### Frontend-Backend Data Flow
- Session-based cart (no database storage)
- AJAX cart operations with CSRF tokens
- Bootstrap modals for user interactions
- Turkish error messages and success notifications
