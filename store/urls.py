from django.shortcuts import render
from django.contrib import admin 
from django.urls import path 
from .views import Index, store
from .views import Signup
from .views import Login, logout
from .views import CheckOut
from .views import OrderView
from store.middlewares.auth_middleware import auth_middleware
from .views import ArtistGallery
from .views import CartView
from .views import UploadArtwork
from django.utils.decorators import method_decorator
from .views import ArtistDashboard

urlpatterns = [ 
	path('', Index.as_view(), name='homepage'), 
	path('store', store.as_view(), name='store'), 
	path('signup', Signup.as_view(), name='signup'), 
	path('login', Login.as_view(), name='login'), 
	path('logout', logout, name='logout'), 
	path('cart/', CartView.as_view(), name='cart'), 
	path('checkout/', CheckOut.as_view(), name='checkout'),
	path('order/<int:order_id>/', OrderView.as_view(), name='order_detail'),
	path('orders/', OrderView.as_view(), name='orders'),
	path('order/place/', OrderView.as_view(), name='place_order'),
	path('artist/dashboard/', ArtistDashboard.as_view(), name='artist_dashboard'),
	path('artist/upload/', UploadArtwork.as_view(), name='upload_artwork'),
	path('artist/<int:artist_id>/', ArtistGallery.as_view(), name='artist_gallery'),
	path('artists/', ArtistGallery.as_view(), name='artists_list'),
] 

