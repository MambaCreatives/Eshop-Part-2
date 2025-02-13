from django.contrib import admin

from .models import Category,Customer,Order,Cart,Artwork

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Artwork)
admin.site.register(Order)
admin.site.register(Cart)

