"""
Manual .mo file compilation using msgfmt tool directly
This script finds and uses the msgfmt executable to compile .po files
"""
import subprocess
import sys
from pathlib import Path

def find_msgfmt():
    """Try to find msgfmt executable"""
    possible_paths = [
        Path(r"C:\Program Files\gettext-iconv\bin\msgfmt.exe"),
        Path(r"C:\Program Files (x86)\gettext-iconv\bin\msgfmt.exe"),
        Path(r"C:\gettext\bin\msgfmt.exe"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Try to find via where command
    try:
        result = subprocess.run(['where', 'msgfmt'], capture_output=True, text=True)
        if result.returncode == 0:
            return Path(result.stdout.strip().split('\n')[0])
    except:
        pass
    
    return None

def compile_with_msgfmt(msgfmt_path, po_file, mo_file):
    """Compile .po to .mo using msgfmt"""
    try:
        result = subprocess.run(
            [str(msgfmt_path), '-o', str(mo_file), str(po_file)],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    BASE_DIR = Path(__file__).resolve().parent
    
    # Find msgfmt
    msgfmt_path = find_msgfmt()
    
    if not msgfmt_path:
        print("❌ 找不到 msgfmt 工具")
        print("\n請確認：")
        print("1. gettext 已正確安裝")
        print("2. 安裝時有勾選 'Add to PATH'")
        print("3. 已重新開啟 PowerShell 視窗")
        print("\n或者手動指定 msgfmt.exe 的位置")
        sys.exit(1)
    
    print(f"✓ 找到 msgfmt: {msgfmt_path}\n")
    
    locales = [
        ('zh_Hant', '繁體中文'),
        ('id', 'Bahasa Indonesia'),
    ]
    
    success_count = 0
    for locale_code, locale_name in locales:
        po_file = BASE_DIR / 'locale' / locale_code / 'LC_MESSAGES' / 'django.po'
        mo_file = BASE_DIR / 'locale' / locale_code / 'LC_MESSAGES' / 'django.mo'
        
        if po_file.exists():
            print(f"編譯 {locale_name} ({locale_code})...", end=' ')
            success, output = compile_with_msgfmt(msgfmt_path, po_file, mo_file)
            
            if success:
                print(f"✓ 成功")
                success_count += 1
            else:
                print(f"✗ 失敗")
                print(f"  錯誤: {output}")
        else:
            print(f"✗ 找不到 PO 檔案: {po_file}")
    
    if success_count > 0:
        print(f"\n✓ 成功編譯 {success_count} 個語言檔案！")
        print("\n現在可以啟動伺服器：")
        print("  python run_server.py")
    else:
        print("\n✗ 沒有成功編譯任何檔案")
