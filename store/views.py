from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Review
from .forms import RegistrationForm, LoginForm, ReviewForm, OrderForm, ProductForm
from django.core.paginator import Paginator

def home(request):
    featured_products = Product.objects.filter(available=True)[:8]
    categories = Category.objects.all()
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    reviews = product.reviews.all()
    review_form = None
    
    if request.user.is_authenticated:
        if request.method == 'POST':
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Your review has been added!')
                return redirect('store:product_detail', slug=product.slug)
        else:
            review_form = ReviewForm()
    
    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'store/product_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('store:product_list')  # Added store: namespace
    else:
        form = RegistrationForm()
    return render(request, 'store/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('store:product_list')  # Added store: namespace
    else:
        form = LoginForm()
    return render(request, 'store/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('store:product_list')  # Added store: namespace

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock < 1:
        messages.error(request, 'This product is out of stock!')
        return redirect('store:product_detail', slug=product.slug)  # Added store: namespace
    
    cart, created = Cart.objects.get_or_create(user=request.user, active=True)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        if cart_item.quantity + 1 <= product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Added another {product.name} to your cart!')
        else:
            messages.error(request, f'Cannot add more {product.name} than available stock!')
    else:
        messages.success(request, f'Added {product.name} to your cart!')
    
    return redirect('store:cart_detail')  # Added store: namespace

@login_required
def cart_detail(request):
    try:
        cart = Cart.objects.get(user=request.user, active=True)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0 and quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
        else:
            messages.error(request, 'Invalid quantity!')
    
    return redirect('store:cart_detail')  # Added store: namespace

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Removed {product_name} from your cart!')
    return redirect('store:cart_detail')  # Added store: namespace

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user, active=True)
        cart_items = cart.items.all()
        
        if not cart_items:
            messages.error(request, 'Your cart is empty!')
            return redirect('store:product_list')  # Added store: namespace
        
        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                order.user = request.user
                order.total_cost = cart.get_total_price()
                order.save()
                
                # Create order items and reduce stock
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=item.product.price,
                        quantity=item.quantity
                    )
                    # Reduce stock
                    product = item.product
                    product.stock -= item.quantity
                    product.save()
                
                # Clear cart
                cart.active = False
                cart.save()
                
                messages.success(request, 'Order placed successfully!')
                return redirect('store:order_confirmation', order_id=order.id)  # Added store: namespace
        else:
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}",
                'email': request.user.email,
            }
            form = OrderForm(initial=initial_data)
        
        context = {
            'form': form,
            'cart': cart,
            'cart_items': cart_items,
        }
        return render(request, 'store/checkout.html', context)
        
    except Cart.DoesNotExist:
        messages.error(request, 'No active cart found!')
        return redirect('store:product_list')  # Added store: namespace

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/my_orders.html', {'orders': orders})

@staff_member_required
def admin_dashboard(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lt=10)
    recent_orders = Order.objects.all()[:10]
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'store/admin_dashboard.html', context)

@staff_member_required
def admin_products(request):
    products = Product.objects.all()
    
    if request.method == 'POST':
        if 'add_product' in request.POST:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product added successfully!')
                return redirect('store:admin_products')  # Added store: namespace
    
    form = ProductForm()
    context = {
        'products': products,
        'form': form,
    }
    return render(request, 'store/admin_products.html', context)

@staff_member_required
def admin_orders(request):
    orders = Order.objects.all()
    status_filter = request.GET.get('status', 'all')
    
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'store/admin_orders.html', context)

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {new_status}!')
    
    return redirect('store:admin_orders')  # Added store: namespace

@staff_member_required
def update_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        new_stock = int(request.POST.get('stock', 0))
        if new_stock >= 0:
            product.stock = new_stock
            product.save()
            messages.success(request, f'Stock for {product.name} updated to {new_stock}!')
    
    return redirect('store:admin_products')  # Added store: namespace