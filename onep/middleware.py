"""
ONEP E-Ticaret Middleware
Sepet işlemleri için cache bypass middleware'i
"""

class CartNoCacheMiddleware:
    """Sepet ile ilgili URL'ler için cache'i devre dışı bırak"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        """Sepet ile ilgili URL'ler için cache'i devre dışı bırak"""
        response = self.get_response(request)
        
        # Sepet URL'leri için cache kontrolü
        if '/cart/' in request.path:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['Vary'] = 'Cookie'  # Session cookie'ye göre değişiklik göster
            
        return response
