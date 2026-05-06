from bs4 import BeautifulSoup
import re

with open('navsi_rezervace_1.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Fix URLs to be absolute
for tag in soup.find_all(href=re.compile('^/')):
    tag['href'] = 'https://www.navsi.cz' + tag['href']
for tag in soup.find_all(src=re.compile('^/')):
    tag['src'] = 'https://www.navsi.cz' + tag['src']

# Remove their original rezervace scripts to avoid conflicts
for script in soup.find_all('script'):
    if script.get('src') and ('rezervace.js' in script.get('src') or 'check_form' in script.get('src')):
        script.decompose()

# Find the gcm-main
main_div = soup.find('div', class_='gcm-main')

messages_html = """
{% if messages %}
    <div class="mt-3">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Zavřít"></button>
            </div>
        {% endfor %}
    </div>
{% endif %}
"""

# Replace the content of gcm-main with django blocks
if main_div:
    main_div.clear()
    main_div.append(BeautifulSoup(messages_html + "{% block content %}{% endblock %}", 'html.parser'))

# Fix the navigation breadcrumb for rezervace
nav_active = soup.find('li', class_='breadcrumb-item active')
if nav_active:
    nav_active.string = "Rezervační systém"

header_top = soup.find('div', class_='gcm-header__right--top')
django_nav_html = """
    <div class="gcm-infobar__ico d-flex align-items-center ms-3" style="gap: 5px;">
        {% if user.is_authenticated %}
            {% if user.is_staff %}
                <a href="{% url 'sprava_rezervaci' %}" class="btn btn-warning btn-sm fw-bold me-2" style="font-size: 0.8rem; padding: 0.2rem 0.5rem; color: #000; text-decoration: none;">
                    Panel obce
                </a>
            {% endif %}
            <a href="{% url 'muj_profil' %}" class="btn btn-outline-dark btn-sm me-2" style="font-size: 0.8rem; padding: 0.2rem 0.5rem; text-decoration: none;" title="Přejít na nastavení profilu">
                👤 {{ user.first_name|default:"Můj profil" }}
            </a>
            <form method="post" action="{% url 'logout' %}" class="m-0 d-inline">
                {% csrf_token %}
                <button type="submit" class="btn btn-outline-dark btn-sm" style="font-size: 0.8rem; padding: 0.2rem 0.5rem;">Odhlásit se</button>
            </form>
        {% else %}
            <a href="{% url 'login' %}" class="btn btn-outline-dark btn-sm me-2" style="font-size: 0.8rem; padding: 0.2rem 0.5rem; text-decoration: none;">Přihlásit se</a>
            <a href="{% url 'registrace' %}" class="btn btn-success btn-sm text-white fw-bold" style="font-size: 0.8rem; padding: 0.2rem 0.5rem; text-decoration: none;">Registrovat se</a>
        {% endif %}
    </div>
"""
if header_top:
    header_top.append(BeautifulSoup(django_nav_html, 'html.parser'))

# Also make sure we have bootstrap JS loaded for the messages to be dismissible
body = soup.find('body')
if body:
    body.append(BeautifulSoup('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>', 'html.parser'))
    # Include some global styles for the django components so they fit Návsí design better
    css_fix = """
    <style>
        /* Bootstrap reset overrides if Návsí CSS conflicts */
        .gcm-main .btn { font-size: 1rem; }
        .gcm-main h1, .gcm-main h2 { color: #154b2a; } /* Návsí green */
        .gcm-main .card { border-radius: 0.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .alert { padding: 1rem; border-radius: 0.25rem; margin-bottom: 1rem; }
        .alert-success { background-color: #d4edda; border-color: #c3e6cb; color: #155724; }
        .alert-dismissible { padding-right: 4rem; position: relative; }
        .btn-close { position: absolute; right: 0; top: 0; padding: 1.25rem 1rem; background: transparent; border: 0; cursor: pointer; }
    </style>
    """
    body.append(BeautifulSoup(css_fix, 'html.parser'))

with open('rezervace/templates/rezervace/base.html', 'w', encoding='utf-8') as f:
    f.write("{% load static %}\n" + str(soup))

# Now for Návsí homepage
with open('navsi_home_1.html', 'r', encoding='utf-8') as f:
    home_html = f.read()

home_soup = BeautifulSoup(home_html, 'html.parser')
for tag in home_soup.find_all(href=re.compile('^/')):
    tag['href'] = 'https://www.navsi.cz' + tag['href']
for tag in home_soup.find_all(src=re.compile('^/')):
    tag['src'] = 'https://www.navsi.cz' + tag['src']

home_header_top = home_soup.find('div', class_='gcm-header__right--top')
if home_header_top:
    home_header_top.append(BeautifulSoup(django_nav_html, 'html.parser'))

# In home page, we want a link to the reservation system where the original reservation system is linked
# Looking for https://www.navsi.cz/prakticke-informace/rezervacni-system/
for a in home_soup.find_all('a', href='https://www.navsi.cz/prakticke-informace/rezervacni-system/'):
    a['href'] = "{% url 'seznam_prostoru' %}"

with open('rezervace/templates/rezervace/hlavni_stranka.html', 'w', encoding='utf-8') as f:
    f.write("{% load static %}\n" + str(home_soup))
