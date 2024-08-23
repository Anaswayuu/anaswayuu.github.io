from django.contrib import admin
from django.urls import path, include
from empleados import views as empleados_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('empleados/', include('empleados.urls')),
    path('', empleados_views.index, name='index'),
    path('home/', empleados_views.home, name='home'),
]