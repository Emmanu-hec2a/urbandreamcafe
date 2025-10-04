from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
import json

def staff_member_required(view_func=None, login_url='admin_login'):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=login_url
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

def admin_login(request):
    """Admin login page"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None and user.is_staff:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': 'Admin login successful!',
                    'redirect': '/admin-panel/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid admin credentials or insufficient permissions'
                })

    return render(request, 'admin/login.html')

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import *
import json

# ==================== ADMIN DASHBOARD ====================

@staff_member_required(login_url='admin_login')
def admin_dashboard(request):
    """Main admin dashboard with overview"""
    today = timezone.now().date()

    # Today's statistics
    today_orders = Order.objects.filter(created_at__date=today)
    today_revenue = today_orders.aggregate(total=Sum('total'))['total'] or 0
    pending_orders = Order.objects.filter(status='pending').count()
    preparing_orders = Order.objects.filter(status='preparing').count()
    out_for_delivery = Order.objects.filter(status='out_for_delivery').count()

    # Popular items today
    popular_today = OrderItem.objects.filter(
        order__created_at__date=today
    ).values(
        'food_item__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('price_at_order')
    ).order_by('-total_quantity')[:5]

    # This week's stats
    week_start = today - timedelta(days=today.weekday())
    weekly_orders = Order.objects.filter(created_at__date__gte=week_start)
    weekly_revenue = weekly_orders.aggregate(total=Sum('total'))['total'] or 0

    # Peak hours (last 7 days)
    peak_hours = Order.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).extra(
        select={'hour': 'EXTRACT(hour FROM created_at)'}
    ).values('hour').annotate(
        order_count=Count('id')
    ).order_by('-order_count')[:5]

    context = {
        'today_orders_count': today_orders.count(),
        'today_revenue': today_revenue,
        'pending_orders': pending_orders,
        'preparing_orders': preparing_orders,
        'out_for_delivery': out_for_delivery,
        'popular_today': popular_today,
        'weekly_orders': weekly_orders.count(),
        'weekly_revenue': weekly_revenue,
        'peak_hours': peak_hours,
    }

    return render(request, 'admin/dashboard.html', context)

# ==================== ORDER MANAGEMENT ====================

@staff_member_required(login_url='admin_login')
def admin_orders(request):
    """Order management page"""
    status_filter = request.GET.get('status', 'all')

    orders = Order.objects.all().select_related('user').prefetch_related('items')

    if status_filter != 'all':
        orders = orders.filter(status=status_filter)

    # Recent orders first
    orders = orders.order_by('-created_at')

    context = {
        'orders': orders[:50],  # Limit to recent 50
        'status_filter': status_filter,
    }

    return render(request, 'admin/orders.html', context)

@staff_member_required(login_url='admin_login')
def get_new_orders(request):
    """API endpoint to check for new orders (for auto-refresh)"""
    last_check = request.GET.get('last_check')

    if last_check:
        last_check_time = timezone.datetime.fromisoformat(last_check)
        new_orders = Order.objects.filter(
            created_at__gt=last_check_time,
            status='pending'
        )
    else:
        new_orders = Order.objects.filter(status='pending')

    orders_data = []
    for order in new_orders:
        orders_data.append({
            'order_number': order.order_number,
            'user': order.user.username,
            'total': float(order.total),
            'hostel': order.hostel,
            'room': order.room_number,
            'phone': order.phone_number,
            'created_at': order.created_at.isoformat(),
        })

    return JsonResponse({
        'success': True,
        'new_orders_count': len(orders_data),
        'orders': orders_data,
        'timestamp': timezone.now().isoformat()
    })

@staff_member_required(login_url='admin_login')
def admin_order_detail(request, order_number):
    """View detailed order information"""
    order = get_object_or_404(Order, order_number=order_number)
    status_history = order.status_history.all()

    context = {
        'order': order,
        'status_history': status_history,
    }

    return render(request, 'admin/order_detail.html', context)

@staff_member_required(login_url='admin_login')
def update_order_status(request):
    """Update order status"""
    if request.method == 'POST':
        data = json.loads(request.body)
        order_number = data.get('order_number')
        new_status = data.get('status')
        notes = data.get('notes', '')

        order = get_object_or_404(Order, order_number=order_number)

        # Update status
        old_status = order.status
        order.status = new_status

        # Set delivered timestamp
        if new_status == 'delivered':
            order.delivered_at = timezone.now()

        order.save()

        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=notes or f'Status changed from {old_status} to {new_status}'
        )

        return JsonResponse({
            'success': True,
            'message': f'Order {order_number} status updated to {new_status}',
            'new_status': new_status,
            'status_display': order.get_status_display()
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@staff_member_required(login_url='admin_login')
def cancel_order(request):
    """Cancel an order"""
    if request.method == 'POST':
        data = json.loads(request.body)
        order_number = data.get('order_number')
        reason = data.get('reason', 'Cancelled by admin')

        order = get_object_or_404(Order, order_number=order_number)
        order.status = 'cancelled'
        order.cancellation_reason = reason
        order.save()

        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            notes=reason
        )

        return JsonResponse({
            'success': True,
            'message': f'Order {order_number} cancelled'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

# ==================== FOOD MENU MANAGEMENT ====================

@staff_member_required(login_url='admin_login')
def admin_menu(request):
    """Food menu management"""
    categories = FoodCategory.objects.all()
    food_items = FoodItem.objects.all().select_related('category')

    context = {
        'categories': categories,
        'food_items': food_items,
    }

    return render(request, 'admin/menu.html', context)

@staff_member_required(login_url='admin_login')
def toggle_food_availability(request):
    """Toggle food item availability"""
    if request.method == 'POST':
        data = json.loads(request.body)
        food_item_id = data.get('food_item_id')

        food_item = get_object_or_404(FoodItem, id=food_item_id)
        food_item.is_available = not food_item.is_available
        food_item.save()

        return JsonResponse({
            'success': True,
            'is_available': food_item.is_available,
            'message': f'{food_item.name} is now {"available" if food_item.is_available else "unavailable"}'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@staff_member_required(login_url='admin_login')
def update_food_price(request):
    """Update food item price"""
    if request.method == 'POST':
        data = json.loads(request.body)
        food_item_id = data.get('food_item_id')
        new_price = data.get('price')

        food_item = get_object_or_404(FoodItem, id=food_item_id)
        food_item.price = new_price
        food_item.save()

        return JsonResponse({
            'success': True,
            'message': f'{food_item.name} price updated to KES {new_price}'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

# ==================== ANALYTICS ====================

@staff_member_required(login_url='admin_login')
def admin_analytics(request):
    """Analytics and reports"""
    # Date range
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)

    # Revenue over time
    daily_revenue = Order.objects.filter(
        created_at__gte=start_date,
        status='delivered'
    ).extra(
        select={'day': 'DATE(created_at)'}
    ).values('day').annotate(
        revenue=Sum('total'),
        orders=Count('id')
    ).order_by('day')

    # Top selling items
    top_items = OrderItem.objects.filter(
        order__created_at__gte=start_date
    ).values(
        'food_item__name',
        'food_item__category__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('price_at_order')
    ).order_by('-total_quantity')[:10]

    # Top customers
    top_customers = Order.objects.filter(
        created_at__gte=start_date,
        status='delivered'
    ).values(
        'user__username',
        'user__phone_number'
    ).annotate(
        total_orders=Count('id'),
        total_spent=Sum('total')
    ).order_by('-total_orders')[:10]

    # Order status distribution
    status_distribution = Order.objects.filter(
        created_at__gte=start_date
    ).values('status').annotate(
        count=Count('id')
    )

    # Calculate totals
    total_revenue = sum(item['revenue'] for item in daily_revenue)
    total_orders = sum(item['orders'] for item in daily_revenue)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    # Peak hours
    peak_hours = Order.objects.filter(
        created_at__gte=start_date
    ).extra(
        select={'hour': 'EXTRACT(hour FROM created_at)'}
    ).values('hour').annotate(
        order_count=Count('id')
    ).order_by('-order_count')[:10]

    context = {
        'daily_revenue': list(daily_revenue),
        'top_items': top_items,
        'top_customers': top_customers,
        'status_distribution': status_distribution,
        'days': days,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'peak_hours': peak_hours,
    }

    return render(request, 'admin/analytics.html', context)

# ==================== CUSTOMER MANAGEMENT ====================

@staff_member_required(login_url='admin_login')
def admin_customers(request):
    """Customer management"""
    customers = User.objects.filter(is_staff=False).annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__total')
    ).order_by('-total_orders')

    context = {
        'customers': customers,
        
    }

    return render(request, 'admin/customers.html', context)
