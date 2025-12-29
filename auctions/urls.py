from django.urls import path
from . import views
from . import admin_views

app_name = 'auctions'

urlpatterns = [
    # User Views
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('products/', views.products_list, name='products_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('my-bids/', views.user_bids_list, name='user_bids_list'),

    # Admin Views
    path('admin/', lambda r: __import__('django.shortcuts').shortcuts.redirect('auctions:admin_login')),
    path('admin/login/', admin_views.admin_login_view, name='admin_login'),
    path('admin/logout/', admin_views.admin_logout_view, name='admin_logout'),
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/products/', admin_views.admin_products_list, name='admin_products_list'),
    path('admin/products/create/', admin_views.admin_product_create, name='admin_product_create'),
    path('admin/products/<int:product_id>/edit/', admin_views.admin_product_edit, name='admin_product_edit'),
    path('admin/products/<int:product_id>/delete/', admin_views.admin_product_delete, name='admin_product_delete'),
    path('admin/bids/', admin_views.admin_bids_list, name='admin_bids_list'),

    # API endpoints
    path('api/products/<int:product_id>/poll/', views.product_poll, name='product_poll'),
    path('api/bids/', views.place_bid, name='place_bid'),
    path('api/products/<int:product_id>/images/', admin_views.get_product_images, name='get_product_images'),
    path('api/products/<int:product_id>/upload-images/', admin_views.upload_product_images, name='upload_product_images'),
]
