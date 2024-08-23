from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse  # Import the messages module
from .models import Empleado
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
import logging
from django.urls import reverse
from django.contrib.auth import logout
import pandas as pd
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db import connection
from django.views.decorators.csrf import csrf_protect

logger = logging.getLogger(__name__)


def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Realiza la consulta manual a la base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM esquema WHERE username = %s AND password = %s", [username, password])
            user = cursor.fetchone()

        if user:
            # Si la autenticación es exitosa, establece la sesión como autenticada
            request.session['user_authenticated'] = True
            request.session['user_id'] = user[0]  # Por ejemplo, almacena el ID del usuario

            # Añade un mensaje de éxito
            messages.success(request, "Inicio de sesión exitoso. ¡Bienvenido de nuevo!")

            return redirect(reverse('home'))
        else:
            # Si la autenticación falla, añade un mensaje de error
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")

            return redirect(reverse('index'))

    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

def logout(request):
    # Limpia la sesión
    request.session.flush()  # Elimina todos los datos de la sesión
    return redirect(reverse('index'))

def listar_empleados(request):
    empleados = Empleado.objects.all()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        empleados_list = list(empleados.values())
        return JsonResponse(empleados_list, safe=False)
    return render(request, 'index.html', {'empleados': empleados})


@csrf_exempt
def agregar_empleado(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plataforma = data.get('plataforma')
        pagina = data.get('pagina')
        usuario = data.get('usuario')
        contraseña = data.get('contraseña')
        empleado = Empleado(plataforma=plataforma, pagina=pagina, usuario=usuario, contraseña=contraseña)
        empleado.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def editar_empleado(request, usuario):
    logger.debug(f"Editar empleado con usuario: {usuario}")
    if request.method == 'PATCH':  # Usando PATCH para editar
        try:
            empleado = Empleado.objects.get(usuario=usuario)
        except Empleado.DoesNotExist:
            logger.error(f"Empleado no encontrado: {usuario}")
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)

        data = json.loads(request.body)
        plataforma = data.get('plataforma', None)
        pagina = data.get('pagina', None)
        nuevo_usuario = data.get('usuario', None)  # Para actualizar el usuario
        contraseña = data.get('contraseña', None)

        # Actualiza los campos si están presentes en los datos enviados
        if plataforma:
            empleado.plataforma = plataforma
        if pagina:
            empleado.pagina = pagina
        if nuevo_usuario:
            empleado.usuario = nuevo_usuario
        if contraseña:
            empleado.contraseña = contraseña

        empleado.save()
        logger.debug(f"Empleado actualizado: {usuario}")
        return JsonResponse({'mensaje': 'Empleado actualizado'}, status=200)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def eliminar_empleado(request, usuario):
    if request.method == "POST":
        empleados = Empleado.objects.filter(usuario=usuario)
        if empleados.exists():
            count, _ = empleados.delete()  # Elimina todos los registros encontrados
            return JsonResponse({'status': 'success', 'message': f'{count} empleados eliminados'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Empleado no encontrado'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@csrf_exempt   
def export_excel(request):
    empleados = Empleado.objects.all()
    data = []

    for empleado in empleados:
        data.append({
            'Plataforma': empleado.plataforma,
            'Página': empleado.pagina,
            'Usuario': empleado.usuario,
            'Contraseña': empleado.contraseña,  # O enmascarar si es necesario
        })

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
    df.to_excel(response, index=False)

    return response

def buscar_empleado(request):
    query = request.GET.get('query', '')
    
    # Realiza una búsqueda en las columnas 'plataforma', 'pagina' y 'usuario'
    empleados = Empleado.objects.filter(
        plataforma__icontains=query
    ) | Empleado.objects.filter(
        pagina__icontains=query
    ) | Empleado.objects.filter(
        usuario__icontains=query
    )
    
    empleados_data = [{
        "plataforma": emp.plataforma,
        "pagina": emp.pagina,
        "usuario": emp.usuario,
        "contraseña": emp.contraseña,
    } for emp in empleados]
    
    return JsonResponse(empleados_data, safe=False)


def import_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES['excel-file']

        # Verificar que el archivo subido es un archivo de Excel
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'Por favor sube un archivo de Excel válido.')
            return redirect('index')  # Cambia 'index' al nombre correcto

        # Leer el archivo Excel
        try:
            df = pd.read_excel(excel_file)

            # Verificar que el archivo tiene las columnas requeridas
            required_columns = ['Plataforma', 'Página', 'Usuario', 'Contraseña']
            for column in required_columns:
                if column not in df.columns:
                    messages.error(request, f'La columna {column} no está presente en el archivo.')
                    return redirect('index')  # Cambia 'index' al nombre correcto

            # Guardar los datos en la base de datos
            for index, row in df.iterrows():
                Empleado.objects.create(
                    plataforma=row['Plataforma'],
                    pagina=row['Página'],
                    usuario=row['Usuario'],
                    contraseña=row['Contraseña']
                )

            messages.success(request, 'Datos importados y guardados correctamente.')
            return redirect('index')  # Cambia 'index' al nombre correcto

        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {str(e)}')
            return redirect('index')  # Cambia 'index' al nombre correcto

    return HttpResponse('Método no permitido', status=405)