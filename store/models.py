from django.db import models
import datetime
from django.contrib.auth.models import User
from django.utils.text import slugify
import os
import joblib
from django.conf import settings
from .utility import extract_features 
from django.contrib.auth.hashers import make_password
import cv2
import numpy as np
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from django.dispatch import receiver
from django.db.models.signals import post_save



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
        """Ensure slug is unique before saving"""
        if not self.slug:
           base_slug = slugify(self.name)
           slug = base_slug
           counter = 1
           while Artwork.objects.filter(slug=slug).exists():
               slug = f"{base_slug}-{counter}"
               counter += 1
           self.slug = slug  

        super().save(*args, **kwargs)  # ✅ Save the object to ensure the image is available

    # ✅ Ensure the image file exists before trying to categorize
        if not self.category or self.category == "unknown":
           if self.image and os.path.exists(self.image.path):
               print(f"✅ Image file found: {self.image.path}")  # Debugging statement
               try:
                   predicted_category = self.predict_category()
                   if predicted_category != 'unknown':  
                      self.category = predicted_category
                      print(f"🎨 Predicted Category: {predicted_category}")  # Debugging
                      Artwork.objects.filter(id=self.id).update(category=predicted_category)  # ✅ Force save in DB
                   else:
                    print("❌ Prediction returned 'unknown', category not updated.")
               except Exception as e:
                print(f"❌ Error categorizing artwork: {e}")
        else:
            print("❌ Error: Image file not found after saving!")
    def predict_category(self):
        """Predicts artwork category using ML model with robust image handling"""
        model_path = os.path.join(settings.BASE_DIR, 'store', 'art_classifier_model.joblib')

        if not os.path.exists(model_path):
            print("❌ Model file not found!")
            return 'unknown'

        try:
            model, le = joblib.load(model_path)
            print("✅ Model loaded successfully.")
        except Exception as e:
            print(f"❌ Model loading error: {e}")
            return 'unknown'

        try:
            # Handle unsaved in-memory file (e.g., during form validation)
            if isinstance(self.image, InMemoryUploadedFile):
                image_data = self.image.read()
                image_array = np.asarray(bytearray(image_data), dtype=np.uint8)
                img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            else:
                # Handle saved file
                if not self.image or not os.path.exists(self.image.path):
                    print(f"❌ Image path invalid: {self.image.path if self.image else 'No image'}")
                    return 'unknown'
                img = cv2.imread(self.image.path)

            if img is None:
                print("❌ Failed to load image data")
                return 'unknown'

            # Image Processing
            img = cv2.resize(img, (128, 128))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            hist = cv2.calcHist([img], [0,1,2], None, [8,8,8], [0,256]*3)
            hist = cv2.normalize(hist, hist).flatten()
            features = np.hstack((hist, edges.flatten()))

            prediction = model.predict(features.reshape(1, -1))
            return le.inverse_transform(prediction)[0]

        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return 'unknown'
    
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