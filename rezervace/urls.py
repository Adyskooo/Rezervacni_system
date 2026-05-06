from django.urls import path
from . import views

urlpatterns = [
    path('', views.hlavni_stranka, name='hlavni_stranka'), 
    
    path('rezervace/', views.seznam_prostoru, name='seznam_prostoru'),
    path('rezervace/krok-1/', views.vytvorit_rezervaci_krok1, name='vytvorit_rezervaci_krok1'),
    path('rezervace/krok-2/', views.vytvorit_rezervaci_krok2, name='vytvorit_rezervaci_krok2'),
    
    path('ucet/profil/', views.muj_profil, name='muj_profil'),
    path('registrace/', views.registrace, name='registrace'), 
    path('sprava/', views.sprava_rezervaci, name='sprava_rezervaci'),
    path('sprava/grafy/', views.grafy_rezervaci, name='grafy_rezervaci'),

    path("zmena-hesla-profil/", views.zmena_hesla_profil, name="zmena_hesla_profil"),
    path("zapomenute-heslo/", views.zapomenute_heslo, name="zapomenute_heslo"),
    path("zadat-kod/", views.zadat_kod, name="zadat_kod"),
    path("nove-heslo/", views.nove_heslo, name="nove_heslo"),
]