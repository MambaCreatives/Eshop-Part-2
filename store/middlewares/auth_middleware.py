from django.shortcuts import redirect
from django.urls import reverse

def auth_middleware(get_response):
    def middleware(request, *args, **kwargs):
        if not request.session.get('customer'):
            return_url = request.META['PATH_INFO']
            return redirect(f'/login?return_url={return_url}')
        
        return get_response(request, *args, **kwargs)

    return middleware

# Add a class-based middleware version
class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        if not request.session.get('customer'):
            return_url = request.META['PATH_INFO']
            return redirect(f'/login?return_url={return_url}')
            
        return self.get_response(request, *args, **kwargs)
