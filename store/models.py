from django.db import models
import datetime
from django.contrib.auth.models import User
from django.utils.text import slugify
import os
import joblib
from django.conf import settings
from .utility import extract_features 
from django.contrib.auth.hashers import make_password



class Category(models.Model):
    name = models.CharField(max_length=50)

    @staticmethod
    def get_all_categories():
        return Category.objects.all()

    def __str__(self):
        return self.name



class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    phone = models.CharField(max_length=15, unique=True)
    user_type = models.CharField(max_length=10, choices=[('customer', 'Customer'), ('artist', 'Artist')])

    # Additional fields for artists
    bio = models.TextField(blank=True, null=True)
    artist_statement = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username


  
class Artwork(models.Model):
    ARTWORK_CATEGORIES = (
        ('pencil', 'Pencil Drawing'),
        ('painting', 'Painting'),
        ('thread', 'Thread Art'),
    )

    name = models.CharField(max_length=100)
    artist = models.ForeignKey('store.Customer', on_delete=models.CASCADE, related_name='artworks')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='artworks/')
    category = models.CharField(max_length=20, choices=ARTWORK_CATEGORIES, blank=True)  # Auto-filled
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)  # SEO-friendly URLs

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Artwork.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug  # Assign a unique slug

        super().save(*args, **kwargs)  # Save the object first

        # Ensure the image exists before attempting to categorize
        if not self.category and self.image:
            try:
                image_path = self.image.path  # Get absolute path
                if os.path.exists(image_path):  
                    self.category = self.predict_category()
                    super().save(update_fields=['category'])  # Save only the updated category
            except Exception as e:
                print(f"Error categorizing artwork: {e}")

    def predict_category(self):
        """Predicts the artwork category using a pre-trained ML model."""
        model_path = os.path.join(settings.BASE_DIR, 'store', 'art_classifier_model.joblib')

        if not os.path.exists(model_path):
            return 'unknown'  # Return default if model is missing

        model, le = joblib.load(model_path)

        try:
            features = extract_features(self.image)  # Updated to use correct file handling
            features = features.reshape(1, -1)
            predicted_category = le.inverse_transform(model.predict(features))[0]
            return predicted_category
        except Exception as e:
            print(f"Error predicting category: {e}")
            return 'unknown'

    def __str__(self):
        return self.name
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