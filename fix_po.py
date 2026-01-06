import re

# Fix zh_Hant django.po
with open(r'locale\zh_Hant\LC_MESSAGES\django.po', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the corrupted section
content = re.sub(r'# New translations for password and bidding features.*', '', content, flags=re.DOTALL)

# Add correct translations
new_translations = '''
# New translations for password and bidding features
msgid "密碼"
msgstr "密碼"

msgid "出生月日四位數，例如：0315"
msgstr "出生月日四位數，例如：0315"

msgid "請輸入出生月日，格式：MMDD"
msgstr "請輸入出生月日，格式：MMDD"

msgid "登入"
msgstr "登入"

msgid "您目前以工號"
msgstr "您目前以工號"

msgid "登入，請確認是您本人操作。冒用他人工號將違反遊戲規定。"
msgstr "登入，請確認是您本人操作。冒用他人工號將違反遊戲規定。"

msgid "當前登入"
msgstr "當前登入"

msgid "當前價格"
msgstr "當前價格"

msgid "下次出價"
msgstr "下次出價"

msgid "每次出價增量為底價的 1/10"
msgstr "每次出價增量為底價的 1/10"

msgid "無法出價"
msgstr "無法出價"
'''

with open(r'locale\zh_Hant\LC_MESSAGES\django.po', 'w', encoding='utf-8') as f:
    f.write(content.rstrip() + new_translations)

print("zh_Hant django.po fixed")

# Fix id django.po
with open(r'locale\id\LC_MESSAGES\django.po', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'# New translations for password and bidding features.*', '', content, flags=re.DOTALL)

new_translations_id = '''
# New translations for password and bidding features
msgid "密碼"
msgstr "Kata Sandi"

msgid "出生月日四位數，例如：0315"
msgstr "Tanggal lahir 4 digit, contoh: 0315"

msgid "請輸入出生月日，格式：MMDD"
msgstr "Masukkan tanggal lahir dengan format MMDD"

msgid "登入"
msgstr "Masuk"

msgid "您目前以工號"
msgstr "Anda saat ini login dengan ID"

msgid "登入，請確認是您本人操作。冒用他人工號將違反遊戲規定。"
msgstr "silakan pastikan ini adalah Anda. Penyalahgunaan ID orang lain akan melanggar aturan permainan."

msgid "當前登入"
msgstr "Login Saat Ini"

msgid "當前價格"
msgstr "Harga Saat Ini"

msgid "下次出價"
msgstr "Penawaran Berikutnya"

msgid "每次出價增量為底價的 1/10"
msgstr "Setiap penawaran bertambah 1/10 dari harga dasar"

msgid "無法出價"
msgstr "Tidak dapat menawar"
'''

with open(r'locale\id\LC_MESSAGES\django.po', 'w', encoding='utf-8') as f:
    f.write(content.rstrip() + new_translations_id)

print("id django.po fixed")
