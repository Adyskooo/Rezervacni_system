import os

urls_path = 'rezervace/urls.py'
with open(urls_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'zapomenute_heslo' not in content:
    content = content.replace(']', '''
    path("zmena-hesla-profil/", views.zmena_hesla_profil, name="zmena_hesla_profil"),
    path("zapomenute-heslo/", views.zapomenute_heslo, name="zapomenute_heslo"),
    path("zadat-kod/", views.zadat_kod, name="zadat_kod"),
    path("nove-heslo/", views.nove_heslo, name="nove_heslo"),
]''')
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(content)
print("Updated URLs")
