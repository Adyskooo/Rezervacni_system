from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Tento nový řádek zprovozní adresy jako /ucet/login/ a /ucet/logout/
    path('ucet/', include('django.contrib.auth.urls')), 
    path('', include('rezervace.urls')), 
]