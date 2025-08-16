"""
ONEP Uygulama URL Yapılandırması
"""
from django.urls import path
from . import views

urlpatterns = [
    # Ana sayfa ve ürün sayfaları
    path('', views.product_list_view, name='product_list'),
    path('product/<int:id>/', views.product_detail_view, name='product_detail'),
    
    # Kullanıcı yönetimi
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Sepet yönetimi (Session tabanlı)
    path('cart/', views.sepet_goruntule, name='cart'),
    path('cart/add/<int:urun_id>/', views.sepete_ekle, name='sepete_ekle'),
    path('cart/remove/<int:urun_id>/', views.sepetten_sil, name='sepetten_sil'),
    path('cart/update/<int:urun_id>/', views.sepet_guncelle, name='sepet_guncelle'),
    path('cart/clear/', views.sepet_bosalt, name='sepet_bosalt'),
    
    # Sipariş yönetimi
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-confirmation/<int:siparis_id>/', views.order_confirmation_view, name='order_confirmation'),
    path('order-history/', views.order_history_view, name='order_history'),
    
    # Yorum sistemi
    path('review/add/<int:urun_id>/', views.yorum_ekle, name='yorum_ekle'),
]
