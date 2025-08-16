from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Urun(models.Model):
    """Ürün modeli - e-ticaret platformundaki ürünleri temsil eder"""
    
    urun_adi = models.CharField(
        max_length=200, 
        verbose_name="Ürün Adı",
        help_text="Ürünün tam adını giriniz"
    )
    aciklama = models.TextField(
        verbose_name="Açıklama",
        help_text="Ürün hakkında detaylı bilgi"
    )
    fiyat = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Fiyat",
        help_text="Ürün fiyatı (TL)"
    )
    stok_adedi = models.PositiveIntegerField(
        default=0,
        verbose_name="Stok Adedi",
        help_text="Mevcut stok miktarı"
    )
    kategori = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Kategori",
        help_text="Ürün kategorisi"
    )
    resim_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Resim URL",
        help_text="Ürün resim bağlantısı"
    )
    olusturulma_tarihi = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    guncellenme_tarihi = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )
    
    @property
    def is_stokta(self):
        """Ürünün stokta olup olmadığını kontrol eder"""
        return self.stok_adedi > 0
    
    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ['-olusturulma_tarihi']
    
    def __str__(self):
        return f"{self.urun_adi} - {self.fiyat} TL"


class Siparis(models.Model):
    """Sipariş modeli - kullanıcı siparişlerini temsil eder"""
    
    DURUM_SECENEKLERI = [
        ('beklemede', 'Beklemede'),
        ('hazirlaniyor', 'Hazırlanıyor'),
        ('kargoda', 'Kargoda'),
        ('teslim_edildi', 'Teslim Edildi'),
        ('iptal_edildi', 'İptal Edildi'),
    ]
    
    kullanici = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı",
        related_name="siparisler"
    )
    siparis_tarihi = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Sipariş Tarihi"
    )
    toplam_tutar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Toplam Tutar",
        help_text="Siparişin toplam tutarı (TL)"
    )
    durum = models.CharField(
        max_length=20,
        choices=DURUM_SECENEKLERI,
        default='beklemede',
        verbose_name="Sipariş Durumu"
    )
    
    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"
        ordering = ['-siparis_tarihi']
    
    def __str__(self):
        return f"Sipariş #{self.id} - {self.kullanici.username} - {self.toplam_tutar} TL"


class SiparisKalemi(models.Model):
    """Sipariş kalemi modeli - siparişin içeriğini temsil eder"""
    
    siparis = models.ForeignKey(
        Siparis,
        related_name='kalemler',
        on_delete=models.CASCADE,
        verbose_name="Sipariş"
    )
    urun = models.ForeignKey(
        Urun,
        on_delete=models.PROTECT,  # Ürün silinmesin, veri bütünlüğü korunsun
        verbose_name="Ürün"
    )
    adet = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Adet",
        help_text="Sipariş edilen ürün adedi"
    )
    birim_fiyat = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Birim Fiyat",
        help_text="Sipariş anındaki ürün fiyatı (TL)"
    )
    
    @property
    def toplam_fiyat(self):
        """Bu kalemin toplam fiyatını hesaplar"""
        return self.miktar * self.birim_fiyat
    
    class Meta:
        verbose_name = "Sipariş Kalemi"
        verbose_name_plural = "Sipariş Kalemleri"
    
    def __str__(self):
        return f"{self.urun.urun_adi} x{self.miktar} - {self.toplam_fiyat} TL"


class Yorum(models.Model):
    """Yorum modeli - ürün değerlendirmelerini temsil eder"""
    
    PUAN_SECENEKLERI = [
        (1, '1 - Çok Kötü'),
        (2, '2 - Kötü'),
        (3, '3 - Orta'),
        (4, '4 - İyi'),
        (5, '5 - Mükemmel'),
    ]
    
    urun = models.ForeignKey(
        Urun,
        related_name='yorumlar',
        on_delete=models.CASCADE,
        verbose_name="Ürün"
    )
    kullanici = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı"
    )
    puan = models.PositiveIntegerField(
        choices=PUAN_SECENEKLERI,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Puan",
        help_text="1-5 arası puan veriniz"
    )
    yorum_metni = models.TextField(
        verbose_name="Yorum",
        help_text="Ürün hakkındaki görüşlerinizi paylaşın"
    )
    tarih = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yorum Tarihi"
    )
    
    class Meta:
        verbose_name = "Yorum"
        verbose_name_plural = "Yorumlar"
        ordering = ['-tarih']
        # Bir kullanıcı aynı ürüne sadece bir kez yorum yapabilir
        unique_together = ('urun', 'kullanici')
    
    def __str__(self):
        return f"{self.kullanici.username} - {self.urun.urun_adi} - {self.puan} yıldız"