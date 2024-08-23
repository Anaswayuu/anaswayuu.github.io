from django.shortcuts import redirect
from django.urls import reverse

class CheckSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_paths = [
            reverse('listar_empleados'),
            reverse('home_empleados'),
            reverse('agregar_empleado'),
            reverse('editar_empleado', args=['dummy']),
            reverse('eliminar_empleado', args=['dummy']),
            reverse('export_excel'),
        ]

    def __call__(self, request):
        # Verifica si la sesión está autenticada y si la ruta es protegida
        if not request.session.get('user_authenticated', False):  # Comprueba si 'user_authenticated' es False o no está en la sesión
            if request.path in self.protected_paths:
                return redirect(reverse('index'))

        response = self.get_response(request)
        return response
