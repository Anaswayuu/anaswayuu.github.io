from django.urls import path
from . import views
from .views import buscar_empleado


urlpatterns = [
    path('', views.index, name='index'),
    path('listar/', views.listar_empleados, name='listar_empleados'),
    path('home/', views.home, name='home_empleados'),  # Apuntar a la vista 'home'
    path('agregar/', views.agregar_empleado, name='agregar_empleado'),
    path('editar/<str:usuario>/', views.editar_empleado, name='editar_empleado'),
    path('buscar/', views.buscar_empleado, name='buscar_empleado'),
    path('eliminar/<str:usuario>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('export_excel/', views.export_excel, name='export_excel'),
    path('logout/', views.logout, name='logout'),
]
