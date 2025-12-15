import os
import json
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .excel_adapter import ExcelAdapter
from .services import BidService, AuthService
from common.exceptions import BusinessException, SystemException

# Initialize logger (using common logger if configured, else standard django logger)
logger = logging.getLogger(__name__)

# Dependeny Injection Setup
DATA_DIR = os.path.join(settings.BASE_DIR, 'data')
adapter = ExcelAdapter(DATA_DIR)
bid_service = BidService(adapter)
auth_service = AuthService(adapter)


def index(request):
    return redirect('auctions:products_list')


def products_list(request):
    try:
        products = adapter.get_all_products()
        employee = request.session.get('employee')
        return render(request, 'products.html', {'products': products, 'employee': employee})
    except Exception as e:
        logger.error("Error loading products list", exc_info=True)
        return render(request, 'error.html', {'error': '無法加載商品列表，請稍後重試。'})


def product_detail(request, product_id):
    try:
        product = adapter.get_product_by_id(product_id)
        if not product:
            return render(request, 'product_detail.html', {'error': '商品不存在'})
        employee = request.session.get('employee')
        return render(request, 'product_detail.html', {'product': product, 'employee': employee})
    except Exception as e:
        logger.error(f"Error loading product {product_id}", exc_info=True)
        return render(request, 'product_detail.html', {'error': '系統錯誤'})


def product_poll(request, product_id):
    try:
        product = adapter.get_product_by_id(product_id)
        if not product:
            return JsonResponse({'success': False, 'message': 'PRODUCT_NOT_FOUND'}, status=404)
        bids = adapter.get_bids_for_product(product_id, limit=10)
        return JsonResponse({'success': True, 'product': product, 'bids': bids})
    except Exception as e:
        logger.error(f"Error polling product {product_id}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'INTERNAL_ERROR'}, status=500)


def login_view(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employeeId')
        try:
            emp = auth_service.login(employee_id)
            # Session management remains in View
            request.session['employee'] = {
                'id': emp.get('id'),
                'employeeId': emp.get('employeeId'), 
                'name': emp.get('name'), 
                'department': emp.get('department')
            }
            return redirect('auctions:products_list')
        except BusinessException as e:
            return render(request, 'login.html', {'error': e.message})
        except Exception as e:
            logger.error("Login failed", exc_info=True)
            return render(request, 'login.html', {'error': '登入系統異常'})
            
    return render(request, 'login.html')


def logout_view(request):
    request.session.pop('employee', None)
    request.session.pop('is_admin', None)
    return redirect('auctions:products_list')


def admin_login(request):
    if request.method == 'POST':
        pwd = request.POST.get('password')
        # In a real app, this should also be in AuthService or similar, but keeping simple as per scope
        if pwd and pwd == os.getenv('ADMIN_PASSWORD'):
            request.session['is_admin'] = True
            return redirect('/admin/')
        return render(request, 'admin_login.html', {'error': '密碼錯誤'})
    return render(request, 'admin_login.html')


@csrf_exempt
def place_bid(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
        
    try:
        data = json.loads(request.body)
        product_id = data.get('productId')
        amount = data.get('amount')
        
        # Validation of input types
        if not product_id or not amount:
             raise BusinessException("Missing productId or amount", code='INVALID_PAYLOAD')
             
        try:
            product_id = int(product_id)
            amount = int(amount)
        except ValueError:
             raise BusinessException("Invalid number format", code='INVALID_PAYLOAD')

        # Authentication check
        session_emp = request.session.get('employee')
        bidder_employee_id = session_emp.get('employeeId') if session_emp else data.get('employeeId')
        
        if not bidder_employee_id:
            raise BusinessException("User not logged in", code='UNAUTHORIZED')

        # Call Service
        result = bid_service.place_bid(product_id, bidder_employee_id, amount)
        return JsonResponse(result)

    except BusinessException as e:
        logger.info(f"Bid business error: {e.message}")
        return JsonResponse({
            'success': False, 
            'message': e.message, 
            'errorCode': e.code
        }, status=400)
        
    except SystemException as e:
        logger.error(f"Bid system error: {e.message}")
        return JsonResponse({
            'success': False, 
            'message': '系統繁忙，請稍後重試', 
            'errorCode': 'INTERNAL_ERROR'
        }, status=500)
        
    except Exception as e:
        logger.error("Unexpected error in place_bid", exc_info=True)
        return JsonResponse({
            'success': False, 
            'message': '未知錯誤', 
            'errorCode': 'UNKNOWN_ERROR'
        }, status=500)
