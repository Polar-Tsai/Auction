import re

# Read the file
with open('auctions/services.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the bid frequency check section
old_code = '''        # Rule: Frequency Check (< 1 second)
        if recent_bids:
            last_bid = recent_bids[0]
            if str(last_bid.get('bidder_id')) == str(employee_id):
                last_ts = datetime.fromisoformat(str(last_bid['bid_timestamp']))
                if (datetime.utcnow() - last_ts).total_seconds() < 1:
                    raise BusinessException("Bid too frequent", code='BID_TOO_FREQUENT')'''

new_code = '''        # Rule: Frequency Check (< 1 second)
        if recent_bids:
            last_bid = recent_bids[0]
            if str(last_bid.get('bidder_id')) == str(employee_id):
                last_ts = datetime.fromisoformat(str(last_bid['bid_timestamp']))
                if (datetime.utcnow() - last_ts).total_seconds() < 1:
                    # Check if user is currently the highest bidder
                    highest_bidder = product.get('highest_bidder_id')
                    if str(highest_bidder) == str(employee_id):
                        raise BusinessException("出價太頻繁，你是目前最高出價者唷！", code='BID_TOO_FREQUENT')
                    else:
                        raise BusinessException("出價太頻繁，請稍後再試", code='BID_TOO_FREQUENT')'''

content = content.replace(old_code, new_code)

# Write back
with open('auctions/services.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully updated bid frequency check message")
