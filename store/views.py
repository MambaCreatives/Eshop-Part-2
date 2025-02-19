from django.db import models

from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import View
from django.contrib.auth.hashers import check_password,make_password
import datetime
from django.contrib import messages
from django.utils.decorators import method_decorator
#from .utils import predict_category
from django.contrib.auth.models import User
# Importing models

from .models import Category
from .models import Customer
from .models import Order
from .models import Artwork

# Importing middleware
from store.middlewares.auth_middleware import auth_middleware


from .models import Category,Customer,Artwork,Order,Cart

class Index(View): 
    def get(self, request): 
        cart = request.session.get('cart', {})
        artworks = Artwork.objects.all().order_by('-created_at')
        categories = dict(Artwork.ARTWORK_CATEGORIES).keys()
        
        # Filter by category if specified
        category = request.GET.get('category')
        if category:
            artworks = artworks.filter(category=category)
            
        return render(request, 'index.html', {
            'artworks': artworks,
            'categories': categories,
            'cart': cart
        })

class Login(View): 
    def get(self, request): 
        if request.session.get('customer'):
            return redirect('homepage')
        return render(request, 'login.html') 
  
    def post(self, request): 
        email = request.POST.get('email') 
        password = request.POST.get('password') 
        customer = Customer.get_customer_by_email(email) 
        error_message = None
        
        if customer: 
            flag = check_password(password, customer.password) 
            if flag: 
                request.session['customer'] = customer.id
                request.session['user_type'] = customer.user_type
                
                # Handle return URL
                return_url = request.GET.get('return_url')
                if return_url:
                    return redirect(return_url)
                    return redirect('homepage') 
            else: 
                error_message = 'Invalid password'
        else: 
            error_message = 'User not found'
  
        return render(request, 'login.html', {'error': error_message}) 
  
  
def logout(request): 
    request.session.clear() 
    return redirect('login') 

class Signup(View):
    def get(self, request): 
        return render(request, 'signup.html') 
  
    def post(self, request): 
        postData = request.POST 
        first_name = postData.get('firstname') 
        last_name = postData.get('lastname') 
        phone = postData.get('phone') 
        email = postData.get('email') 
        password = postData.get('password') 
        user_type = postData.get('user_type', 'customer')
        
        # Additional artist fields
        bio = postData.get('bio') if user_type == 'artist' else None
        artist_statement = postData.get('artist_statement') if user_type == 'artist' else None
        profile_image = request.FILES.get('profile_image') if user_type == 'artist' else None
        
        value = { 
            'first_name': first_name, 
            'last_name': last_name, 
            'phone': phone, 
            'email': email,
            'user_type': user_type,
            'bio': bio,
            'artist_statement': artist_statement
        } 
  
        customer = Customer(
            first_name=first_name,
                            last_name=last_name, 
                            phone=phone, 
                            email=email, 
            password=password,
            user_type=user_type,
            bio=bio,
            artist_statement=artist_statement,
            profile_image=profile_image
        )
        
        error_message = self.validateCustomer(customer) 
  
        if not error_message: 
            customer.password = make_password(password) 
            customer.register() 
            return redirect('homepage') 
        else: 
            data = { 
                'error': error_message, 
                'values': value 
            } 
            return render(request, 'signup.html', data) 
  
    def validateCustomer(self, customer): 
        error_message = None
        if (not customer.first_name): 
            error_message = "Please Enter your First Name !!"
        elif len(customer.first_name) < 3: 
            error_message = 'First Name must be 3 char long or more'
        elif not customer.last_name: 
            error_message = 'Please Enter your Last Name'
        elif len(customer.last_name) < 3: 
            error_message = 'Last Name must be 3 char long or more'
        elif not customer.phone: 
            error_message = 'Enter your Phone Number'
        elif len(customer.phone) < 10: 
            error_message = 'Phone Number must be 10 char Long'
        elif len(customer.password) < 5: 
            error_message = 'Password must be 5 char long'
        elif len(customer.email) < 5: 
            error_message = 'Email must be 5 char long'
        elif customer.isExists(): 
            error_message = 'Email Address Already Registered..'
        # saving 
  
        return error_message 

        
    


class CheckOut(View):
    @method_decorator(auth_middleware)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Ensure the cart is not empty before checkout"""
        customer_id = request.session.get('customer')
        if not customer_id:
           return redirect('login')

    # ✅ Fetch cart items from the database
        cart_items = Cart.objects.filter(customer_id=customer_id, status=False)
        subtotal = sum(item.artwork.price * item.quantity for item in cart_items)
        shipping = 200  # Fixed shipping cost
        total = subtotal + shipping

         # ✅ Debugging: Print cart items before rendering
        print("DEBUG: Cart items being sent to checkout page:", cart_items)

        if not cart_items.exists():
           messages.warning(request, 'Your cart is empty')
           return redirect('cart')

        return render(request, 'checkout.html', {
           'cart_items': cart_items,
           'subtotal': subtotal,
           'shipping': shipping,
           'total': total
    })


    def post(self, request):
        """Process checkout and create orders from the cart"""
        customer_id = request.session.get('customer')
        if not customer_id:
            return redirect('login')

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            messages.error(request, 'Customer not found')
            return redirect('checkout')

        cart_items = Cart.objects.filter(customer=customer, status=False)  # Fetch cart items

        if not cart_items.exists():
            messages.error(request, 'Your cart is empty')
            return redirect('cart')

        address = request.POST.get('address')
        phone = request.POST.get('phone')

        if not address or not phone:
            messages.error(request, 'Address and phone are required')
            return redirect('checkout')

        orders_created = []

        for cart_item in cart_items:
            try:
                artwork = Artwork.objects.get(id=cart_item.artwork.id)
                order = Order.objects.create(
                    customer=customer,
                    artwork=artwork,
                    price=artwork.price,
                    quantity=cart_item.quantity,
                    address=address,
                    phone=phone,
                    status='pending'  # Default status
                )
                orders_created.append(order)
                print(f"✅ SUCCESS: Order created -> Order ID: {order.id}")
            except Artwork.DoesNotExist:
                messages.error(request, f'Artwork with ID {cart_item.artwork.id} not found')
                return redirect('checkout')
            
        # ✅ Clear cart after order placement
        cart_items.delete()

        messages.success(request, 'Orders placed successfully!')

        # ✅ Redirect to order details if only one order
        if len(orders_created) == 1:
            return redirect('order_detail', order_id=orders_created[0].id)
        else:
                messages.error(request, 'Error placing orders')
            
        return redirect('orders')



class OrderView(View): 
    @method_decorator(auth_middleware)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
  
    def get(self, request, order_id=None):
        customer = request.session.get('customer') 
        if not customer:
            return redirect('login')
        
        # If order_id is provided, show single order detail
        if order_id:
            try:
                order = Order.objects.get(id=order_id, customer=customer)
                return render(request, 'order_detail.html', {'order': order})
            except Order.DoesNotExist:
                messages.error(request, 'Order not found')
                return redirect('orders')
        
        # Show all orders
        orders = Order.get_orders_by_customer(customer) 
        return render(request, 'orders.html', {'orders': orders}) 

    def post(self, request):
        if not request.session.get('customer'):
            return redirect('login')
            
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, 'Your cart is empty')
            return redirect('cart')
            
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        if not address or not phone:
            messages.error(request, 'Address and phone are required')
            return redirect('checkout')
            
        customer = Customer.objects.get(id=request.session.get('customer'))
        orders_created = []
        
        for artwork_id, quantity in cart.items():
            try:
                artwork = Artwork.objects.get(id=artwork_id)
                order = Order(
                    customer=customer,
                    artwork=artwork,
                    price=artwork.price,
                    quantity=quantity,
                    address=address,
                    phone=phone
                )
                order.place_order()
                orders_created.append(order)
            except Artwork.DoesNotExist:
                continue
        
        if orders_created:
            # Clear the cart after successful order placement
            request.session['cart'] = {}
            messages.success(request, 'Orders placed successfully!')
            
            # If single order, redirect to its detail page
            if len(orders_created) == 1:
                return redirect('order_detail', order_id=orders_created[0].id)
        else:
            messages.error(request, 'Error placing orders')
            
        return redirect('orders')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            customer = Customer.objects.get(email=email)
            if customer.password == password:  # Note: In production, use proper password hashing
                request.session['customer'] = customer.id
                messages.success(request, 'Successfully logged in!')
                return redirect('homepage')
            else:
                messages.error(request, 'Invalid password')
        except Customer.DoesNotExist:
            messages.error(request, 'No account found with this email')
        
        return render(request, 'login.html', {'values': {'email': email}})
    
    return render(request, 'login.html') 
  
class ArtistDashboard(View):
    @method_decorator(auth_middleware)
    def dispatch(self, request, *args, **kwargs):
        if request.session.get('user_type') != 'artist':
            messages.error(request, 'Only artists can access the dashboard')
            return redirect('homepage')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        artist_id = request.session.get('customer')
        artist = Customer.objects.get(id=artist_id)
        artworks = Artwork.objects.filter(artist=artist).order_by('-created_at')
        
        return render(request, 'artist_dashboard.html', {
            'artist': artist,
            'artworks': artworks
        })

class UploadArtwork(View):
    @method_decorator(auth_middleware)
    def dispatch(self, request, *args, **kwargs):
        if request.session.get('user_type') != 'artist':
            messages.error(request, 'Only artists can upload artwork')
            return redirect('homepage')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, 'upload_artwork.html')
    
    def post(self, request):
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        category = request.POST.get('category')
        
        if not all([name, description, price, image, category]):
            messages.error(request, 'All fields are required')
            return render(request, 'upload_artwork.html')
            
        try:
            artist_id = request.session.get('customer')
            
            artwork = Artwork(
                name=name,
                artist=Customer.objects.get(id=artist_id),
                description=description,
                price=float(price),
                image=image,
                category=category
            )
            artwork.save()
            messages.success(request, 'Artwork uploaded successfully!')
            return redirect('artist_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error uploading artwork: {str(e)}')
            return render(request, 'upload_artwork.html')
  
class ArtistGallery(View):
    def get(self, request, artist_id=None):
        if artist_id:
            # Show specific artist's gallery
            try:
                artist = Customer.objects.get(id=artist_id, user_type='artist')
                artworks = Artwork.objects.filter(artist=artist).order_by('-created_at')
                return render(request, 'artist_gallery.html', {
                    'artist': artist,
                    'artworks': artworks
                })
            except Customer.DoesNotExist:
                messages.error(request, 'Artist not found')
                return redirect('homepage')
        else:
            # Show all artists
            artists = Customer.objects.filter(user_type='artist')
            return render(request, 'artists.html', {'artists': artists})
  
class CartView(View):
    def get(self, request):
        """Retrieve the cart for the logged-in customer and display items"""
        if not request.session.get('customer'):
            messages.warning(request, 'Please login to view your cart')
            return redirect('login')

        customer_id = request.session.get('customer')
        cart_items = Cart.objects.filter(customer_id=customer_id, status=False)  # Get unprocessed cart items
        subtotal = sum(item.artwork.price * item.quantity for item in cart_items)
        shipping = 200  # Fixed shipping cost
        total = subtotal + shipping

        return render(request, 'cart.html', {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'total': total
        })

    def post(self, request):
        """Handle adding, updating, or removing items in the cart"""
        if not request.session.get('customer'):
            messages.warning(request, 'Please login to add items to cart')
            return redirect('login')

        action = request.POST.get('action')
        artwork_id = request.POST.get('artwork_id')

        if not artwork_id or not artwork_id.isdigit():
            messages.error(request, 'Invalid artwork ID')
            return redirect('cart')

        customer_id = request.session.get('customer')

        try:
            artwork = Artwork.objects.get(id=artwork_id)
            cart_item, created = Cart.objects.get_or_create(
                customer_id=customer_id,
                artwork=artwork,
                status=False,  # Only modify active cart items
                defaults={'quantity': 1, 'price': artwork.price, 'date': datetime.datetime.today()}
            )

            if action == 'increase':
                cart_item.quantity += 1
                messages.success(request, 'Artwork quantity increased')

            elif action == 'decrease':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    messages.success(request, 'Artwork quantity decreased')
                else:
                    cart_item.delete()
                    messages.success(request, 'Artwork removed from cart')
                    return redirect('cart')

            elif action == 'remove':
                cart_item.delete()
                messages.success(request, 'Artwork removed from cart')
                return redirect('cart')

            cart_item.save()
        except Artwork.DoesNotExist:
            messages.error(request, 'Artwork not found')

        return redirect('cart')

class store(View):
            def get(self, request):
                cart = request.session.get('cart', {})  
                artworks = Artwork.objects.all().order_by('-created_at')
                categories = dict(Artwork.ARTWORK_CATEGORIES).keys()
        
                # Filter by category if specified
                category = request.GET.get('category')
                if category:
                    artworks = artworks.filter(category=category)
            
                return render(request, 'store.html', {
                    'artworks': artworks,
                    'categories': categories,
                    'cart': cart
                })




  