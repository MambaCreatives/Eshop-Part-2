from django.db import models
import datetime
from django.contrib.auth.models import User
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=50)

    @staticmethod
    def get_all_categories():
        return Category.objects.all()

    def __str__(self):
        return self.name

class Customer(models.Model):
    USER_TYPES = (
        ('customer', 'Art Buyer'),
        ('artist', 'Artist'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    # Use Django's User model for password handling instead of storing plain text
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customer')
    
    # For artists
    bio = models.TextField(blank=True, null=True)
    artist_statement = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='artist_profiles/', blank=True, null=True)
    
    def register(self):
        self.save()
    
    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return None
    
    def is_exists(self):
        return Customer.objects.filter(email=self.email).exists()

class Artwork(models.Model):
    ARTWORK_CATEGORIES = (
        ('pencil', 'Pencil Drawing'),
        ('painting', 'Painting'),
        ('thread', 'Thread Art'),
    )
    
    name = models.CharField(max_length=100)
    artist = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='artworks')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='artworks/')
    category = models.CharField(max_length=20, choices=ARTWORK_CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)  # For SEO-friendly URLs

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @staticmethod
    def get_artworks_by_id(ids):
        return Artwork.objects.filter(id__in=ids)

    @staticmethod
    def get_all_artworks():
        return Artwork.objects.all()

    @staticmethod
    def get_artworks_by_category(category):
        if category:
            return Artwork.objects.filter(category=category)
        return Artwork.get_all_artworks()

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id} - {self.customer.user.username if self.customer and self.customer.user else 'Unknown'}"

    @classmethod
    def get_orders_by_customer(cls, customer):
        return cls.objects.filter(customer=customer).order_by('-date')

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Unknown')

class Cart(models.Model):
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Match Artwork and Order
    address = models.CharField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    date = models.DateTimeField(default=datetime.datetime.now)  # Use DateTimeField for consistency
    status = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)

    def place_order(self):
        self.save()

    @staticmethod
    def get_cart_items_by_customer(customer):
        return Cart.objects.filter(customer=customer, status=False).select_related('artwork')