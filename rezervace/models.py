from django.db import models
from django.contrib.auth.models import User


# --- NOVÝ MODEL PROFILU ---
class Profil(models.Model):
    uzivatel = models.OneToOneField(User, on_delete=models.CASCADE)
    telefon = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon")

    def __str__(self):
        return f"Profil uživatele {self.uzivatel.username}"


class ResetHeslaKod(models.Model):
    uzivatel = models.ForeignKey(User, on_delete=models.CASCADE)
    kod = models.CharField(max_length=6)
    vytvoreno = models.DateTimeField(auto_now_add=True)
    pouzito = models.BooleanField(default=False)

    def platnost_vyprsela(self):
        from django.utils import timezone
        import datetime
        return timezone.now() > self.vytvoreno + datetime.timedelta(minutes=15)
        
    def __str__(self):
        return f"Kód pro {self.uzivatel.email}"


class Prostor(models.Model):
    nazev = models.CharField(max_length=100, verbose_name="Název prostoru")
    popis = models.TextField(blank=True, verbose_name="Popis")

    class Meta:
        verbose_name = "Prostor"
        verbose_name_plural = "Prostory"

    def __str__(self):
        return self.nazev


class Rezervace(models.Model):
    prostor = models.ForeignKey(Prostor, on_delete=models.CASCADE, verbose_name="Prostor")
    
    # Uživatel už je nepovinný
    uzivatel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Registrovaný uživatel")
    
    jmeno = models.CharField(max_length=50, verbose_name="Jméno")
    prijmeni = models.CharField(max_length=50, verbose_name="Příjmení")
    email = models.EmailField(verbose_name="E-mail")
    telefon = models.CharField(max_length=20, verbose_name="Telefon")
    
    zacatek = models.DateTimeField(verbose_name="Začátek rezervace")
    konec = models.DateTimeField(verbose_name="Konec rezervace")
    schvaleno = models.BooleanField(default=False, verbose_name="Schváleno obcí")

    class Meta:
        verbose_name = "Rezervace"
        verbose_name_plural = "Rezervace"

    def __str__(self):
        return f"{self.prostor} - {self.jmeno} {self.prijmeni} ({self.zacatek})"