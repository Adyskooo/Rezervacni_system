import os

files_to_fix = [
    'rezervace/templates/rezervace/base.html',
    'rezervace/templates/rezervace/hlavni_stranka.html'
]

for file in files_to_fix:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix CSS url() that use relative paths
    content = content.replace("url('/data/", "url('https://www.navsi.cz/data/")
    content = content.replace('url("/data/', 'url("https://www.navsi.cz/data/')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Fixed URLs")
