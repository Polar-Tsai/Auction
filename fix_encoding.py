import sys

# Read the file with error handling
try:
    # Try reading with different encodings
    encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'gbk', 'big5']
    
    for enc in encodings:
        try:
            with open('templates/products.html', 'r', encoding=enc) as f:
                content = f.read()
            print(f"Successfully read with encoding: {enc}")
            
            # Write back as UTF-8
            with open('templates/products.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("File saved as UTF-8")
            break
        except UnicodeDecodeError:
            continue
    else:
        print("All encodings failed, trying binary mode...")
        with open('templates/products.html', 'rb') as f:
            data = f.read()
        
        # Find and replace problematic byte
        print(f"Byte at position 978: {hex(data[978])}")
        # Replace 0xa8 with space or appropriate character
        data = data.replace(b'\xa8', b' ')
        
        # Try to decode
        content = data.decode('utf-8', errors='replace')
        
        with open('templates/products.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("File fixed and saved as UTF-8")
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
