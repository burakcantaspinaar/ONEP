from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError
from decimal import Decimal
import json

from .models import Urun, Siparis, SiparisKalemi, Yorum


class UrunModelTest(TestCase):
    """Ürün modeli testleri"""
    
    def setUp(self):
        self.urun = Urun.objects.create(
            urun_adi="Test Ürün",
            aciklama="Test açıklama",
            fiyat=Decimal('100.00'),
            stok_adedi=10,
            kategori="Test Kategori"
        )
    
    def test_urun_str_representation(self):
        """Ürün string temsilini test et"""
        expected = f"{self.urun.urun_adi} - {self.urun.fiyat} TL"
        self.assertEqual(str(self.urun), expected)
    
    def test_is_stokta_property_true(self):
        """Stokta olan ürün için is_stokta property'si True olmalı"""
        self.assertTrue(self.urun.is_stokta)
    
    def test_is_stokta_property_false(self):
        """Stokta olmayan ürün için is_stokta property'si False olmalı"""
        self.urun.stok_adedi = 0
        self.urun.save()
        self.assertFalse(self.urun.is_stokta)


class YorumModelTest(TestCase):
    """Yorum modeli testleri"""
    
    def setUp(self):
        self.kullanici = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.urun = Urun.objects.create(
            urun_adi="Test Ürün",
            aciklama="Test açıklama",
            fiyat=Decimal('100.00'),
            stok_adedi=10
        )
    
    def test_unique_together_constraint(self):
        """Bir kullanıcının aynı ürüne ikinci bir yorum yapamaması"""
        # İlk yorum
        Yorum.objects.create(
            urun=self.urun,
            kullanici=self.kullanici,
            puan=5,
            yorum_metni="Harika ürün!"
        )
        
        # İkinci yorum - hata vermeli
        with self.assertRaises(IntegrityError):
            Yorum.objects.create(
                urun=self.urun,
                kullanici=self.kullanici,
                puan=4,
                yorum_metni="İkinci yorum"
            )


class SepetYonetimiTest(TestCase):
    """Sepet yönetimi testleri"""
    
    def setUp(self):
        self.client = Client()
        self.kullanici = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.urun = Urun.objects.create(
            urun_adi="Test Ürün",
            aciklama="Test açıklama",
            fiyat=Decimal('100.00'),
            stok_adedi=5
        )
    
    def test_stokta_olmayan_urun_sepete_eklenemez(self):
        """Stokta olmayan bir ürünün sepete eklenememesi"""
        # Ürünü stoksuz yap
        self.urun.stok_adedi = 0
        self.urun.save()
        
        # Sepete eklemeye çalış
        response = self.client.post(
            reverse('sepete_ekle', args=[self.urun.id])
        )
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('stokta bulunmuyor', data['message'])
    
    def test_stokta_olan_urun_sepete_eklenebilir(self):
        """Stokta olan ürünün sepete eklenebilmesi"""
        response = self.client.post(
            reverse('sepete_ekle', args=[self.urun.id])
        )
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 1)
    
    def test_stok_miktari_asimi_engellenir(self):
        """Stok miktarını aşan sepet ekleme engellenmeli"""
        # Stok miktarı kadar ürün ekle
        for i in range(self.urun.stok_adedi):
            self.client.post(reverse('sepete_ekle', args=[self.urun.id]))
        
        # Bir tane daha eklemeye çalış - hata vermeli
        response = self.client.post(
            reverse('sepete_ekle', args=[self.urun.id])
        )
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('maksimum stok miktarına ulaşıldı', data['message'])


class SiparisYonetimiTest(TestCase):
    """Sipariş yönetimi testleri"""
    
    def setUp(self):
        self.client = Client()
        self.kullanici = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.urun = Urun.objects.create(
            urun_adi="Test Ürün",
            aciklama="Test açıklama",
            fiyat=Decimal('100.00'),
            stok_adedi=10
        )
        # Kullanıcıyı giriş yap
        self.client.login(username='testuser', password='testpass123')
    
    def test_sepetten_siparis_olusturuldiginda_stok_duser(self):
        """Sepetten sipariş oluşturulduğunda stok miktarının doğru şekilde düşmesi"""
        # Başlangıç stok miktarı
        baslangic_stok = self.urun.stok_adedi
        siparis_miktari = 3
        
        # Sepete ürün ekle
        session = self.client.session
        session['sepet'] = {str(self.urun.id): siparis_miktari}
        session.save()
        
        # Sipariş oluştur
        response = self.client.post(reverse('checkout'))
        
        # Ürünü yeniden yükle ve stok kontrolü yap
        self.urun.refresh_from_db()
        beklenen_stok = baslangic_stok - siparis_miktari
        self.assertEqual(self.urun.stok_adedi, beklenen_stok)
    
    def test_siparis_kalemi_olusturulur(self):
        """Sipariş oluşturulduğunda sipariş kalemlerinin doğru oluşturulması"""
        siparis_miktari = 2
        
        # Sepete ürün ekle
        session = self.client.session
        session['sepet'] = {str(self.urun.id): siparis_miktari}
        session.save()
        
        # Sipariş oluştur
        response = self.client.post(reverse('checkout'))
        
        # Sipariş ve sipariş kalemlerini kontrol et
        siparis = Siparis.objects.filter(kullanici=self.kullanici).first()
        self.assertIsNotNone(siparis)
        
        siparis_kalemi = SiparisKalemi.objects.filter(siparis=siparis).first()
        self.assertIsNotNone(siparis_kalemi)
        self.assertEqual(siparis_kalemi.adet, siparis_miktari)
        self.assertEqual(siparis_kalemi.birim_fiyat, self.urun.fiyat)
    
    def test_sepet_siparisiten_sonra_temizlenir(self):
        """Sipariş oluşturduktan sonra sepetin temizlenmesi"""
        # Sepete ürün ekle
        session = self.client.session
        session['sepet'] = {str(self.urun.id): 2}
        session.save()
        
        # Sipariş oluştur
        response = self.client.post(reverse('checkout'))
        
        # Sepet temizlenmiş olmalı
        self.assertEqual(self.client.session.get('sepet', {}), {})


class GuvenlikTestleri(TestCase):
    """Güvenlik ve izin testleri"""
    
    def setUp(self):
        self.client = Client()
        self.kullanici = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.urun = Urun.objects.create(
            urun_adi="Test Ürün",
            aciklama="Test açıklama",
            fiyat=Decimal('100.00'),
            stok_adedi=10
        )
    
    def test_giris_yapmamis_kullanici_korunali_sayfalara_erisemez(self):
        """Giriş yapmamış kullanıcının korumalı sayfalara erişememesi"""
        korunali_sayfalar = [
            'checkout',
            'order_history',
        ]
        
        for sayfa in korunali_sayfalar:
            response = self.client.get(reverse(sayfa))
            # Login sayfasına yönlendirme olmalı
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login/', response.url)
    
    def test_giris_yapmis_kullanici_korunali_sayfalara_erisebilir(self):
        """Giriş yapmış kullanıcının korumalı sayfalara erişebilmesi"""
        # Kullanıcıyı giriş yap
        self.client.login(username='testuser', password='testpass123')
        
        korunali_sayfalar = [
            'order_history',
        ]
        
        for sayfa in korunali_sayfalar:
            response = self.client.get(reverse(sayfa))
            self.assertEqual(response.status_code, 200)
    
    def test_yorum_ekleme_icin_giris_gerekli(self):
        """Yorum ekleme için giriş yapılması gerekli"""
        response = self.client.post(
            reverse('yorum_ekle', args=[self.urun.id]),
            data=json.dumps({'puan': 5, 'yorum_metni': 'Test yorum'}),
            content_type='application/json'
        )
        
        # 302 (redirect) dönmeli - login sayfasına yönlendirme
        self.assertEqual(response.status_code, 302)


class FormTestleri(TestCase):
    """Form validasyon testleri"""
    
    def test_kullanici_kayit_formu_gecerli_veri(self):
        """Kullanıcı kayıt formunun geçerli veriyle çalışması"""
        from .forms import KullaniciKayitFormu
        
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        
        form = KullaniciKayitFormu(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_kullanici_kayit_formu_email_benzersizlik(self):
        """E-posta benzersizlik kontrolü"""
        from .forms import KullaniciKayitFormu
        
        # İlk kullanıcıyı oluştur
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='pass123'
        )
        
        # Aynı e-posta ile ikinci kullanıcı kayıt formunu test et
        form_data = {
            'username': 'user2',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',  # Aynı e-posta
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        
        form = KullaniciKayitFormu(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Bu e-posta adresi zaten kullanılıyor', form.errors['email'][0])


class ViewTestleri(TestCase):
    """View fonksiyonları testleri"""
    
    def setUp(self):
        self.client = Client()
        self.urun = Urun.objects.create(
            urun_adi="Test Ürün",
            aciklama="Test açıklama",
            fiyat=Decimal('100.00'),
            stok_adedi=10,
            kategori="Test Kategori"
        )
    
    def test_product_list_view_calisiyor(self):
        """Ürün listeleme sayfasının çalışması"""
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.urun.urun_adi)
    
    def test_product_detail_view_calisiyor(self):
        """Ürün detay sayfasının çalışması"""
        response = self.client.get(reverse('product_detail', args=[self.urun.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.urun.urun_adi)
    
    def test_sepet_goruntuleme_calisiyor(self):
        """Sepet görüntüleme sayfasının çalışması"""
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
    
    def test_urun_arama_fonksiyonu(self):
        """Ürün arama fonksiyonunun çalışması"""
        response = self.client.get(reverse('product_list'), {'arama': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.urun.urun_adi)
        
        # Bulunamayan arama
        response = self.client.get(reverse('product_list'), {'arama': 'Bulunamaz'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.urun.urun_adi)
