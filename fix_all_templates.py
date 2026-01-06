import os
import shutil

# List of template files to fix
template_files = [
    'templates/products.html',
    'templates/login.html', 
    'templates/product_detail.html',
    'templates/base.html'
]

for filepath in template_files:
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} - not found")
        continue
    
    print(f"Processing {filepath}...")
    
    # Backup original
    shutil.copy(filepath, filepath + '.backup')
    
    # Try to read with CP950 (Traditional Chinese Windows encoding)
    try:
        with open(filepath, 'r', encoding='cp950') as f:
            content = f.read()
        print(f"  Read successfully with cp950")
        
        # Write as UTF-8
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Saved as UTF-8")
        
    except Exception as e:
        print(f"  Error with cp950: {e}")
        
        # Try UTF-8 with BOM
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            print(f"  Read successfully with utf-8-sig")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Saved as UTF-8")
            
        except Exception as e2:
            print(f"  Error with utf-8-sig: {e2}")
            # Restore from backup
            shutil.copy(filepath + '.backup', filepath)
            print(f"  Restored from backup")

print("\nDone!")
