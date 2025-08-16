from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Yorum


class KullaniciKayitFormu(UserCreationForm):
    """Kullanıcı kayıt formu - Türkçe hata mesajları ile"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'E-posta adresiniz'
        }),
        error_messages={
            'required': 'E-posta adresi zorunludur.',
            'invalid': 'Geçerli bir e-posta adresi giriniz.'
        }
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adınız'
        }),
        error_messages={
            'required': 'Ad alanı zorunludur.',
            'max_length': 'Ad en fazla 30 karakter olabilir.'
        }
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Soyadınız'
        }),
        error_messages={
            'required': 'Soyad alanı zorunludur.',
            'max_length': 'Soyad en fazla 30 karakter olabilir.'
        }
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Widget'ları özelleştir
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Kullanıcı adınız'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Şifreniz'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Şifrenizi tekrar giriniz'
        })
        
        # Hata mesajlarını Türkçeleştir
        self.fields['username'].error_messages = {
            'required': 'Kullanıcı adı zorunludur.',
            'unique': 'Bu kullanıcı adı zaten kullanılıyor.',
            'invalid': 'Kullanıcı adı sadece harf, rakam ve @/./+/-/_ karakterlerini içerebilir.'
        }
        
        self.fields['password1'].error_messages = {
            'required': 'Şifre zorunludur.'
        }
        
        self.fields['password2'].error_messages = {
            'required': 'Şifre tekrarı zorunludur.'
        }
        
        # Yardım metinlerini Türkçeleştir
        self.fields['username'].help_text = 'Zorunlu. 150 karakter veya daha az. Sadece harf, rakam ve @/./+/-/_ karakterleri.'
        self.fields['password1'].help_text = '''
        <ul>
            <li>Şifreniz kişisel bilgilerinize çok benzer olmamalı.</li>
            <li>Şifreniz en az 8 karakter içermelidir.</li>
            <li>Şifreniz yaygın kullanılan şifrelerden olmamalı.</li>
            <li>Şifreniz tamamen sayısal olmamalı.</li>
        </ul>
        '''
    
    def clean_email(self):
        """E-posta benzersizlik kontrolü"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Bu e-posta adresi zaten kullanılıyor.')
        return email
    
    def clean_password2(self):
        """Şifre eşleşme kontrolü"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Şifreler eşleşmiyor.')
        
        return password2
    
    def save(self, commit=True):
        """Kullanıcıyı kaydet"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user


class KullaniciGirisFormu(AuthenticationForm):
    """Kullanıcı giriş formu - Türkçe hata mesajları ile"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Widget'ları özelleştir
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Kullanıcı adınız'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Şifreniz'
        })
        
        # Hata mesajlarını Türkçeleştir
        self.fields['username'].error_messages = {
            'required': 'Kullanıcı adı zorunludur.'
        }
        self.fields['password'].error_messages = {
            'required': 'Şifre zorunludur.'
        }
    
    def confirm_login_allowed(self, user):
        """Giriş izni kontrolü"""
        if not user.is_active:
            raise ValidationError(
                'Bu hesap devre dışı bırakılmış.',
                code='inactive',
            )
    
    error_messages = {
        'invalid_login': 'Kullanıcı adı veya şifre hatalı.',
        'inactive': 'Bu hesap devre dışı bırakılmış.',
    }


class YorumFormu(forms.ModelForm):
    """Ürün yorumu formu"""
    
    class Meta:
        model = Yorum
        fields = ('puan', 'yorum_metni')
        widgets = {
            'puan': forms.Select(
                choices=Yorum.PUAN_SECENEKLERI,
                attrs={
                    'class': 'form-select',
                }
            ),
            'yorum_metni': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ürün hakkındaki görüşlerinizi paylaşın...'
            })
        }
        error_messages = {
            'puan': {
                'required': 'Puan vermeniz zorunludur.',
                'invalid_choice': 'Geçerli bir puan seçiniz.'
            },
            'yorum_metni': {
                'required': 'Yorum metni zorunludur.',
                'max_length': 'Yorum metni çok uzun.'
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Alan etiketlerini Türkçeleştir
        self.fields['puan'].label = 'Puanınız'
        self.fields['yorum_metni'].label = 'Yorumunuz'
        
        # Yardım metinleri
        self.fields['puan'].help_text = '1 (Çok Kötü) - 5 (Mükemmel) arası puan veriniz.'
        self.fields['yorum_metni'].help_text = 'Ürün hakkındaki deneyiminizi ve görüşlerinizi paylaşın.'
    
    def clean_yorum_metni(self):
        """Yorum metni validasyonu"""
        yorum_metni = self.cleaned_data.get('yorum_metni')
        
        if yorum_metni:
            # Minimum uzunluk kontrolü
            if len(yorum_metni.strip()) < 10:
                raise ValidationError('Yorum en az 10 karakter olmalıdır.')
            
            # Maksimum uzunluk kontrolü
            if len(yorum_metni) > 1000:
                raise ValidationError('Yorum en fazla 1000 karakter olabilir.')
        
        return yorum_metni


class UrunAramaFormu(forms.Form):
    """Ürün arama ve filtreleme formu"""
    
    arama = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ürün ara...'
        })
    )
    
    kategori = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    min_fiyat = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min fiyat',
            'min': '0',
            'step': '0.01'
        })
    )
    
    max_fiyat = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max fiyat',
            'min': '0',
            'step': '0.01'
        })
    )
    
    siralama = forms.ChoiceField(
        choices=[
            ('', 'Sıralama'),
            ('-olusturulma_tarihi', 'En Yeni'),
            ('olusturulma_tarihi', 'En Eski'),
            ('fiyat', 'Fiyat (Düşük → Yüksek)'),
            ('-fiyat', 'Fiyat (Yüksek → Düşük)'),
            ('urun_adi', 'İsim (A → Z)'),
            ('-urun_adi', 'İsim (Z → A)'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    def __init__(self, *args, **kwargs):
        kategoriler = kwargs.pop('kategoriler', [])
        super().__init__(*args, **kwargs)
        
        # Kategori seçeneklerini dinamik olarak ayarla
        kategori_secenekleri = [('', 'Tüm Kategoriler')]
        kategori_secenekleri.extend([(kat, kat) for kat in kategoriler])
        self.fields['kategori'].widget.choices = kategori_secenekleri