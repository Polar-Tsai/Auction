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
        
        
        # Separate products by status for sorting
        closed_products = [p for p in products if p.get('status') in ['Closed', 'Unsold', 'Ended']]
        other_products = [p for p in products if p.get('status') not in ['Closed', 'Unsold', 'Ended']]
        
        # Sort closed products by end_time (descending - latest first)
        from datetime import datetime
        def parse_end_time(product):
            end_str = product.get('end_time', '')
            if not end_str:
                return datetime.min
            try:
                if 'T' in end_str:
                    return datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                else:
                    return datetime.strptime(end_str, "%Y-%m-%d %H:%M")
            except:
                return datetime.min
        
        closed_products.sort(key=parse_end_time, reverse=True)
        
        # Combine: closed products first, then others
        products = closed_products + other_products
        
        # Add highest bidder and winner information for all products
        for product in products:
            # Get the highest bid for this product
            bids = adapter.get_bids_for_product(product['id'], limit=1)
            
            if bids:
                bidder_id = bids[0].get('bidder_id')
                # For all products: store highest bidder ID (工號)
                product['highest_bidder_id'] = bidder_id
                
                #  For closed products: also get winner name
                if product.get('status') in ['Closed', 'Unsold', 'Ended']:
                    winner = adapter.get_employee_by_employeeId(bidder_id)
                    product['winner_name'] = winner.get('name') if winner else bidder_id
                    logger.info(f"Product {product['id']} ({product['name']}): Winner = {product['winner_name']}")
                else:
                    product['winner_name'] = None
            else:
                # No bids yet
                product['highest_bidder_id'] = None
                product['winner_name'] = None
                if product.get('status') in ['Closed', 'Unsold', 'Ended']:
                    logger.info(f"Product {product['id']} ({product['name']}): No bids")


        
        # Calculate status aggregation counts
        status_counts = {
            'Open': 0,
            'Closed': 0,
            'Upcoming': 0
        }
        
        for product in products:
            status = product.get('status')
            if status == 'Open':
                status_counts['Open'] += 1
            elif status == 'Upcoming':
                status_counts['Upcoming'] += 1
            else:  # Closed, Ended or Unsold
                status_counts['Closed'] += 1

        
        employee = request.session.get('employee')
        return render(request, 'products.html', {
            'products': products, 
            'employee': employee,
            'status_counts': status_counts
        })
    except Exception as e:
        logger.error("Error loading products list", exc_info=True)
        return render(request, 'error.html', {'error': '無法加載商品列表,請稍後重試。'})



def product_detail(request, product_id):
    try:
        product = adapter.get_product_by_id(product_id)
        if not product:
            return render(request, 'product_detail.html', {'error': '商品不存在'})
        
        # Calculate bid increment (start_price / 10, rounded up)
        import math
        start_price = int(product.get('start_price', 0))
        bid_increment = math.ceil(start_price / 10) if start_price > 0 else 1
        
        images = adapter.get_product_images(product_id)
        employee = request.session.get('employee')
        return render(request, 'product_detail.html', {
            'product': product, 
            'images': images, 
            'employee': employee,
            'bid_increment': bid_increment
        })
    except Exception as e:
        logger.error(f"Error loading product {product_id}", exc_info=True)
        return render(request, 'product_detail.html', {'error': '系統錯誤'})


def product_poll(request, product_id):
    try:
        product = adapter.get_product_by_id(product_id)
        if not product:
            return JsonResponse({'success': False, 'message': 'PRODUCT_NOT_FOUND'}, status=404)
        bids = adapter.get_bids_for_product(product_id, limit=10)
        
        # Add highest bidder information (只返回工號)
        highest_bidder = None
        if bids:
            bidder_id = bids[0].get('bidder_id')
            highest_bidder = {
                'id': bidder_id,
                'amount': bids[0].get('amount')
            }
        
        # Add bidder names to bid history
        for bid in bids:
            bidder = adapter.get_employee_by_employeeId(bid.get('bidder_id'))
            if bidder:
                bid['bidder_name'] = bidder.get('name')
            else:
                bid['bidder_name'] = bid.get('bidder_id')
        
        return JsonResponse({
            'success': True, 
            'product': product, 
            'bids': bids,
            'highest_bidder': highest_bidder
        })
    except Exception as e:
        logger.error(f"Error polling product {product_id}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'INTERNAL_ERROR'}, status=500)


def products_poll(request):
    """
    API endpoint for real-time product list polling.
    Returns all products with latest data, status counts, and winner information.
    """
    try:
        from datetime import datetime
        
        products = adapter.get_all_products()
        
        # Separate products by status for sorting
        closed_products = [p for p in products if p.get('status') in ['Closed', 'Unsold', 'Ended']]
        other_products = [p for p in products if p.get('status') not in ['Closed', 'Unsold', 'Ended']]
        
        # Sort closed products by end_time (descending - latest first)
        def parse_end_time(product):
            end_str = product.get('end_time', '')
            if not end_str:
                return datetime.min
            try:
                if 'T' in end_str:
                    return datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                else:
                    return datetime.strptime(end_str, "%Y-%m-%d %H:%M")
            except:
                return datetime.min
        
        closed_products.sort(key=parse_end_time, reverse=True)
        
        # Combine: closed products first, then others
        products = closed_products + other_products
        
        # Add highest bidder and winner information for all products
        for product in products:
            # Get the highest bid for this product
            bids = adapter.get_bids_for_product(product['id'], limit=1)
            
            if bids:
                bidder_id = bids[0].get('bidder_id')
                # For all products: store highest bidder ID (工號)
                product['highest_bidder_id'] = bidder_id
                
                # For closed products: also get winner name
                if product.get('status') in ['Closed', 'Unsold', 'Ended']:
                    winner = adapter.get_employee_by_employeeId(bidder_id)
                    product['winner_name'] = winner.get('name') if winner else bidder_id
                else:
                    product['winner_name'] = None
            else:
                # No bids yet
                product['highest_bidder_id'] = None
                product['winner_name'] = None
        
        # Calculate status counts
        status_counts = {'Open': 0, 'Closed': 0, 'Upcoming': 0}
        for product in products:
            status = product.get('status')
            if status == 'Open':
                status_counts['Open'] += 1
            elif status == 'Upcoming':
                status_counts['Upcoming'] += 1
            else:  # Closed, Ended or Unsold
                status_counts['Closed'] += 1
        
        return JsonResponse({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'products': products,
            'status_counts': status_counts
        })
    except Exception as e:
        logger.error("Error in products_poll", exc_info=True)
        return JsonResponse({'success': False, 'message': 'INTERNAL_ERROR'}, status=500)




def login_view(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employeeId')
        password = request.POST.get('password')  # Get password from form
        try:
            # Pass password to auth_service
            emp = auth_service.login(employee_id, password)
            # Session management remains in View
            request.session['employee'] = {
                'id': emp.get('id'),
                'employeeId': emp.get('employeeId'), 
                'name': emp.get('name'), 
                'department': emp.get('department'),
                'is_potential_admin': emp.get('admin', 'False') == 'True'  # Parse admin field
            }
            return redirect('auctions:products_list')
        except BusinessException as e:
            return render(request, 'login.html', {'error': e.message})
        except Exception as e:
            logger.error("Login failed", exc_info=True)
            return render(request, 'login.html', {'error': '登入系統異常'})
            
    return render(request, 'login.html')


def user_bids_list(request):
    employee = request.session.get('employee')
    if not employee:
        return redirect('auctions:login')
        
    try:
        bids = adapter.get_bids_for_employee(employee.get('employeeId'))
        return render(request, 'user_bids.html', {'bids': bids, 'employee': employee})
    except Exception as e:
        logger.error(f"Error loading user bids for {employee.get('employeeId')}", exc_info=True)
        return render(request, 'error.html', {'error': '無法讀取您的出價紀錄'})


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
