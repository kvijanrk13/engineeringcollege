# fix_emojis.py
with open('dashboard/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('❌', '[X]')
content = content.replace('✔', '[OK]')
content = content.replace('✅', '[OK]')
content = content.replace('⚠', '[WARNING]')

with open('dashboard/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed all emoji characters')