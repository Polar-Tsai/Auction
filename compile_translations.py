"""
Pure Python .po to .mo compiler with proper UTF-8 encoding support  
Includes metadata header for proper charset declaration
"""
import struct
import array
from pathlib import Path

def generate_mo_file(po_file, mo_file):
    """
    Compile a .po file to a .mo file using pure Python with UTF-8 support
    """
    # Parse .po file
    messages = {}
    current_msgid = []
    current_msgstr = []
    in_msgid = False
    in_msgstr = False
    
    with open(po_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('msgid "'):
                # Save previous entry
                if in_msgstr:
                    msgid = ''.join(current_msgid)
                    msgstr = ''.join(current_msgstr)
                    messages[msgid] = msgstr
                
                # Start new msgid
                current_msgid = [line[7:-1]]  # Remove 'msgid "' and '"'
                current_msgstr = []
                in_msgid = True
                in_msgstr = False
                
            elif line.startswith('msgstr "'):
                current_msgstr = [line[8:-1]]  # Remove 'msgstr "' and '"'
                in_msgid = False
                in_msgstr = True
                
            elif line.startswith('"') and line.endswith('"'):
                # Continuation line
                content = line[1:-1]
                if in_msgid:
                    current_msgid.append(content)
                elif in_msgstr:
                    current_msgstr.append(content)
        
        # Don't forget the last entry
        if in_msgstr:
            msgid = ''.join(current_msgid)
            msgstr = ''.join(current_msgstr)
            messages[msgid] = msgstr
    
    # Ensure we have the header with charset info
    if '' not in messages or 'Content-Type' not in messages.get('', ''):
        # Add a proper header
        messages[''] = (
            'Content-Type: text/plain; charset=UTF-8\\n'
            'Content-Transfer-Encoding: 8bit\\n'
        )
    
    # Build .mo file
    keys = sorted(messages.keys())
    offsets = []
    ids = b''
    strs = b''
    
    for key in keys:
        msg = messages[key]
        # Encode as UTF-8
        key_bytes = key.encode('utf-8')
        msg_bytes = msg.encode('utf-8')
        
        offsets.append((len(ids), len(key_bytes), len(strs), len(msg_bytes)))
        ids += key_bytes + b'\x00'
        strs += msg_bytes + b'\x00'
    
    # MO file format
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    
    # Build index tables
    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]
    
    # Build header
    magic = 0x950412de
    version = 0
    msgcount = len(keys)
    masteridx = 7 * 4
    transidx = masteridx + 8 * msgcount
    
    header = struct.pack(
        'Iiiiiii',
        magic,
        version,
        msgcount,
        masteridx,
        transidx,
        0,  # hash table size
        0   # hash table offset
    )
    
    # Write .mo file
    with open(mo_file, 'wb') as f:
        f.write(header)
        f.write(array.array('i', koffsets).tobytes())
        f.write(array.array('i', voffsets).tobytes())
        f.write(ids)
        f.write(strs)
    
    return len(keys) - 1  # Subtract 1 for the header entry

if __name__ == '__main__':
    BASE_DIR = Path(__file__).resolve().parent
    
    locales = [
        ('zh_Hant', '繁體中文'),
        ('id', 'Bahasa Indonesia'),
    ]
    
    success_count = 0
    for locale_code, locale_name in locales:
        po_file = BASE_DIR / 'locale' / locale_code / 'LC_MESSAGES' / 'django.po'
        mo_file = BASE_DIR / 'locale' / locale_code / 'LC_MESSAGES' / 'django.mo'
        
        if po_file.exists():
            try:
                msg_count = generate_mo_file(po_file, mo_file)
                print(f"✓ Compiled {locale_name} ({locale_code}): {msg_count} messages")
                print(f"  {po_file.name} -> {mo_file.name}")
                success_count += 1
            except Exception as e:
                print(f"✗ Failed to compile {locale_name}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"✗ PO file not found: {po_file}")
    
    if success_count > 0:
        print(f"\n✓ Successfully compiled {success_count} locale(s)!")
        print("\nYou can now run the server:")
        print("  python run_server.py")
    else:
        print("\n✗ No translations were compiled.")
