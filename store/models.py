from django.db import models 
import datetime 
from django.contrib.auth.models import User

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # ✅ Ensure User relation exists
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
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
        except:
            return None
    
    def isExists(self):
        if Customer.objects.filter(email=self.email):
            return True
        return False

class Artwork(models.Model):
    ARTWORK_CATEGORIES = (
        ('pencil', 'Pencil Drawing'),
        ('painting', 'Painting'),
        ('thread', 'Thread Art'),
        
    )
    
    name = models.CharField(max_length=100)
    artist = models.ForeignKey(Customer, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='artworks/')
    category = models.CharField(max_length=20, choices=ARTWORK_CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)
    
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
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)  # Make sure this field exists
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    @classmethod
    def get_orders_by_customer(cls, customer):
        return cls.objects.filter(customer=customer).order_by('-date')

    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]

class Cart(models.Model):
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
    address = models.CharField(blank=True, default='', max_length=50)
    phone = models.CharField(blank=True, default='', max_length=50)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)

    def placeOrder(self):
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('-date')


