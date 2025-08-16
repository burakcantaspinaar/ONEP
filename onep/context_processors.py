def cart_context(request):
    """Sepet bilgilerini tüm template'lerde kullanılabilir hale getirir"""
    sepet = request.session.get('sepet', {})
    cart_count = sum(sepet.values()) if sepet else 0
    
    return {
        'cart_count': cart_count,
        'cart_items': sepet
    }
