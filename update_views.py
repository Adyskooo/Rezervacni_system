import os

views_path = 'rezervace/views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_views = """
# --- RESET A ZMENA HESLA ---
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from .models import ResetHeslaKod
from .forms import ZapomenuteHesloForm, ZadatKodForm, NoveHesloForm, ZmenaHeslaProfilForm

@login_required
def zmena_hesla_profil(request):
    if request.method == 'POST':
        form = ZmenaHeslaProfilForm(request.POST)
        if form.is_valid():
            user = request.user
            stare_heslo = form.cleaned_data['stare_heslo']
            nove_heslo = form.cleaned_data['nove_heslo']
            potvrzeni = form.cleaned_data['potvrzeni_hesla']
            
            if not user.check_password(stare_heslo):
                messages.error(request, "Zadali jste chybné současné heslo.")
            elif nove_heslo != potvrzeni:
                messages.error(request, "Nová hesla se neshodují.")
            elif len(nove_heslo) < 8:
                messages.error(request, "Nové heslo musí mít alespoň 8 znaků.")
            else:
                user.set_password(nove_heslo)
                user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                messages.success(request, "Vaše heslo bylo úspěšně změněno.")
                return redirect('muj_profil')
    else:
        form = ZmenaHeslaProfilForm()
    
    return render(request, 'rezervace/zmena_hesla_profil.html', {'form': form})

def zapomenute_heslo(request):
    if request.method == 'POST':
        form = ZapomenuteHesloForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                kod = ''.join(random.choices(string.digits, k=6))
                
                ResetHeslaKod.objects.filter(uzivatel=user, pouzito=False).update(pouzito=True)
                ResetHeslaKod.objects.create(uzivatel=user, kod=kod)
                
                try:
                    send_mail(
                        'Kód pro obnovení hesla',
                        f'Váš ověřovací kód pro obnovení hesla je: {kod}\nKód je platný 15 minut.',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Chyba při odesílání e-mailu: {e}")
                    # Pro lokální testování, pokud nefungují maily
                    messages.warning(request, f"(Lokální test) Váš kód je: {kod}")
                
                request.session['reset_email'] = email
                messages.success(request, "Ověřovací kód byl odeslán na Váš e-mail.")
                return redirect('zadat_kod')
            except User.DoesNotExist:
                messages.error(request, "Uživatel s tímto e-mailem nebyl nalezen.")
    else:
        form = ZapomenuteHesloForm()
    
    return render(request, 'rezervace/zapomenute_heslo.html', {'form': form})

def zadat_kod(request):
    if 'reset_email' not in request.session:
        return redirect('zapomenute_heslo')
        
    email = request.session['reset_email']
    
    if request.method == 'POST':
        form = ZadatKodForm(request.POST)
        if form.is_valid():
            kod = form.cleaned_data['kod']
            try:
                user = User.objects.get(email=email)
                reset_zaznam = ResetHeslaKod.objects.filter(uzivatel=user, kod=kod, pouzito=False).latest('vytvoreno')
                
                if reset_zaznam.platnost_vyprsela():
                    messages.error(request, "Platnost kódu vypršela. Vyžádejte si prosím nový.")
                    return redirect('zapomenute_heslo')
                
                reset_zaznam.pouzito = True
                reset_zaznam.save()
                
                request.session['kod_overen'] = True
                messages.success(request, "Kód byl úspěšně ověřen.")
                return redirect('nove_heslo')
                
            except (User.DoesNotExist, ResetHeslaKod.DoesNotExist):
                messages.error(request, "Neplatný kód.")
    else:
        form = ZadatKodForm()
        
    return render(request, 'rezervace/zadat_kod.html', {'form': form, 'email': email})

def nove_heslo(request):
    if 'reset_email' not in request.session or not request.session.get('kod_overen'):
        return redirect('zapomenute_heslo')
        
    if request.method == 'POST':
        form = NoveHesloForm(request.POST)
        if form.is_valid():
            nove_heslo = form.cleaned_data['nove_heslo']
            potvrzeni = form.cleaned_data['potvrzeni_hesla']
            
            if nove_heslo != potvrzeni:
                messages.error(request, "Hesla se neshodují.")
            elif len(nove_heslo) < 8:
                messages.error(request, "Heslo musí mít alespoň 8 znaků.")
            else:
                email = request.session['reset_email']
                user = User.objects.get(email=email)
                user.set_password(nove_heslo)
                user.save()
                
                del request.session['reset_email']
                del request.session['kod_overen']
                
                messages.success(request, "Vaše heslo bylo úspěšně změněno. Nyní se můžete přihlásit.")
                return redirect('login')
    else:
        form = NoveHesloForm()
        
    return render(request, 'rezervace/nove_heslo.html', {'form': form})
"""

if 'def zapomenute_heslo' not in content:
    with open(views_path, 'a', encoding='utf-8') as f:
        f.write(new_views)
print("Updated views")
