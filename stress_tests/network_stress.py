import requests
import concurrent.futures
import time
import json

# Target Configuration
BASE_URL = "http://10.10.10.205"  # From user
PRODUCT_ID = 34
PLAYERS = 30

def bid_task(user_index):
    # API endpoint
    url = f"{BASE_URL}/zh-hant/api/bids/"
    
    bidder_id = f"NET_STRESS_{user_index:03d}"
    # ULTIMATE COLLISION: All users bid EXACTLY 30000 at the same time
    payload = {
        "productId": PRODUCT_ID,
        "amount": 30000, 
        "employeeId": bidder_id
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    start = time.time()
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        end = time.time()
        res_data = {}
        try:
            res_data = response.json()
        except:
            res_data = {"raw_text": response.text[:200]}

        return {
            "user": bidder_id,
            "status": response.status_code,
            "data": res_data,
            "time": end - start
        }
    except Exception as e:
        return {
            "user": bidder_id,
            "status": "ERROR",
            "error": str(e),
            "time": time.time() - start
        }

def run_network_test():
    print(f"🚀 Launching NETWORK STRESS TEST on {BASE_URL}")
    print(f"🔥 Targets: {PLAYERS} concurrent bidders on Product {PRODUCT_ID}")
    
    results = []
    start_all = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=PLAYERS) as executor:
        futures = [executor.submit(bid_task, i) for i in range(PLAYERS)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    duration = time.time() - start_all
    success = [r for r in results if r['status'] == 200 and r.get('data', {}).get('success')]
    biz_fail = [r for r in results if r['status'] == 400]
    sys_fail = [r for r in results if r['status'] == 500 or r['status'] == "ERROR"]

    print(f"RESULTS: Success={len(success)}, BizDeny={len(biz_fail)}, Error={len(sys_fail)}, Time={duration:.2f}s")
    if success:
        last_success = max(success, key=lambda x: x['data'].get('amount', 0))
        print(f"WINNER: {last_success['user']} @ ${last_success['data'].get('amount')}")

if __name__ == "__main__":
    run_network_test()
