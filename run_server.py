import os
import sys
from waitress import serve
from auction_site.wsgi import application

def run():
    port = 80
    host = '0.0.0.0'
    
    print("----------------------------------------------------------------")
    print("Attempting to start Waitress server on Port 80...")
    print("----------------------------------------------------------------")
    
    try:
        print(f"Serving on http://{host}:{port}")
        print("Access via:")
        print("  http://localhost")
        print("  http://test-auction.kingsteel.com/")
        print("----------------------------------------------------------------")
        serve(application, host=host, port=port)
    except OSError as e:
        if hasattr(e, 'winerror') and e.winerror == 10013: # Access denied
            print("\n[WARNING] Could not bind to port 80 (Access Denied).")
            print("To use Port 80, you must run this script as Administrator.")
            print("\nFalling back to Port 8080...")
            port = 8080
            print(f"Serving on http://{host}:{port}")
            print(f"Access via: http://test-auction.kingsteel.com:{port}/")
            try:
                serve(application, host=host, port=port)
            except Exception as e2:
                print(f"[ERROR] Failed to start on port 8080: {e2}")
        else:
            print(f"\n[ERROR] An error occurred: {e}")

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    # Keep window open
    input("\nPress Enter to exit...")
