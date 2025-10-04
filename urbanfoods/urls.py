from django.urls import path
from . import views
from . import admin_views

app_name = 'urbanfoods'

urlpatterns = [
    # Public pages
    path('', views.homepage, name='homepage'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

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
    path('profile/', views.profile, name='profile'),
    path('orders/<str:order_number>/rate/', views.rate_order, name='rate_order'),
    path('orders/<str:order_number>/submit_review/', views.submit_food_review, name='submit_food_review'),


]
