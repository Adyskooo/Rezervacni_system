from django import forms
from django.contrib.auth.models import User
from .models import Rezervace
import re
from django.core.exceptions import ValidationError

def validate_password_strength(value):
    if len(value) < 8:
        raise ValidationError("Heslo musí mít alespoň 8 znaků.")
    if not re.search(r'[A-Z]', value):
        raise ValidationError("Heslo musí obsahovat alespoň jedno velké písmeno.")
    if not re.search(r'[a-z]', value):
        raise ValidationError("Heslo musí obsahovat alespoň jedno malé písmeno.")
    if not re.search(r'[0-9]', value):
        raise ValidationError("Heslo musí obsahovat alespoň jednu číslici.")

# --- FORMULÁŘ PRO KROK 2 (DOKONČENÍ REZERVACE) ---
class RezervaceForm(forms.ModelForm):
    heslo = forms.CharField(
        label="Heslo (vyplňte pro vytvoření účtu)", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), 
        required=False,
        validators=[validate_password_strength]
    )

    class Meta:
        model = Rezervace
        fields = ['jmeno', 'prijmeni', 'email', 'telefon']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields.pop('heslo', None)
            
            self.fields['jmeno'].initial = user.first_name
            self.fields['prijmeni'].initial = user.last_name
            self.fields['email'].initial = user.email
            
            if hasattr(user, 'profil') and user.profil.telefon:
                self.fields['telefon'].initial = user.profil.telefon

    def clean(self):
        cleaned_data = super().clean()
        heslo = cleaned_data.get("heslo")
        email = cleaned_data.get("email")

        if heslo and User.objects.filter(email=email).exists():
            self.add_error('email', "Uživatel s tímto e-mailem již existuje.")
        
        return cleaned_data


# --- FORMULÁŘ PRO REGISTRACI (z předchozích fází) ---
class RegistraceForm(forms.ModelForm):
    heslo = forms.CharField(
        label="Heslo", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        validators=[validate_password_strength]
    )
    heslo_potvrzeni = forms.CharField(
        label="Potvrzení hesla", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )
    telefon = forms.CharField(label="Telefon", max_length=20, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Jméno',
            'last_name': 'Příjmení',
            'email': 'E-mail',
        }

    def clean(self):
        cleaned_data = super().clean()
        heslo = cleaned_data.get("heslo")
        heslo_potvrzeni = cleaned_data.get("heslo_potvrzeni")
        email = cleaned_data.get("email")

        if heslo != heslo_potvrzeni:
            self.add_error('heslo_potvrzeni', "Hesla se neshodují.")
        
        if User.objects.filter(email=email).exists():
            self.add_error('email', "Uživatel s tímto e-mailem již existuje.")
            
        return cleaned_data

class ZapomenuteHesloForm(forms.Form):
    email = forms.EmailField(
        label="Váš e-mail",
        widget=forms.EmailInput(attrs={'autocomplete': 'off'})
    )

class ZadatKodForm(forms.Form):
    kod = forms.CharField(label="Ověřovací kód (6 znaků)", max_length=6)

class NoveHesloForm(forms.Form):
    nove_heslo = forms.CharField(
        label="Nové heslo", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        validators=[validate_password_strength]
    )
    potvrzeni_hesla = forms.CharField(
        label="Potvrzení nového hesla", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        heslo = cleaned_data.get("nove_heslo")
        potvrzeni = cleaned_data.get("potvrzeni_hesla")

        if heslo != potvrzeni:
            self.add_error('potvrzeni_hesla', "Hesla se neshodují.")
        return cleaned_data

class ZmenaHeslaProfilForm(forms.Form):
    stare_heslo = forms.CharField(
        label="Současné heslo", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )
    nove_heslo = forms.CharField(
        label="Nové heslo", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        validators=[validate_password_strength]
    )
    potvrzeni_hesla = forms.CharField(
        label="Potvrzení nového hesla", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        heslo = cleaned_data.get("nove_heslo")
        potvrzeni = cleaned_data.get("potvrzeni_hesla")

        if heslo != potvrzeni:
            self.add_error('potvrzeni_hesla', "Hesla se neshodují.")
        return cleaned_data