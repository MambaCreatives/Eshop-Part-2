from django.urls import path
from .views import (
    Index, store, Signup, Login_view, logout, CheckOut, OrderView, 
    ArtistGallery, CartView, UploadArtwork, ArtistDashboard
)
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import ArtworkDetailView
from .views import Login_view


urlpatterns = [ 
    path('', Index.as_view(), name='homepage'), 
    path('store/', store.as_view(), name='store'), 
    path('signup/', Signup.as_view(), name='signup'), 
    path('login/', Login_view.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', CartView.as_view(), name='cart'), 
    path('checkout/', CheckOut.as_view(), name='checkout'),
    path('faq/', views.faq, name='faq'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('contact/', views.contact, name='contact'),
     
    
    # Order paths
    path('order/<int:order_id>/', OrderView.as_view(), name='order_detail'),
    path('orders/', OrderView.as_view(), name='orders'),
    path('order/place/', OrderView.as_view(), name='place_order'),

    # Artist paths
    path('artist/dashboard/', ArtistDashboard.as_view(), name='artist_dashboard'),
    path('upload/<int:pk>/', UploadArtwork.as_view(), name='upload_artwork'),
    path('artist/<int:artist_id>/', ArtistGallery.as_view(), name='artist_gallery'),
    path('artists/', ArtistGallery.as_view(), name='artists_list'),
    
    # Prediction path
    path('upload/', UploadArtwork.as_view(), name='upload_artwork'),
    path('artwork/<int:pk>/', ArtworkDetailView.as_view(), name='artwork_detail'),  # ✅ ADD THIS
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
