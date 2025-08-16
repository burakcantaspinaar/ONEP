from django.contrib import admin
from .models import Urun, Siparis, SiparisKalemi, Yorum


class SiparisKalemiInline(admin.TabularInline):
    """Sipariş kalemleri için inline admin"""
    model = SiparisKalemi
    extra = 0
    readonly_fields = ('toplam_fiyat',)
    
    def toplam_fiyat(self, obj):
        if obj.adet and obj.birim_fiyat:
            return f"{obj.adet * obj.birim_fiyat} TL"
        return "-"
    toplam_fiyat.short_description = 'Toplam Fiyat'


@admin.register(Urun)
class UrunAdmin(admin.ModelAdmin):
    """Ürün modeli admin yapılandırması"""
    list_display = ('urun_adi', 'kategori', 'fiyat', 'stok_adedi', 'is_stokta', 'olusturulma_tarihi')
    list_filter = ('kategori', 'olusturulma_tarihi', 'guncellenme_tarihi')
    search_fields = ('urun_adi', 'aciklama', 'kategori')
    ordering = ('-olusturulma_tarihi',)
    readonly_fields = ('olusturulma_tarihi', 'guncellenme_tarihi')
    list_per_page = 25
    
    fieldsets = (
        ('Ürün Bilgileri', {
            'fields': ('urun_adi', 'aciklama', 'kategori')
        }),
        ('Fiyat ve Stok', {
            'fields': ('fiyat', 'stok_adedi')
        }),
        ('Resim', {
            'fields': ('resim_url',)
        }),
        ('Tarihler', {
            'fields': ('olusturulma_tarihi', 'guncellenme_tarihi'),
            'classes': ('collapse',)
        }),
    )
    
    def is_stokta(self, obj):
        return obj.is_stokta
    is_stokta.boolean = True
    is_stokta.short_description = 'Stokta'


@admin.register(Siparis)
class SiparisAdmin(admin.ModelAdmin):
    """Sipariş modeli admin yapılandırması"""
    list_display = ('id', 'kullanici', 'siparis_tarihi', 'toplam_tutar', 'durum')
    list_filter = ('durum', 'siparis_tarihi')
    search_fields = ('kullanici__username', 'kullanici__email', 'id')
    ordering = ('-siparis_tarihi',)
    readonly_fields = ('siparis_tarihi',)
    inlines = [SiparisKalemiInline]
    list_per_page = 25
    
    fieldsets = (
        ('Sipariş Bilgileri', {
            'fields': ('kullanici', 'siparis_tarihi', 'durum')
        }),
        ('Ödeme Bilgileri', {
            'fields': ('toplam_tutar',)
        }),
    )
    
    def get_queryset(self, request):
        """Sipariş sorgusu optimizasyonu"""
        qs = super().get_queryset(request)
        return qs.select_related('kullanici').prefetch_related('kalemler__urun')


@admin.register(SiparisKalemi)
class SiparisKalemiAdmin(admin.ModelAdmin):
    """Sipariş kalemi modeli admin yapılandırması"""
    list_display = ('siparis_id', 'urun', 'adet', 'birim_fiyat', 'toplam_fiyat_display')
    list_filter = ('siparis__durum', 'siparis__siparis_tarihi')
    search_fields = ('urun__urun_adi', 'siparis__kullanici__username')
    ordering = ('-siparis__siparis_tarihi',)
    list_per_page = 25
    
    def toplam_fiyat_display(self, obj):
        return f"{obj.toplam_fiyat} TL"
    toplam_fiyat_display.short_description = 'Toplam Fiyat'
    
    def siparis_id(self, obj):
        return f"Sipariş #{obj.siparis.id}"
    siparis_id.short_description = 'Sipariş'
    
    def get_queryset(self, request):
        """Sipariş kalemi sorgusu optimizasyonu"""
        qs = super().get_queryset(request)
        return qs.select_related('siparis__kullanici', 'urun')


@admin.register(Yorum)
class YorumAdmin(admin.ModelAdmin):
    """Yorum modeli admin yapılandırması"""
    list_display = ('kullanici', 'urun', 'puan', 'tarih', 'yorum_ozeti')
    list_filter = ('puan', 'tarih', 'urun__kategori')
    search_fields = ('kullanici__username', 'urun__urun_adi', 'yorum_metni')
    ordering = ('-tarih',)
    readonly_fields = ('tarih',)
    list_per_page = 25
    
    fieldsets = (
        ('Yorum Bilgileri', {
            'fields': ('kullanici', 'urun', 'puan')
        }),
        ('İçerik', {
            'fields': ('yorum_metni',)
        }),
        ('Tarih', {
            'fields': ('tarih',),
            'classes': ('collapse',)
        }),
    )
    
    def yorum_ozeti(self, obj):
        """Yorum metninin ilk 50 karakterini gösterir"""
        if len(obj.yorum_metni) > 50:
            return f"{obj.yorum_metni[:50]}..."
        return obj.yorum_metni
    yorum_ozeti.short_description = 'Yorum Özeti'
    
    def get_queryset(self, request):
        """Yorum sorgusu optimizasyonu"""
        qs = super().get_queryset(request)
        return qs.select_related('kullanici', 'urun')


# Admin site başlık ve açıklama ayarları
admin.site.site_header = 'ONEP Admin Paneli'
admin.site.site_title = 'ONEP Yönetimi'
admin.site.index_title = 'ONEP E-Ticaret Platformu Yönetimi'
