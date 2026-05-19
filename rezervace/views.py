from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
import calendar
from datetime import datetime, date, time, timedelta
import json
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth, TruncHour

from .models import Prostor, Rezervace, Profil, ResetHeslaKod
from .forms import (
    RezervaceForm, RegistraceForm, 
    ZapomenuteHesloForm, ZadatKodForm, 
    NoveHesloForm, ZmenaHeslaProfilForm
)
from django.contrib import messages
import random
import string
from django.conf import settings
from django.contrib.auth import update_session_auth_hash

def hlavni_stranka(request):
    return render(request, 'rezervace/hlavni_stranka.html')


def seznam_prostoru(request):
    prostory = Prostor.objects.all()
    return render(request, 'rezervace/seznam_prostoru.html', {'prostory': prostory})


# --- KROK 1: VÝBĚR TERMÍNU ---
def vytvorit_rezervaci_krok1(request):
    prostor_id = request.GET.get('prostor') or request.POST.get('prostor')
    if not prostor_id:
        return redirect('seznam_prostoru')

    vybrany_prostor = Prostor.objects.get(id=prostor_id)
    
    vybrane_datum_str = request.GET.get('datum') or request.POST.get('datum')
    vybrane_datum = None
    sloty = []

    if vybrane_datum_str:
        try:
            vybrane_datum = datetime.strptime(vybrane_datum_str, '%Y-%m-%d').date()
            rezervace_dnes = Rezervace.objects.filter(prostor=vybrany_prostor, zacatek__date=vybrane_datum)
            
            cas_start = datetime.combine(vybrane_datum, time(8, 0))
            cas_konec = datetime.combine(vybrane_datum, time(20, 0))
            krok = timedelta(minutes=30)
            
            aktualni = cas_start
            while aktualni < cas_konec:
                konec_slotu = aktualni + krok
                obsazeno = rezervace_dnes.filter(zacatek__lt=konec_slotu, konec__gt=aktualni).exists()
                sloty.append({
                    'cas_od': aktualni.strftime('%H:%M'),
                    'cas_do': konec_slotu.strftime('%H:%M'),
                    'obsazeno': obsazeno,
                    'hodnota': f"{aktualni.strftime('%H:%M')}-{konec_slotu.strftime('%H:%M')}"
                })
                aktualni = konec_slotu
        except ValueError:
            pass

    dnes = date.today()
    rok_str = request.GET.get('rok')
    mesic_str = request.GET.get('mesic')
    
    zobrazovany_rok = int(rok_str) if rok_str else (vybrane_datum.year if vybrane_datum else dnes.year)
    zobrazovany_mesic = int(mesic_str) if mesic_str else (vybrane_datum.month if vybrane_datum else dnes.month)

    dalsi_m = zobrazovany_mesic + 1 if zobrazovany_mesic < 12 else 1
    dalsi_r = zobrazovany_rok if zobrazovany_mesic < 12 else zobrazovany_rok + 1
    pred_m = zobrazovany_mesic - 1 if zobrazovany_mesic > 1 else 12
    pred_r = zobrazovany_rok if zobrazovany_mesic > 1 else zobrazovany_rok - 1

    cal = calendar.monthcalendar(zobrazovany_rok, zobrazovany_mesic)
    kalendar_data = []
    
    # Stáhneme všechny rezervace v daném měsíci, ať nezatěžujeme databázi
    rezervace_v_mesici = Rezervace.objects.filter(
        prostor=vybrany_prostor, zacatek__year=zobrazovany_rok, zacatek__month=zobrazovany_mesic
    )

    MAX_SLOTU = 24 # Od 8:00 do 20:00 po 30 minutách je přesně 24 slotů

    for tyden in cal:
        tyden_data = []
        for den in tyden:
            if den == 0:
                tyden_data.append({'den': 0, 'stav': 'prazdny'})
            else:
                aktualni_datum = date(zobrazovany_rok, zobrazovany_mesic, den)
                
                if aktualni_datum < dnes:
                    stav = 'minulost'
                else:
                    stav = 'volno'
                    rezervace_dnes = [r for r in rezervace_v_mesici if r.zacatek.date() == aktualni_datum]
                    obsazene_sloty = sum([
                        (r.konec - r.zacatek).total_seconds() / 1800 
                        for r in rezervace_dnes
                    ])
                    
                    if obsazene_sloty >= MAX_SLOTU:
                        stav = 'obsazeno'
                
                if vybrane_datum and vybrane_datum == aktualni_datum:
                    stav = 'vybrano'

                tyden_data.append({
                    'den': den,
                    'datum': aktualni_datum.strftime('%Y-%m-%d'),
                    'stav': stav
                })
        kalendar_data.append(tyden_data)

    mesice_nazvy = ['', 'Leden', 'Únor', 'Březen', 'Duben', 'Květen', 'Červen', 'Červenec', 'Srpen', 'Září', 'Říjen', 'Listopad', 'Prosinec']

    if request.method == 'POST' and vybrane_datum:
        vybrany_cas = request.POST.get('vybrany_cas')
        if vybrany_cas:
            cas_od_str, cas_do_str = vybrany_cas.split('-')
            zacatek_rezervace = datetime.combine(vybrane_datum, datetime.strptime(cas_od_str, '%H:%M').time())
            konec_rezervace = datetime.combine(vybrane_datum, datetime.strptime(cas_do_str, '%H:%M').time())

            request.session['rezervace_data'] = {
                'prostor_id': vybrany_prostor.id,
                'zacatek': zacatek_rezervace.isoformat(),
                'konec': konec_rezervace.isoformat()
            }
            return redirect('vytvorit_rezervaci_krok2')

    return render(request, 'rezervace/krok1.html', {
        'vybrany_prostor': vybrany_prostor,
        'vybrane_datum': vybrane_datum_str,
        'sloty': sloty,
        'kalendar_data': kalendar_data,
        'nazev_mesice': mesice_nazvy[zobrazovany_mesic],
        'zobrazovany_rok': zobrazovany_rok,
        'pred_m': pred_m, 'pred_r': pred_r,
        'dalsi_m': dalsi_m, 'dalsi_r': dalsi_r
    })

# --- KROK 2: OSOBNÍ ÚDAJE ---
def vytvorit_rezervaci_krok2(request):
    if 'rezervace_data' not in request.session:
        return redirect('vytvorit_rezervaci_krok1')

    # --- PŘEDVYPLNĚNÍ DAT (včetně telefonu z profilu) ---
    initial_data = {}
    if request.user.is_authenticated:
        profil, _ = Profil.objects.get_or_create(uzivatel=request.user)
        initial_data = {
            'jmeno': request.user.first_name,
            'prijmeni': request.user.last_name,
            'email': request.user.email,
            'telefon': profil.telefon,
        }

    if request.method == 'POST':
        form = RezervaceForm(request.POST, user=request.user)
        if form.is_valid():
            nova_rezervace = form.save(commit=False)
            
            session_data = request.session['rezervace_data']
            nova_rezervace.prostor = Prostor.objects.get(id=session_data['prostor_id'])
            nova_rezervace.zacatek = datetime.fromisoformat(session_data['zacatek'])
            nova_rezervace.konec = datetime.fromisoformat(session_data['konec'])

            # --- ULOŽENÍ TELEFONU A ÚČTU ---
            if request.user.is_authenticated:
                nova_rezervace.uzivatel = request.user
                
                profil, _ = Profil.objects.get_or_create(uzivatel=request.user)
                profil.telefon = nova_rezervace.telefon
                profil.save()
            else:
                heslo = form.cleaned_data.get('heslo')
                if heslo:
                    email = form.cleaned_data.get('email')
                    
                    novy_uzivatel = User.objects.create_user(
                        username=email, email=email, password=heslo,
                        first_name=nova_rezervace.jmeno, last_name=nova_rezervace.prijmeni
                    )
                    nova_rezervace.uzivatel = novy_uzivatel
                    
                    Profil.objects.create(uzivatel=novy_uzivatel, telefon=nova_rezervace.telefon)

            nova_rezervace.save()
            
            # --- ODESLÁNÍ E-MAILU OBČANOVI ---
            predmet = f"Potvrzení přijetí žádosti - {nova_rezervace.prostor.nazev}"
            zprava = (
                f"Dobrý den, {nova_rezervace.jmeno},\n\n"
                f"Vaše žádost o rezervaci prostoru {nova_rezervace.prostor.nazev} na termín "
                f"{nova_rezervace.zacatek.strftime('%d. %m. %Y (%H:%M)')} byla úspěšně přijata.\n\n"
                f"Aktuálně čeká na potvrzení obcí. O výsledku Vás budeme informovat dalším e-mailem.\n\n"
                f"S pozdravem,\nObec Návsí"
            )
            send_mail(
                subject=predmet,
                message=zprava,
                from_email=None, 
                recipient_list=[nova_rezervace.email],
                fail_silently=False,
            )

            del request.session['rezervace_data']
            messages.success(request, "Vaše rezervace byla úspěšně vytvořena a čeká na schválení. O potvrzení budete informováni e-mailem.")
            return redirect('seznam_prostoru')
    else:
        form = RezervaceForm(initial=initial_data, user=request.user)

    return render(request, 'rezervace/krok2.html', {'form': form})


# --- REGISTRACE ---
def registrace(request):
    if request.method == 'POST':
        form = RegistraceForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['heslo'])
            user.save()
            
            Profil.objects.create(uzivatel=user, telefon=form.cleaned_data.get('telefon'))
            login(request, user)
            return redirect('seznam_prostoru')
    else:
        form = RegistraceForm()

    return render(request, 'rezervace/registrace.html', {'form': form})


# --- MŮJ PROFIL ---
@login_required
def muj_profil(request):
    profil, _ = Profil.objects.get_or_create(uzivatel=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('jmeno', '')
        request.user.last_name = request.POST.get('prijmeni', '')
        request.user.save()

        profil.telefon = request.POST.get('telefon', '')
        profil.save()

    moje_rezervace = Rezervace.objects.filter(uzivatel=request.user).order_by('-zacatek')

    return render(request, 'rezervace/muj_profil.html', {
        'profil': profil,
        'moje_rezervace': moje_rezervace
    })

# --- RESET A ZMENA HESLA ---

@login_required
def zmena_hesla_profil(request):
    if request.method == 'POST':
        form = ZmenaHeslaProfilForm(request.POST)
        if form.is_valid():
            user = request.user
            stare_heslo = form.cleaned_data['stare_heslo']
            nove_heslo = form.cleaned_data['nove_heslo']
            
            if not user.check_password(stare_heslo):
                messages.error(request, "Zadali jste chybné současné heslo.")
            else:
                user.set_password(nove_heslo)
                user.save()
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
                    messages.warning(request, f"(Testovací režim) Váš kód je: {kod}")
                
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


# --- SPRÁVCOVSKÝ PANEL (Jen pro zaměstnance obce) ---
@staff_member_required
def sprava_rezervaci(request):
    if request.method == 'POST':
        rezervace_id = request.POST.get('rezervace_id')
        akce = request.POST.get('akce')
        
        if rezervace_id and akce:
            rezervace = Rezervace.objects.get(id=rezervace_id)
            if akce == 'schvalit':
                rezervace.schvaleno = True
                rezervace.save()
                
                # --- ODESLÁNÍ E-MAILU O SCHVÁLENÍ ---
                predmet = f"Schválení rezervace - {rezervace.prostor.nazev}"
                zprava = (
                    f"Dobrý den, {rezervace.jmeno},\n\n"
                    f"s radostí Vám oznamujeme, že Vaše rezervace prostoru {rezervace.prostor.nazev} "
                    f"na termín {rezervace.zacatek.strftime('%d. %m. %Y (%H:%M)')} byla SCHVÁLENA.\n\n"
                    f"Těšíme se na Vás!\n\n"
                    f"S pozdravem,\nObec Návsí"
                )
                send_mail(
                    subject=predmet,
                    message=zprava,
                    from_email=None,
                    recipient_list=[rezervace.email],
                    fail_silently=False,
                )
                
            elif akce == 'smazat':
                rezervace.delete()
            return redirect('sprava_rezervaci')

    cekajici_rezervace = Rezervace.objects.filter(schvaleno=False).order_by('zacatek')
    historie_rezervaci = Rezervace.objects.filter(schvaleno=True).order_by('-zacatek')[:20] 

    return render(request, 'rezervace/sprava.html', {
        'cekajici': cekajici_rezervace,
        'historie': historie_rezervaci
    })

@staff_member_required
def grafy_rezervaci(request):
    nyni = timezone.now()
    
    # Poslední den (po hodinách)
    vcera = nyni - timedelta(days=1)
    rezervace_den = (
        Rezervace.objects.filter(zacatek__gte=vcera)
        .annotate(hodina=TruncHour('zacatek'))
        .values('hodina')
        .annotate(pocet=Count('id'))
        .order_by('hodina')
    )
    graf_den = {
        'labels': [r['hodina'].strftime('%H:00') if r['hodina'] else '' for r in rezervace_den],
        'data': [r['pocet'] for r in rezervace_den]
    }
    
    # Poslední týden (po dnech)
    tyden = nyni - timedelta(days=7)
    rezervace_tyden = (
        Rezervace.objects.filter(zacatek__gte=tyden)
        .annotate(den=TruncDate('zacatek'))
        .values('den')
        .annotate(pocet=Count('id'))
        .order_by('den')
    )
    graf_tyden = {
        'labels': [r['den'].strftime('%d.%m.') if r['den'] else '' for r in rezervace_tyden],
        'data': [r['pocet'] for r in rezervace_tyden]
    }
    
    # Poslední měsíc (po dnech)
    mesic = nyni - timedelta(days=30)
    rezervace_mesic = (
        Rezervace.objects.filter(zacatek__gte=mesic)
        .annotate(den=TruncDate('zacatek'))
        .values('den')
        .annotate(pocet=Count('id'))
        .order_by('den')
    )
    graf_mesic = {
        'labels': [r['den'].strftime('%d.%m.') if r['den'] else '' for r in rezervace_mesic],
        'data': [r['pocet'] for r in rezervace_mesic]
    }
    
    # Poslední rok (po měsících)
    rok = nyni - timedelta(days=365)
    rezervace_rok = (
        Rezervace.objects.filter(zacatek__gte=rok)
        .annotate(mesic=TruncMonth('zacatek'))
        .values('mesic')
        .annotate(pocet=Count('id'))
        .order_by('mesic')
    )
    graf_rok = {
        'labels': [r['mesic'].strftime('%m/%Y') if r['mesic'] else '' for r in rezervace_rok],
        'data': [r['pocet'] for r in rezervace_rok]
    }
    
    return render(request, 'rezervace/grafy.html', {
        'graf_den': json.dumps(graf_den),
        'graf_tyden': json.dumps(graf_tyden),
        'graf_mesic': json.dumps(graf_mesic),
        'graf_rok': json.dumps(graf_rok),
    })