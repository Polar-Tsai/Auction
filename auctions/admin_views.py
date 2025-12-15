from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings
from .services import AdminService, ProductService
from .excel_adapter import ExcelAdapter

# Initialize services
# Note: Ideally dependency injection or singleton pattern, but instantiating here is simple for Django
adapter = ExcelAdapter(settings.DATA_DIR)
admin_service = AdminService(adapter)
product_service = ProductService(adapter)

def admin_login_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if admin_service.authenticate(password):
            # Set session
            request.session['is_admin'] = True
            return redirect('auctions:admin_dashboard')
        else:
            return render(request, 'admin_login.html', {'error': '密碼錯誤'})
    return render(request, 'admin_login.html')

def admin_logout_view(request):
    request.session.flush()
    return redirect('auctions:index')

def admin_dashboard(request):
    if not request.session.get('is_admin'):
        return redirect('auctions:admin_login')
    
    stats = admin_service.get_dashboard_stats()
    return render(request, 'admin_dashboard.html', {'stats': stats})

def admin_products_list(request):
    if not request.session.get('is_admin'):
        return redirect('auctions:admin_login')
    
    products = product_service.get_all_products()
    return render(request, 'admin_products_list.html', {'products': products})

def admin_product_create(request):
    if not request.session.get('is_admin'):
        return redirect('auctions:admin_login')
        
    if request.method == 'POST':
        try:
            data = {
                'name': request.POST.get('name'),
                'start_price': request.POST.get('start_price'),
                'description': request.POST.get('description'),
                'image_url': request.POST.get('image_url'),
                'start_time': request.POST.get('start_time'), # Format?
                'end_time': request.POST.get('end_time'),
                'status': request.POST.get('status', 'Upcoming')
            }
            product_service.create_product(data)
            return redirect('auctions:admin_products_list')
        except Exception as e:
            return render(request, 'admin_product_form.html', {'error': str(e), 'action': 'Create'})

    return render(request, 'admin_product_form.html', {'action': 'Create'})

def admin_product_edit(request, product_id):
    if not request.session.get('is_admin'):
        return redirect('auctions:admin_login')
    
    product = product_service.get_product(product_id)
    if not product:
        return redirect('auctions:admin_products_list')

    if request.method == 'POST':
        try:
            data = {
                'name': request.POST.get('name'),
                'start_price': request.POST.get('start_price'), # Should strict check if bids exist
                'current_price': request.POST.get('current_price'), # Admin override
                'description': request.POST.get('description'),
                'image_url': request.POST.get('image_url'),
                'start_time': request.POST.get('start_time'),
                'end_time': request.POST.get('end_time'),
                'status': request.POST.get('status')
            }
            # Remove empty keys to avoid overwriting with None
            data = {k: v for k, v in data.items() if v is not None}
            
            product_service.update_product(product_id, data)
            return redirect('auctions:admin_products_list')
        except Exception as e:
            return render(request, 'admin_product_form.html', {'error': str(e), 'product': product, 'action': 'Edit'})

    return render(request, 'admin_product_form.html', {'product': product, 'action': 'Edit'})

def admin_product_delete(request, product_id):
    if not request.session.get('is_admin'):
        return redirect('auctions:admin_login')
        
    if request.method == 'POST':
        product_service.delete_product(product_id)
        
    return redirect('auctions:admin_products_list')

def admin_bids_list(request):
    if not request.session.get('is_admin'):
        return redirect('auctions:admin_login')
    # Use adapter directly or via generic service
    # Just reading raw CSV is fine for now
    import pandas as pd
    f = adapter.bids_path
    try:
        df = pd.read_csv(f)
        bids = df.sort_values('bid_timestamp', ascending=False).to_dict('records')
    except:
        bids = []
    return render(request, 'admin_bids_list.html', {'bids': bids})
