from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.db import transaction
from decimal import Decimal
import json

from .models import Urun, Siparis, SiparisKalemi, Yorum
from .forms import KullaniciKayitFormu, KullaniciGirisFormu, YorumFormu


def sepet_hesapla(sepet):
    """Sepet toplamlarını hesaplar"""
    toplam_tutar = Decimal('0.00')
    
    for urun_id, miktar in sepet.items():
        try:
            urun = Urun.objects.get(id=urun_id)
            ara_toplam = urun.fiyat * miktar
            toplam_tutar += ara_toplam
        except Urun.DoesNotExist:
            pass
    
    kdv_orani = Decimal('0.18')
    kdv_tutari = (toplam_tutar * kdv_orani).quantize(Decimal('0.01'))
    genel_toplam = (toplam_tutar + kdv_tutari).quantize(Decimal('0.01'))
    
    return {
        'toplam_tutar': float(toplam_tutar),
        'kdv_tutari': float(kdv_tutari),
        'genel_toplam': float(genel_toplam)
    }


def product_list_view(request):
    """Ürün listeleme sayfası"""
    urunler = Urun.objects.all().order_by('-olusturulma_tarihi')
    
    # Arama fonksiyonu
    arama = request.GET.get('arama')
    if arama:
        urunler = urunler.filter(
            Q(urun_adi__icontains=arama) | 
            Q(aciklama__icontains=arama) |
            Q(kategori__icontains=arama)
        )
    
    # Kategori filtresi
    kategori = request.GET.get('kategori')
    if kategori:
        urunler = urunler.filter(kategori=kategori)
    
    # Fiyat filtresi
    min_fiyat = request.GET.get('min_fiyat')
    max_fiyat = request.GET.get('max_fiyat')
    if min_fiyat:
        urunler = urunler.filter(fiyat__gte=min_fiyat)
    if max_fiyat:
        urunler = urunler.filter(fiyat__lte=max_fiyat)
    
    # Sıralama
    siralama = request.GET.get('siralama', '-olusturulma_tarihi')
    if siralama == 'fiyat_artan':
        urunler = urunler.order_by('fiyat')
    elif siralama == 'fiyat_azalan':
        urunler = urunler.order_by('-fiyat')
    elif siralama == 'isim_artan':
        urunler = urunler.order_by('urun_adi')
    elif siralama == 'isim_azalan':
        urunler = urunler.order_by('-urun_adi')
    else:
        urunler = urunler.order_by('-olusturulma_tarihi')
    
    # Sayfalama
    paginator = Paginator(urunler, 12)  # Sayfa başına 12 ürün
    sayfa_numarasi = request.GET.get('page')
    sayfa_urunleri = paginator.get_page(sayfa_numarasi)
    
    # Kategoriler listesi (tekrarsız)
    kategoriler = list(set(Urun.objects.values_list('kategori', flat=True).exclude(kategori='')))
    
    context = {
        'urunler': sayfa_urunleri,
        'categories': kategoriler,
        'arama': arama,
        'secili_kategori': kategori,
        'secili_siralama': siralama,
    }
    
    # AJAX isteği kontrolü
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX isteği ise sadece ürün grid'ini döndür
        return render(request, '_product_grid.html', context)
    
    return render(request, 'product_list.html', context)


def product_detail_view(request, id):
    """Ürün detay sayfası"""
    urun = get_object_or_404(Urun, id=id)
    
    # Ürün yorumları
    yorumlar = urun.yorumlar.all().select_related('kullanici')
    
    # Ortalama puan hesaplama
    ortalama_puan = yorumlar.aggregate(ort=Avg('puan'))['ort']
    if ortalama_puan:
        ortalama_puan = round(ortalama_puan, 1)
    
    # Benzer ürünler (aynı kategoriden)
    benzer_urunler = Urun.objects.filter(
        kategori=urun.kategori
    ).exclude(id=urun.id)[:4]
    
    context = {
        'product': urun,
        'reviews': yorumlar,
        'ortalama_puan': ortalama_puan,
        'related_products': benzer_urunler,
    }
    return render(request, 'product_detail.html', context)


def signup_view(request):
    """Kullanıcı kayıt sayfası"""
    print(f"DEBUG - Signup view called with method: {request.method}")
    
    if request.method == 'POST':
        print(f"DEBUG - POST data: {request.POST}")
        form = KullaniciKayitFormu(request.POST)
        print(f"DEBUG - Form created")
        
        if form.is_valid():
            print(f"DEBUG - Form is valid, saving user...")
            kullanici = form.save()
            username = form.cleaned_data.get('username')
            print(f"DEBUG - User {username} created successfully")
            messages.success(request, f'{username} için hesap başarıyla oluşturuldu!')
            login(request, kullanici)
            print(f"DEBUG - User logged in, redirecting...")
            return redirect('product_list')
        else:
            print(f"DEBUG - Form is NOT valid. Errors: {form.errors}")
            print(f"DEBUG - Non-field errors: {form.non_field_errors()}")
            for field, errors in form.errors.items():
                print(f"DEBUG - Field {field} errors: {errors}")
    else:
        print(f"DEBUG - GET request, creating empty form")
        form = KullaniciKayitFormu()
    
    print(f"DEBUG - Rendering signup template")
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    """Kullanıcı giriş sayfası"""
    print(f"DEBUG - Login view called with method: {request.method}")
    
    if request.method == 'POST':
        print(f"DEBUG - POST data: {request.POST}")
        form = KullaniciGirisFormu(request, data=request.POST)
        print(f"DEBUG - Form created")
        
        if form.is_valid():
            print(f"DEBUG - Form is valid")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(f"DEBUG - Attempting authentication for user: {username}")
            kullanici = authenticate(username=username, password=password)
            
            if kullanici is not None:
                print(f"DEBUG - Authentication successful for {username}")
                login(request, kullanici)
                messages.success(request, f'Hoş geldin {username}!')
                next_page = request.GET.get('next', 'product_list')
                print(f"DEBUG - Redirecting to: {next_page}")
                return redirect(next_page)
            else:
                print(f"DEBUG - Authentication failed for user: {username}")
                messages.error(request, 'Kullanıcı adı veya şifre hatalı!')
        else:
            print(f"DEBUG - Form is NOT valid. Errors: {form.errors}")
            messages.error(request, 'Kullanıcı adı veya şifre hatalı!')
    else:
        print(f"DEBUG - GET request, creating empty form")
        form = KullaniciGirisFormu()
    
    print(f"DEBUG - Rendering login template")
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Kullanıcı çıkış"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız!')
    return redirect('product_list')


@login_required
def profile_view(request):
    """Kullanıcı profil sayfası"""
    context = {
        'user': request.user,
    }
    return render(request, 'profile.html', context)


@login_required
def profile_edit_view(request):
    """Kullanıcı profil düzenleme sayfası"""
    if request.method == 'POST':
        # Form verileri alınır
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        
        # Kullanıcı bilgilerini güncelle
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        # Başarılı işlem sonrası profil sayfasına yönlendir
        messages.success(request, 'Profil bilgileriniz başarıyla güncellendi.')
        return redirect('profile')
    
    context = {
        'user': request.user,
    }
    return render(request, 'profile_edit.html', context)


@login_required
def order_history_view(request):
    """Kullanıcının sipariş geçmişi"""
    siparisler = Siparis.objects.filter(kullanici=request.user).order_by('-siparis_tarihi')
    return render(request, 'order_history.html', {'siparisler': siparisler})


def sepet_goruntule(request):
    """Sepet görüntüleme sayfası"""
    sepet = request.session.get('sepet', {})
    sepet_urunleri = []
    toplam_tutar = Decimal('0.00')
    
    for urun_id, miktar in sepet.items():
        try:
            urun = Urun.objects.get(id=urun_id)
            ara_toplam = urun.fiyat * miktar
            toplam_tutar += ara_toplam
            
            # Ürün resim URL'sini context'e ekle
            resim_url = None
            if urun.resim_url:
                resim_url = urun.resim_url
                
            sepet_urunleri.append({
                'urun': urun,
                'miktar': miktar,
                'ara_toplam': ara_toplam,
                'resim_url': resim_url
            })
        except Urun.DoesNotExist:
            # Silinmiş ürünü sepetten kaldır
            del sepet[urun_id]
            request.session['sepet'] = sepet
    
    # Vergi ve genel toplam hesapla
    kdv_orani = Decimal('0.18')
    kdv_tutari = (toplam_tutar * kdv_orani).quantize(Decimal('0.01'))
    genel_toplam = (toplam_tutar + kdv_tutari).quantize(Decimal('0.01'))

    context = {
        'sepet_urunleri': sepet_urunleri,
        'toplam_tutar': toplam_tutar,
        'kdv_tutari': kdv_tutari,
        'genel_toplam': genel_toplam,
        'sepet_bos': len(sepet_urunleri) == 0
    }
    return render(request, 'cart.html', context)


def sepete_ekle(request, urun_id):
    """Ürünü sepete ekleme"""
    urun = get_object_or_404(Urun, id=urun_id)
    
    # Stok kontrolü
    if not urun.is_stokta:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'{urun.urun_adi} stokta bulunmuyor!'
            })
        else:
            messages.error(request, f'{urun.urun_adi} stokta bulunmuyor!')
            return redirect('product_list')
    
    sepet = request.session.get('sepet', {})
    urun_id_str = str(urun_id)
    
    # Miktar kontrolü
    mevcut_miktar = sepet.get(urun_id_str, 0)
    if mevcut_miktar >= urun.stok_adedi:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'{urun.urun_adi} için maksimum stok miktarına ulaşıldı!'
            })
        else:
            messages.error(request, f'{urun.urun_adi} için maksimum stok miktarına ulaşıldı!')
            return redirect('product_list')
    
    # Sepete ekle
    sepet[urun_id_str] = mevcut_miktar + 1
    request.session['sepet'] = sepet
    
    # Sepet toplam ürün sayısını hesapla
    toplam_urun = sum(sepet.values())
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{urun.urun_adi} sepete eklendi!',
            'cart_count': toplam_urun
        })
    else:
        messages.success(request, f'{urun.urun_adi} sepete eklendi!')
        return redirect('product_list')


def sepetten_sil(request, urun_id):
    """Ürünü sepetten silme"""
    sepet = request.session.get('sepet', {})
    urun_id_str = str(urun_id)
    
    if urun_id_str in sepet:
        urun = get_object_or_404(Urun, id=urun_id)
        del sepet[urun_id_str]
        request.session['sepet'] = sepet
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Sepet toplamlarını hesapla
            sepet_toplam = sepet_hesapla(sepet)
            
            return JsonResponse({
                'success': True,
                'message': f'{urun.urun_adi} sepetten silindi!',
                'cart_count': sum(sepet.values()),
                'toplam_tutar': sepet_toplam['toplam_tutar'],
                'kdv_tutari': sepet_toplam['kdv_tutari'],
                'genel_toplam': sepet_toplam['genel_toplam']
            })
        else:
            messages.success(request, f'{urun.urun_adi} sepetten silindi!')
            return redirect('cart')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'message': 'Ürün sepette bulunamadı!'
        })
    else:
        messages.error(request, 'Ürün sepette bulunamadı!')
        return redirect('cart')


@require_POST
def sepet_guncelle(request, urun_id):
    """Sepetteki ürün miktarını güncelleme"""
    try:
        print(f"sepet_guncelle called - Method: {request.method}, urun_id: {urun_id}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"POST data: {request.POST}")
        
        if request.method == 'POST':
            sepet = request.session.get('sepet', {})
            urun_id_str = str(urun_id)
            
            if urun_id_str in sepet:
                mevcut_miktar = sepet[urun_id_str]
                
                # Action değerini kontrol et (increase/decrease)
                action = request.POST.get('action')
                
                if action == 'increase':
                    yeni_miktar = mevcut_miktar + 1
                elif action == 'decrease':
                    yeni_miktar = mevcut_miktar - 1
                else:
                    # Form data veya JSON data kontrolü
                    if request.content_type == 'application/json':
                        try:
                            data = json.loads(request.body)
                            yeni_miktar = int(data.get('miktar', 1))
                        except (ValueError, json.JSONDecodeError):
                            return JsonResponse({
                                'success': False,
                                'message': 'Geçersiz miktar!'
                            })
                    else:
                        try:
                            yeni_miktar = int(request.POST.get('miktar', 1))
                        except (ValueError, TypeError):
                            return JsonResponse({
                                'success': False,
                                'message': 'Geçersiz miktar değeri!'
                            })
                
                if yeni_miktar > 0:
                    # Stok kontrolü
                    urun = get_object_or_404(Urun, id=urun_id)
                    if yeni_miktar <= urun.stok_adedi:
                        sepet[urun_id_str] = yeni_miktar
                        request.session['sepet'] = sepet
                        
                        # Yeni toplam hesapla
                        yeni_toplam = urun.fiyat * yeni_miktar
                        
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            # Sepet toplamlarını hesapla
                            sepet_toplam = sepet_hesapla(sepet)
                            
                            return JsonResponse({
                                'success': True,
                                'message': 'Miktar güncellendi!',
                                'new_quantity': yeni_miktar,
                                'new_total': float(yeni_toplam),
                                'cart_count': sum(sepet.values()),
                                'toplam_tutar': sepet_toplam['toplam_tutar'],
                                'kdv_tutari': sepet_toplam['kdv_tutari'],
                                'genel_toplam': sepet_toplam['genel_toplam']
                            })
                        else:
                            messages.success(request, 'Miktar güncellendi!')
                            return redirect('cart')
                    else:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'message': f'Stokta sadece {urun.stok_adedi} adet var!'
                            })
                        else:
                            messages.error(request, f'Stokta sadece {urun.stok_adedi} adet var!')
                            return redirect('cart')
                else:
                    # Miktar 0 ise ürünü sil
                    del sepet[urun_id_str]
                    request.session['sepet'] = sepet
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        # Sepet toplamlarını hesapla
                        sepet_toplam = sepet_hesapla(sepet)
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Ürün sepetten silindi!',
                            'cart_count': sum(sepet.values()),
                            'toplam_tutar': sepet_toplam['toplam_tutar'],
                            'kdv_tutari': sepet_toplam['kdv_tutari'],
                            'genel_toplam': sepet_toplam['genel_toplam']
                        })
                    else:
                        messages.success(request, 'Ürün sepetten silindi!')
                        return redirect('cart')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Ürün sepette bulunamadı!'
                    })
                else:
                    messages.error(request, 'Ürün sepette bulunamadı!')
                    return redirect('cart')
        
        return redirect('cart')
        
    except Exception as e:
        # Tüm beklenmeyen hataları yakala
        print(f"Sepet güncelleme hatası: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Bir hata oluştu. Lütfen tekrar deneyin.'
            })
        else:
            messages.error(request, 'Bir hata oluştu. Lütfen tekrar deneyin.')
            return redirect('cart')


@require_POST
def sepet_bosalt(request):
    """Sepeti tamamen boşaltma"""
    request.session['sepet'] = {}
    return JsonResponse({
        'success': True,
        'message': 'Sepet boşaltıldı!',
        'cart_count': 0
    })


@login_required
def checkout_view(request):
    """Ödeme sayfası - Sepetten siparişe geçiş"""
    sepet = request.session.get('sepet', {})
    
    if not sepet:
        messages.error(request, 'Sepetiniz boş!')
        return redirect('sepet_goruntule')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Sepetteki ürünlerin güncel stok durumunu kontrol et
                sepet_urunleri = []
                toplam_tutar = Decimal('0.00')
                
                for urun_id, miktar in sepet.items():
                    urun = get_object_or_404(Urun, id=urun_id)
                    
                    # Stok kontrolü
                    if urun.stok_adedi < miktar:
                        messages.error(
                            request,
                            f'{urun.urun_adi} için yeterli stok yok! '
                            f'Stokta {urun.stok_adedi} adet var.'
                        )
                        return redirect('sepet_goruntule')
                    
                    sepet_urunleri.append({
                        'urun': urun,
                        'miktar': miktar,
                        'birim_fiyat': urun.fiyat
                    })
                    toplam_tutar += urun.fiyat * miktar
                
                # Sipariş oluştur
                siparis = Siparis.objects.create(
                    kullanici=request.user,
                    toplam_tutar=toplam_tutar
                )
                
                # Sipariş kalemlerini oluştur ve stokları güncelle
                for sepet_urun in sepet_urunleri:
                    SiparisKalemi.objects.create(
                        siparis=siparis,
                        urun=sepet_urun['urun'],
                        miktar=sepet_urun['miktar'],
                        birim_fiyat=sepet_urun['birim_fiyat']
                    )
                    
                    # Stok güncelle
                    sepet_urun['urun'].stok_adedi -= sepet_urun['miktar']
                    sepet_urun['urun'].save()
                
                # Sepeti temizle
                request.session['sepet'] = {}
                
                messages.success(request, 'Siparişiniz başarıyla oluşturuldu!')
                return redirect('order_confirmation', siparis_id=siparis.id)
                
        except Exception as e:
            messages.error(request, 'Sipariş oluşturulurken bir hata oluştu!')
            return redirect('sepet_goruntule')
    
    # GET request - checkout sayfasını göster
    sepet_urunleri = []
    toplam_tutar = Decimal('0.00')
    
    for urun_id, miktar in sepet.items():
        urun = get_object_or_404(Urun, id=urun_id)
        urun_toplam = urun.fiyat * miktar
        sepet_urunleri.append({
            'urun': urun,
            'miktar': miktar,
            'toplam': urun_toplam
        })
        toplam_tutar += urun_toplam
    
    context = {
        'sepet_urunleri': sepet_urunleri,
        'toplam_tutar': toplam_tutar,
    }
    return render(request, 'checkout.html', context)


@login_required
def order_confirmation_view(request, siparis_id):
    """Sipariş onay sayfası"""
    siparis = get_object_or_404(
        Siparis.objects.select_related('kullanici').prefetch_related('kalemler__urun'),
        id=siparis_id,
        kullanici=request.user
    )
    
    context = {
        'siparis': siparis,
    }
    return render(request, 'order_confirmation.html', context)


@login_required
@require_POST
def yorum_ekle(request, urun_id):
    """Ürüne yorum ekleme"""
    urun = get_object_or_404(Urun, id=urun_id)
    
    # Kullanıcının bu ürüne daha önce yorum yapıp yapmadığını kontrol et
    mevcut_yorum = Yorum.objects.filter(urun=urun, kullanici=request.user).first()
    if mevcut_yorum:
        return JsonResponse({
            'success': False,
            'message': 'Bu ürüne daha önce yorum yaptınız!'
        })
    
    try:
        data = json.loads(request.body)
        puan = int(data.get('puan'))
        yorum_metni = data.get('yorum_metni', '').strip()
        
        if not (1 <= puan <= 5):
            return JsonResponse({
                'success': False,
                'message': 'Puan 1-5 arasında olmalıdır!'
            })
        
        if not yorum_metni:
            return JsonResponse({
                'success': False,
                'message': 'Yorum metni boş olamaz!'
            })
        
        # Yorum oluştur
        Yorum.objects.create(
            urun=urun,
            kullanici=request.user,
            puan=puan,
            yorum_metni=yorum_metni
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Yorumunuz başarıyla eklendi!'
        })
        
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({
            'success': False,
            'message': 'Geçersiz veri!'
        })