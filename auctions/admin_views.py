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
    
    # 為每個產品添加第一張圖片
    for product in products:
        try:
            photo_dir = Path(settings.BASE_DIR) / 'data_photo' / str(product['id'])
            if photo_dir.exists():
                images = sorted([
                    f for f in photo_dir.iterdir() 
                    if f.suffix.lower() in ['.jpg', '.jpeg', '.png']
                ])
                if images:
                    # 使用第一張圖片
                    product['first_image_url'] = f"/data_photo/{product['id']}/{images[0].name}"
                else:
                    product['first_image_url'] = None
            else:
                product['first_image_url'] = None
        except Exception as e:
            product['first_image_url'] = None
    
    return render(request, 'admin_products_list.html', {'products': products})

def admin_product_create(request):
    if not request.session.get('is_admin'):
        return redirect('auctions:admin_login')
        
    if request.method == 'POST':
        try:
            status = 'Unsold' if request.POST.get('is_unsold') else 'Upcoming'
            # Type casting for prices to avoid pandas dtype warnings
            start_price = request.POST.get('start_price')
            if start_price: start_price = int(start_price)
            
            data = {
                'name': request.POST.get('name'),
                'start_price': start_price,
                'description': request.POST.get('description'),
                'start_time': request.POST.get('start_time'), # Format?
                'end_time': request.POST.get('end_time'),
                'status': status
            }
            product_id = product_service.create_product(data)
            # Redirect to edit page instead of list, so admin can upload images
            return redirect('auctions:admin_product_edit', product_id=product_id)
        except Exception as e:
            return render(request, 'admin_product_form.html', {'error': str(e), 'action': 'Create', 'product': {}})

    return render(request, 'admin_product_form.html', {'action': 'Create', 'product': {}})


def admin_product_edit(request, product_id):
    if not request.session.get('is_admin'):
        return redirect('auctions:admin_login')
    
    product = product_service.get_product(product_id)
    if not product:
        return redirect('auctions:admin_products_list')

    if request.method == 'POST':
        try:
            status = 'Unsold' if request.POST.get('is_unsold') else ''
            
            # Type casting
            start_price = request.POST.get('start_price')
            current_price = request.POST.get('current_price')
            if start_price: start_price = int(start_price)
            if current_price: current_price = float(current_price)

            data = {
                'name': request.POST.get('name'),
                'start_price': start_price,
                'current_price': current_price,
                'description': request.POST.get('description'),
                'start_time': request.POST.get('start_time'),
                'end_time': request.POST.get('end_time'),
                'status': status
            }

            # Remove empty keys to avoid overwriting with None
            data = {k: v for k, v in data.items() if v is not None}
            
            product_service.update_product(product_id, data)
            return redirect('auctions:admin_products_list')
        except Exception as e:
            return render(request, 'admin_product_form.html', {'error': str(e), 'product': product, 'action': 'Edit'})

    # 格式化時間為 datetime-local 輸入框格式 (YYYY-MM-DDTHH:MM)
    from datetime import datetime
    if product.get('start_time'):
        try:
            dt = datetime.fromisoformat(str(product['start_time']).replace('Z', '+00:00'))
            product['start_time'] = dt.strftime('%Y-%m-%dT%H:%M')
        except:
            pass
    
    if product.get('end_time'):
        try:
            dt = datetime.fromisoformat(str(product['end_time']).replace('Z', '+00:00'))
            product['end_time'] = dt.strftime('%Y-%m-%dT%H:%M')
        except:
            pass

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

# API endpoints for image management
import os
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def get_product_images(request, product_id):
    """Get list of existing images for a product"""
    try:
        photo_dir = Path(settings.BASE_DIR) / 'data_photo' / str(product_id)
        
        if not photo_dir.exists():
            return JsonResponse({'success': True, 'images': []})
        
        # Get all image files
        image_files = []
        for file in sorted(photo_dir.iterdir()):
            if file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                image_files.append({
                    'filename': file.name,
                    'url': f'/data_photo/{product_id}/{file.name}'
                })
        
        return JsonResponse({'success': True, 'images': image_files})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_http_methods(["POST"])
def upload_product_images(request, product_id):
    """Upload images for a product"""
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'message': '未授權'}, status=403)
    
    try:
        photo_dir = Path(settings.BASE_DIR) / 'data_photo' / str(product_id)
        photo_dir.mkdir(parents=True, exist_ok=True)
        
        # Handle deletions first
        delete_images = request.POST.getlist('delete_images')
        for filename in delete_images:
            file_path = photo_dir / filename
            if file_path.exists() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                file_path.unlink()
        
        # Get uploaded files
        uploaded_files = request.FILES.getlist('images')
        
        if not uploaded_files and not delete_images:
            return JsonResponse({'success': False, 'message': '沒有檔案上傳'})
        
        # Get existing images to determine numbering
        existing_images = sorted([
            f for f in photo_dir.iterdir() 
            if f.suffix.lower() in ['.jpg', '.jpeg', '.png']
        ])
        next_number = len(existing_images) + 1
        
        uploaded_count = 0
        for file in uploaded_files:
            # Validate file type
            file_ext = os.path.splitext(file.name)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png']:
                continue
            
            # Save with numbered filename
            new_filename = f"{next_number}{file_ext}"
            file_path = photo_dir / new_filename
            
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            uploaded_count += 1
            next_number += 1
        
        return JsonResponse({
            'success': True,
            'message': f'成功上傳 {uploaded_count} 張圖片',
            'uploaded_count': uploaded_count,
            'deleted_count': len(delete_images)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
