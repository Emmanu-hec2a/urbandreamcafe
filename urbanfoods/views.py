from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.paginator import Paginator
from .models import *
import json

# ==================== HOMEPAGE & FOOD CATALOG ====================

def homepage(request):
    """Main food catalog page"""
    # Get store type from session or default to 'food'
    store_type = request.session.get('store_type', 'food')
    
    # Filter categories by store type
    categories = FoodCategory.objects.filter(store_type=store_type)

    # Get filter parameters
    category_id = request.GET.get('category')
    search_query = request.GET.get('q')

    # Base queryset filtered by store type
    food_items = FoodItem.objects.filter(is_available=True, store_type=store_type)

    # Apply filters
    if category_id:
        food_items = food_items.filter(category_id=category_id)
    if search_query:
        food_items = food_items.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Get special items filtered by store type
    meal_of_day = FoodItem.objects.filter(is_meal_of_day=True, is_available=True, store_type=store_type).first()
    featured_items_queryset = FoodItem.objects.filter(is_featured=True, is_available=True, store_type=store_type)[:4]
    featured_items = list(featured_items_queryset) if featured_items_queryset else []
    popular_items = FoodItem.objects.filter(is_available=True, store_type=store_type).order_by('-times_ordered')[:6]

    # Cart count
    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.item_count

    context = {
        'categories': categories,
        'food_items': food_items,
        'meal_of_day': meal_of_day,
        'featured_items': featured_items,
        'popular_items': popular_items,
        'cart_count': cart_count,
        'selected_category': category_id,
        'search_query': search_query,
        'store_type': store_type,
    }
    return render(request, 'homepage.html', context)

@require_http_methods(["POST"])
def switch_store(request):
    """Switch between food and liquor store"""
    data = json.loads(request.body)
    store_type = data.get('store_type', 'food')
    
    if store_type in ['food', 'liquor', 'grocery']:
        # Clear cart if user is authenticated and cart has items of different store type
        if request.user.is_authenticated:
            try:
                cart, _ = Cart.objects.get_or_create(user=request.user)
                if cart.items.exists():
                    # Check if cart has items of different store type
                    cart_items = cart.items.select_related('food_item').all()
                    has_different_store_type = any(
                        item.food_item.store_type != store_type for item in cart_items
                    )
                    
                    if has_different_store_type:
                        # Clear the cart
                        cart.items.all().delete()
            except Cart.DoesNotExist:
                pass
        
        request.session['store_type'] = store_type
        return JsonResponse({'success': True, 'store_type': store_type})
    
    return JsonResponse({'success': False, 'message': 'Invalid store type'}, status=400)

# ==================== AUTHENTICATION ====================

def signup_view(request):
    """User registration"""
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            phone = data.get('phone')

            # Validation
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'Username already exists'})
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email already registered'})

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone
            )

            # Auto login
            login(request, user)

            return JsonResponse({
                'success': True,
                'message': 'Account created successfully!',
                'redirect': '/'
            })

    return render(request, 'signup.html')

def login_view(request):
    """User login"""
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            remember = data.get('remember', False)

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                # Remember me functionality
                if not remember:
                    request.session.set_expiry(0)  # Browser close

                return JsonResponse({
                    'success': True,
                    'message': 'Login successful!',
                    'redirect': '/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid username or password'
                })

    return render(request, 'login.html')

def logout_view(request):
    """User logout"""
    logout(request)
    return redirect('login')

# ==================== CART OPERATIONS ====================

@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    """Add item to cart"""
    data = json.loads(request.body)
    food_item_id = data.get('food_item_id')
    quantity = int(data.get('quantity', 1))

    food_item = get_object_or_404(FoodItem, id=food_item_id, is_available=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Check if cart has items of different store type
    if cart.items.exists():
        cart_items = cart.items.select_related('food_item').all()
        existing_store_type = cart_items.first().food_item.store_type
        
        if existing_store_type != food_item.store_type:
            return JsonResponse({
                'success': False,
                'message': f'Cannot mix {existing_store_type} and {food_item.store_type} items in cart. Please clear your cart first or switch stores.'
            }, status=400)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        food_item=food_item,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return JsonResponse({
        'success': True,
        'message': f'{food_item.name} added to cart',
        'cart_count': cart.item_count,
        'cart_total': float(cart.total)
    })

@login_required
@require_http_methods(["POST"])
def update_cart_item(request):
    """Update cart item quantity"""
    data = json.loads(request.body)
    cart_item_id = data.get('cart_item_id')
    quantity = int(data.get('quantity'))

    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    cart = cart_item.cart if quantity > 0 else request.user.cart

    return JsonResponse({
        'success': True,
        'cart_count': cart.item_count,
        'cart_total': float(cart.total),
        'item_subtotal': float(cart_item.subtotal) if quantity > 0 else 0
    })

@login_required
@require_http_methods(["POST"])
def remove_from_cart(request):
    """Remove item from cart"""
    data = json.loads(request.body)
    cart_item_id = data.get('cart_item_id')

    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()

    cart = request.user.cart

    return JsonResponse({
        'success': True,
        'message': 'Item removed from cart',
        'cart_count': cart.item_count,
        'cart_total': float(cart.total)
    })

@login_required
def get_cart(request):
    """Get cart contents"""
    cart, _ = Cart.objects.get_or_create(user=request.user)

    items = []
    for item in cart.items.all():
        items.append({
            'id': item.id,
            'food_item_id': item.food_item.id,
            'name': item.food_item.name,
            'price': float(item.food_item.price),
            'quantity': item.quantity,
            'subtotal': float(item.subtotal),
            'image': item.food_item.image.url if item.food_item.image else None
        })

    return JsonResponse({
        'success': True,
        'items': items,
        'cart_count': cart.item_count,
        'subtotal': float(cart.total),
        'delivery_fee': 0,
        'total': float(cart.total)
    })

# ==================== ORDER PLACEMENT ====================

@login_required
@require_http_methods(["POST"])
def place_order(request):
    """Place a new order"""
    data = json.loads(request.body)

    cart = get_object_or_404(Cart, user=request.user)

    if not cart.items.exists():
        return JsonResponse({'success': False, 'message': 'Cart is empty'})

    # Extract order details
    hostel = data.get('hostel')
    room_number = data.get('room_number')
    phone_number = data.get('phone_number')
    delivery_notes = data.get('delivery_notes', '')

    # Calculate totals
    subtotal = cart.total
    delivery_fee = 0  # Free campus delivery
    total = subtotal + delivery_fee

    # Create order
    order = Order.objects.create(
        user=request.user,
        hostel=hostel,
        room_number=room_number,
        phone_number=phone_number,
        delivery_notes=delivery_notes,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        estimated_delivery=timezone.now() + timezone.timedelta(minutes=30)
    )

    # Create order items and update food popularity
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            food_item=cart_item.food_item,
            quantity=cart_item.quantity,
            price_at_order=cart_item.food_item.price
        )

        # Update times ordered
        cart_item.food_item.times_ordered += cart_item.quantity
        cart_item.food_item.save()

    # Create initial status history
    OrderStatusHistory.objects.create(
        order=order,
        status='pending',
        notes='Order placed'
    )

    # Clear cart
    cart.items.all().delete()

    # Award loyalty points
    request.user.loyalty_points += int(total)
    request.user.save()

    return JsonResponse({
        'success': True,
        'message': 'Order placed successfully!',
        'order_number': order.order_number,
        'estimated_delivery': order.estimated_delivery.strftime('%I:%M %p')
    })

# ==================== ORDER TRACKING ====================

@login_required
def my_orders(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')

    # Separate active and completed orders
    active_orders = orders.exclude(status__in=['delivered', 'cancelled'])
    order_history = orders.filter(status__in=['delivered', 'cancelled'])

    context = {
        'active_orders': active_orders,
        'order_history': order_history,
    }
    return render(request, 'my_orders.html', context)

@login_required
def order_detail(request, order_number):
    """View specific order details"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    status_history = order.status_history.all()

    context = {
        'order': order,
        'status_history': status_history,
    }
    return render(request, 'order_detail.html', context)

@login_required
def order_status_api(request, order_number):
    """API endpoint for order status polling"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    return JsonResponse({
        'success': True,
        'status': order.status,
        'status_display': order.get_status_display(),
        'updated_at': order.updated_at.isoformat()
    })

# ==================== USER PROFILE ====================

@login_required
def profile(request):
    """User profile page"""
    if request.method == 'POST':
        user = request.user
        user.phone_number = request.POST.get('phone_number')
        user.default_hostel = request.POST.get('default_hostel')
        user.default_room = request.POST.get('default_room')
        user.save()

        return redirect('profile')

    recent_orders = Order.objects.filter(user=request.user)[:5]

    context = {
        'recent_orders': recent_orders,
    }
    return render(request, 'profile.html', context)

# ==================== ORDER RATING ====================

@login_required
@require_http_methods(["POST"])
def rate_order(request, order_number):
    """Rate and review a delivered order"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user, status='delivered')

    if order.rating:
        return JsonResponse({'success': False, 'message': 'Order already rated'})

    rating = request.POST.get('rating')
    review = request.POST.get('review', '')

    if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
        return JsonResponse({'success': False, 'message': 'Invalid rating'})

    order.rating = int(rating)
    order.review = review
    order.save()

    return redirect('order_detail', order_number=order_number)

# ==================== FOOD REVIEWS ====================

@login_required
@require_http_methods(["POST"])
def submit_food_review(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)

    if order.status != 'delivered':
        return JsonResponse({'success': False, 'message': 'You can only review delivered orders'}, status=400)

    for item in order.items.all():
        rating = request.POST.get(f'rating-{item.food_item.id}')
        comment = request.POST.get(f'comment-{item.food_item.id}', '')

        if rating:
            if not FoodReview.objects.filter(user=request.user, food_item=item.food_item, order=order).exists():
                FoodReview.objects.create(
                    user=request.user,
                    food_item=item.food_item,
                    order=order,
                    rating=rating,
                    comment=comment
                )

    return redirect('order_detail', order_number=order.order_number)


# ==================== ORDER CANCELLATION ====================

@login_required
@require_http_methods(["POST"])
def cancel_order(request, order_number):
    """Cancel an order with reason"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # Only allow cancellation for pending or preparing orders
    if order.status not in ['pending', 'preparing']:
        return JsonResponse({'success': False, 'message': 'Order cannot be cancelled at this stage'})

    reason = request.POST.get('reason', '').strip()
    if not reason:
        return JsonResponse({'success': False, 'message': 'Please provide a cancellation reason'})

    # Update order status
    order.status = 'cancelled'
    order.cancellation_reason = reason
    order.save()

    # Create status history
    OrderStatusHistory.objects.create(
        order=order,
        status='cancelled',
        notes=f'Cancelled by user: {reason}'
    )

    return JsonResponse({'success': True, 'message': 'Order cancelled successfully'})

