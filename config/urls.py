from django.contrib import admin
from django.urls import path, include
from urbanfoods import views, admin_views
from django.conf import settings
from django.views.generic import RedirectView
from django.templatetags.static import static as static_url
from django.conf.urls.static import static

urlpatterns = [
    # Comment out or remove the default Django admin URL to disable access
    # path('admin/', admin.site.urls),
    # path(' ', include('urbanfoods.urls')),
    # ==================== PUBLIC PAGES ====================
    path('', views.homepage, name='homepage'),
    
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ==================== CART & ORDERS ====================
    # Cart operations
    path('api/cart/', views.get_cart, name='get_cart'),
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/update/', views.update_cart_item, name='update_cart_item'),
    path('api/cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    
    # Order placement
    path('api/order/place/', views.place_order, name='place_order'),
    
    # Order tracking
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('api/orders/<str:order_number>/status/', views.order_status_api, name='order_status_api'),
    
    # User profile
    path('orders/<str:order_number>/rate/', views.rate_order, name='rate_order'),
    path('profile/', views.profile, name='profile'),
    
    # ==================== ADMIN DASHBOARD ====================
    path('admin-panel/login/', admin_views.admin_login, name='admin_login'),
    path('admin-panel/', admin_views.admin_dashboard, name='admin_dashboard'),
    
    # Order management
    path('admin-panel/orders/', admin_views.admin_orders, name='admin_orders'),
    path('admin-panel/orders/<str:order_number>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('admin-panel/api/orders/new/', admin_views.get_new_orders, name='get_new_orders'),
    path('admin-panel/api/orders/update-status/', admin_views.update_order_status, name='update_order_status'),
    path('admin-panel/api/orders/cancel/', admin_views.cancel_order, name='cancel_order'),
    
    # Menu management
    path('admin-panel/menu/', admin_views.admin_menu, name='admin_menu'),
    path('admin-panel/api/menu/toggle-availability/', admin_views.toggle_food_availability, name='toggle_food_availability'),
    path('admin-panel/api/menu/update-price/', admin_views.update_food_price, name='update_food_price'),
    path('admin-panel/api/menu/add-category/', admin_views.add_category, name='add_category'),
    path('admin-panel/api/menu/edit-category/', admin_views.edit_category, name='edit_category'),
    path('admin-panel/api/menu/delete-category/', admin_views.delete_category, name='delete_category'),
    path('admin-panel/api/menu/add-food-item/', admin_views.add_food_item, name='add_food_item'),
    path('admin-panel/api/menu/edit-food-item/', admin_views.edit_food_item, name='edit_food_item'),
    path('admin-panel/api/menu/delete-food-item/', admin_views.delete_food_item, name='delete_food_item'),
    
    # Analytics
    path('admin-panel/analytics/', admin_views.admin_analytics, name='admin_analytics'),
    
    # Customer management
    path('admin-panel/customers/', admin_views.admin_customers, name='admin_customers'),
    path('admin-panel/customers/<int:customer_id>/', admin_views.admin_customer_detail, name='admin_customer_detail'),
    path('admin-panel/api/customers/<int:customer_id>/orders/', admin_views.get_customer_orders, name='get_customer_orders'),
    path('admin-panel/api/customers/send-message/', admin_views.send_customer_message, name='send_customer_message'),
    path('admin-panel/api/customers/update-status/', admin_views.update_customer_status, name='update_customer_status'),

    # Dashboard API
    path('admin-panel/api/dashboard/stats/', admin_views.admin_dashboard_stats, name='dashboard_stats'),
    path('admin-panel/api/orders/recent/', admin_views.get_new_orders, name='admin_api_new_orders'),
    path('admin-panel/api/admin/update-profile/', admin_views.update_admin_profile, name='admin_api_update_admin_profile'),
    
    # Reviews management
    path('orders/<str:order_number>/submit_review/', views.submit_food_review, name='submit_food_review'),

    # Favicon
    path('favicon.ico', RedirectView.as_view(url=static_url('images/favicon.png'), permanent=True)),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
