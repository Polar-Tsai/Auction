import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")
try:
    import common
    print("Import common: SUCCESS")
    from common.exceptions import BusinessException
    print("Import common.exceptions: SUCCESS")
    
    import auctions.services
    print("Import auctions.services: SUCCESS")
    
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Error: {e}")
