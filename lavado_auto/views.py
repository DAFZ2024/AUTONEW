import http.client
import json

from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from .models import Usuario,Comentario,MensajeQueja,Reserva,Servicio,Empresa,EmpresaServicio, ReservaServicio
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import ComentarioForm, ReservaForm, UsuariosForm,ComentarioClienteForm,QuejaForm,ServicioForm,EmpresaForm,ProfileUserForm
from datetime import datetime,timedelta
from django.utils import timezone
from functools import wraps

# Decorador personalizado para verificar autenticación y rol de admin
def admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        print(f"🔍 @admin_required verificando acceso a {function.__name__}")
        
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            print(f"❌ Usuario no autenticado")
            messages.error(request, 'Debes iniciar sesión como administrador para acceder a esta sección.')
            return redirect('logincrud')
        
        print(f"👤 Usuario autenticado: {request.user.nombre_usuario}")
        print(f"🎭 Rol del usuario: {getattr(request.user, 'rol', 'NO_ROL')}")
        
        # Verificar si el usuario es administrador
        if not hasattr(request.user, 'rol'):
            print(f"❌ Usuario no tiene atributo 'rol'")
            messages.error(request, 'Error: El usuario no tiene un rol asignado.')
            return redirect('logincrud')
            
        if request.user.rol != 'admin':
            print(f"❌ Rol incorrecto: {request.user.rol}")
            messages.error(request, f'Acceso denegado. Tu rol actual es "{request.user.rol}". Solo los administradores pueden acceder a esta sección.')
            return redirect('logincrud')
        
        print(f"✅ Acceso permitido para {request.user.nombre_usuario} a {function.__name__}")
        return function(request, *args, **kwargs)
    return wrap

# Create your views here.



def home(request):
    comentarios = Comentario.objects.all().order_by('-fecha')  # Recupera todos los comentarios
    return render(request, 'home.html', {'comentarios': comentarios})

def empresas(request):
    return render(request, 'empresas.html')

def login(request):
    # Si ya está logueado, redirigir al home
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        # REGISTRO DE USUARIO
        if 'nombre_completo' in request.POST:
            nombre_completo = request.POST['nombre_completo']
            nombre_usuario = request.POST['nombre_usuario']
            correo = request.POST['correo']
            telefono = request.POST.get('telefono')
            direccion = request.POST.get('direccion')
            contrasena1 = request.POST['contrasena1']
            contrasena2 = request.POST['contrasena2']
            
            # Validar que las contraseñas coincidan
            if contrasena1 != contrasena2:
                messages.error(request, "Las contraseñas no coinciden, intentalo de nuevo")
                return redirect('login')
            
            # Validar que el nombre de usuario no exista
            if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
                messages.error(request, "El nombre de usuario ya esta registrado, intenta con otro.")
                return redirect('login')
            
            # Validar que el correo no exista
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, "El correo ya esta registrado, intenta con otro.")
                return redirect('login')
            
            # Concatenar el prefijo "57" al teléfono
            telefono_completo = "57" + telefono
            
            # Crear el nuevo usuario
            nuevo_usuario = Usuario.objects.create_user(
                nombre_completo=nombre_completo,
                nombre_usuario=nombre_usuario,
                correo=correo,
                telefono=telefono_completo,
                direccion=direccion,
                password=contrasena1  # ✅ Usar 'password' no 'contrasena'
            )
            
            messages.success(request, "El usuario ha sido creado exitosamente. Ahora puedes iniciar sesión.")
            return redirect('login')
        
        # INICIO DE SESIÓN
        else:
            nombre_usuario = request.POST['nombre_usuario']
            contrasena = request.POST['contrasena']
            
            # Autenticar usuario
            usuario = authenticate(request, username=nombre_usuario, password=contrasena)
            
            if usuario is not None:
                auth_login(request, usuario)
                messages.success(request, f'Bienvenido de nuevo, {usuario.nombre_usuario}!')
                return redirect('home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
                return redirect('login')
    
    # GET: Mostrar la página de login/registro
    else:
        return render(request, 'login.html')
    

@login_required
def perfil_usuario(request):
    usuario = request.user  # Obtén el usuario actualmente autenticado
    form = ProfileUserForm(instance=usuario)  # Crea un formulario con los datos del usuario

    if request.method == 'POST':
        form = ProfileUserForm(request.POST, request.FILES, instance=usuario)  # Incluye el usuario existente

        if form.is_valid():
            # Manejar la actualización de la contraseña antes de guardar
            contrasena11 = request.POST.get('contrasena11', '').strip()
            contrasena22 = request.POST.get('contrasena22', '').strip()

            # Validar contraseñas si se proporcionan
            if contrasena11 or contrasena22:
                if not contrasena11 or not contrasena22:
                    messages.error(request, 'Debes completar ambos campos de contraseña.')
                    return render(request, 'perfil_usuario.html', {'usuario': usuario, 'form': form})
                
                if contrasena11 != contrasena22:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return render(request, 'perfil_usuario.html', {'usuario': usuario, 'form': form})
                
                if len(contrasena11) < 6:
                    messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
                    return render(request, 'perfil_usuario.html', {'usuario': usuario, 'form': form})

            # Guardar los datos del usuario
            usuario_actualizado = form.save()

            # Cambiar la contraseña si se proporcionó
            if contrasena11:
                usuario_actualizado.set_password(contrasena11)
                usuario_actualizado.save()
                messages.success(request, 'Perfil y contraseña actualizados correctamente.')
            else:
                messages.success(request, 'Perfil actualizado correctamente.')
            
            # Redirigir al perfil para mostrar la notificación
            return redirect('perfil')
        else:
            # Si el formulario no es válido, mostrar errores
            messages.error(request, 'Por favor corrige los errores en el formulario.')

    return render(request, 'perfil_usuario.html', {'usuario': usuario, 'form': form})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')



def nosotros(request):
    return render(request, 'nosotros.html')



def servicios(request):
    comentarios = Comentario.objects.all().order_by('-fecha')  # Recupera todos los comentarios
    return render(request, 'servicios.html', {'comentarios': comentarios})


def reservas(request):
    ahora = timezone.now()
    hoy = ahora.date()
    servicios = Servicio.objects.all()  # Obtener todos los servicios disponibles
    empresas = Empresa.objects.all()    # Obtener todas las empresas disponibles
    empresaservicio = EmpresaServicio.objects.all()
    
    fecha_seleccionada = None
    servicios_filtrados = []
    
    # Inicializar la variable 'ocupadas' antes de cualquier otra cosa.
    reservas_existentes = Reserva.objects.all()
    
    ocupadas = {
        "fechas": {reserva.fecha for reserva in reservas_existentes},
        "horas": {}
    }
    
    for reserva in reservas_existentes:
        if reserva.fecha not in ocupadas["horas"]:
            ocupadas["horas"][reserva.fecha] = set()
        ocupadas["horas"][reserva.fecha].add(reserva.hora.strftime('%H:%M'))
    
    if request.method == "POST":
        opcion_empresa_id = request.POST.get('id_empresa')
        fecha_seleccionada = request.POST.get('fecha')
        hora = request.POST.get('hora')
        usuario = request.user
        servicio_id = request.POST.get('id_servicio')
        
        try:
            servicio = Servicio.objects.get(id_servicio=servicio_id)
        except Servicio.DoesNotExist:
            messages.error(request, "El servicio seleccionado no existe.")
            return redirect('reservas')
        
        if opcion_empresa_id:
            try:
                empresa = Empresa.objects.get(id_empresa=opcion_empresa_id)
            except Empresa.DoesNotExist:
                messages.error(request, "El punto seleccionado no existe.")
                return redirect('reservas')
            
            # Filtrar los servicios disponibles para la empresa seleccionada
            servicios_filtrados = Servicio.objects.filter(
                id_servicio__in=EmpresaServicio.objects.filter(empresa=empresa).values('servicio')
            )
            
            if not servicios_filtrados:
                messages.error(request, "No hay servicios disponibles para la empresa seleccionada.")
                return redirect('reservas')
            
            # Verificar que el servicio seleccionado esté disponible para esta empresa
            if servicio not in servicios_filtrados:
                messages.error(request, "El servicio seleccionado no está disponible para esta empresa.")
                return redirect('reservas')
            
            # Verificar si la fecha y hora están ocupadas
            fecha_obj = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()
            if fecha_obj in ocupadas["fechas"] and hora in ocupadas["horas"].get(fecha_obj, set()):
                messages.error(request, f"Lo siento, la fecha {fecha_seleccionada} a las {hora} ya está ocupada.")
                return redirect('reservas')
            
            # Crear la reserva
            reserva = Reserva(
                empresa=empresa,
                fecha=fecha_seleccionada,
                hora=hora,
                usuario=usuario
            )
            reserva.save()
            
            # Crear la relación entre reserva y servicio
            ReservaServicio.objects.create(reserva=reserva, servicio=servicio)
            
            messages.success(request, f"Tu cita para {servicio.nombre_servicio} ha sido reservada para el {fecha_seleccionada} a las {hora}.")
            return redirect('reservas')
        else:
            messages.error(request, "No se ha seleccionado un punto.")
            return redirect('reservas')
    
    # Generar horas disponibles
    horas_disponibles = {}
    for i in range(15):
        fecha = hoy + timedelta(days=i)
        horas_disponibles[fecha] = []
        
        for h in range(8, 21):  # De 8:00 AM a 8:00 PM
            hora_formateada = f"{h:02}:00"
            
            if fecha == hoy and h < ahora.hour:
                continue
            
            # Verifica si la hora está ocupada para esta fecha
            if hora_formateada not in ocupadas["horas"].get(fecha, set()):
                horas_disponibles[fecha].append(hora_formateada)
    
    fechas_disponibles = [hoy + timedelta(days=i) for i in range(15)]
    
    return render(request, 'reservas.html', {
        'ocupadas': ocupadas,
        'horas_disponibles': horas_disponibles,
        'fechas_disponibles': fechas_disponibles,
        'hoy': hoy,
        'servicios_filtrados': servicios_filtrados,
        'empresas': empresas,
        'servicios': servicios,
        'empresaservicio': empresaservicio
    })

# Vista para obtener servicios por empresa (AJAX)
def obtener_servicios(request):
    empresa_id = request.GET.get('empresa_id')
    if empresa_id:
        try:
            empresa = Empresa.objects.get(id_empresa=empresa_id)
            servicios = Servicio.objects.filter(
                id_servicio__in=EmpresaServicio.objects.filter(empresa=empresa).values('servicio')
            )
            servicios_data = [
                {
                    'id_servicio': servicio.id_servicio,
                    'nombre_servicio': servicio.nombre_servicio,
                    'descripcion': servicio.descripcion,
                    'precio': servicio.precio
                } for servicio in servicios
            ]
            empresa_data = {
                'nombre_empresa': empresa.nombre_empresa,
                'direccion': empresa.direccion,
                'telefono': empresa.telefono
            }
            return JsonResponse({'servicios': servicios_data, 'empresa': empresa_data})
        except Empresa.DoesNotExist:
            return JsonResponse({'servicios': [], 'empresa': None})
    return JsonResponse({'servicios': [], 'empresa': None})

# Vista para obtener información de la empresa (AJAX)
def obtener_info_empresa(request):
    empresa_id = request.GET.get('empresa_id')
    if empresa_id:
        try:
            empresa = Empresa.objects.get(id_empresa=empresa_id)
            return JsonResponse({
                'nombre': empresa.nombre_empresa,
                'direccion': empresa.direccion,
                'telefono': empresa.telefono
            })
        except Empresa.DoesNotExist:
            return JsonResponse({
                'nombre': 'No disponible',
                'direccion': 'No disponible',
                'telefono': 'No disponible'
            })
    return JsonResponse({
        'nombre': 'No disponible',
        'direccion': 'No disponible',
        'telefono': 'No disponible'
    })

# Vista para obtener información del servicio (AJAX)
def obtener_info_servicio(request):
    servicio_id = request.GET.get('servicio_id')
    if servicio_id:
        try:
            servicio = Servicio.objects.get(id_servicio=servicio_id)
            return JsonResponse({
                'nombre_servicio': servicio.nombre_servicio,
                'descripcion': servicio.descripcion,
                'precio': servicio.precio
            })
        except Servicio.DoesNotExist:
            return JsonResponse({
                'nombre_servicio': 'Servicio no encontrado',
                'descripcion': 'No disponible',
                'precio': 0
            })
    return JsonResponse({
        'nombre_servicio': 'Selecciona un servicio',
        'descripcion': '',
        'precio': 0
    })

# Vista para obtener horas disponibles (AJAX)
def get_horas(request):
    empresa_id = request.GET.get('empresa_id')
    servicio_id = request.GET.get('servicio_id')
    fecha_str = request.GET.get('fecha')
    if empresa_id and servicio_id and fecha_str:
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            if fecha_obj < timezone.now().date():
                return JsonResponse({'horas': []})

            reservas_existentes = Reserva.objects.filter(
                empresa_id=empresa_id,
                fecha=fecha_obj
            )

            # Solo toma las reservas que tengan el servicio seleccionado
            reservas_con_servicio = []
            for reserva in reservas_existentes:
                if ReservaServicio.objects.filter(reserva=reserva, servicio_id=servicio_id).exists():
                    reservas_con_servicio.append(reserva)

            horas_ocupadas = set(reserva.hora.strftime('%H:%M') for reserva in reservas_con_servicio)

            horas_disponibles = []
            for h in range(8, 21):  # 8:00 a 20:00
                hora_formateada = f"{h:02}:00"
                if fecha_obj == timezone.now().date() and h < timezone.now().hour:
                    continue
                if hora_formateada not in horas_ocupadas:
                    horas_disponibles.append(hora_formateada)

            return JsonResponse({'horas': horas_disponibles})

        except ValueError:
            return JsonResponse({'horas': []})

    return JsonResponse({'horas': []})




def planes(request):
    return render(request, 'planes.html')


@login_required
def citas(request):
    ahora = datetime.now()
    hoy = ahora.date()
    
    # Obtener reservas del usuario actual with prefetch_related para optimizar
    reservas_no_completadas = Reserva.objects.filter(
        estado='no_completado', 
        usuario=request.user
    ).prefetch_related('servicios', 'empresa')
    
    reservas_completadas = Reserva.objects.filter(
        estado='completado', 
        usuario=request.user
    ).prefetch_related('servicios', 'empresa')
    
    servicios = Servicio.objects.all() 
    empresas = Empresa.objects.all()

    horas_disponibles = {}
    ocupadas = {
        "fechas": {reserva.fecha for reserva in reservas_no_completadas},
        "horas": {}
    }

    # Obtener horas ocupadas de reservas no completadas
    for reserva in reservas_no_completadas:
        if reserva.fecha not in ocupadas["horas"]:
            ocupadas["horas"][reserva.fecha] = set()
        ocupadas["horas"][reserva.fecha].add(reserva.hora.strftime('%H:%M'))

    # Filtrar fechas y horas disponibles desde hoy
    for i in range(15):  # Desde hoy hasta 15 días adelante
        fecha = hoy + timedelta(days=i)
        horas_disponibles[fecha] = []

        for h in range(8, 16):  # De 08:00 a 15:00
            hora_formateada = f"{h:01}:00"

            # Si la fecha es hoy, verifica que la hora no haya pasado
            if fecha == hoy and h < ahora.hour:
                continue  # Ignora horas pasadas para hoy

            # Verifica si la hora está ocupada en la fecha seleccionada
            if hora_formateada not in ocupadas["horas"].get(fecha, set()):
                horas_disponibles[fecha].append(hora_formateada)

    if request.method == "POST":
        # Manejar la eliminación de reservas
        if 'eliminar' in request.POST:
            reserva_id = request.POST.get('eliminar')
            reserva = get_object_or_404(Reserva, id_reserva=reserva_id, usuario=request.user)  # Filtrar por usuario
            reserva.delete()
            messages.error(request, 'Reserva eliminada con éxito.')
            return redirect('citas')
        
        # Manejar la creación o edición de reservas
        if 'id_reserva' in request.POST:  # Para editar
            reserva_id = request.POST.get('id_reserva')
            reserva = get_object_or_404(Reserva, id_reserva=reserva_id, usuario=request.user)  # Filtrar por usuario

            # Actualiza la reserva
            reserva.empresa_id = request.POST.get('empresa')  # Actualiza el lugar
            reserva.fecha = request.POST.get('fecha')  # Actualiza la fecha
            reserva.hora = request.POST.get('hora')  # Actualiza la hora
            reserva.servicio_id = request.POST.get('servicio')  # Actualiza el servicio
            reserva.save()
            messages.success(request, 'Reserva actualizada con éxito.')
            return redirect('citas')
        else:  # Para crear
            form = ReservaForm(request.POST)
            if form.is_valid():
                reserva = form.save(commit=False)
                reserva.usuario = request.user  # Asignar el usuario actual
                reserva.save()
                messages.success(request, 'Reserva creada con éxito.')
                return redirect('citas')
    else:
        form = ReservaForm()

    # Generar lista de fechas disponibles
    fechas_disponibles = [hoy + timedelta(days=i) for i in range(15)] 

    # Renderiza la vista con los datos necesarios
    return render(request, 'citas.html', {
        'reservas_no_completadas': reservas_no_completadas,
        'reservas_completadas': reservas_completadas,
        'servicios': servicios,
        'empresas': empresas,
        'horas_disponibles': horas_disponibles,
        'fechas_disponibles': fechas_disponibles,
        'hoy': hoy,
    })




@login_required
def contacto(request):
    if request.method == 'POST':
        contenido = request.POST.get('contenido')

        if contenido:
            mensaje = MensajeQueja(contenido=contenido, usuario=request.user)
            mensaje.save()
            messages.success(request, "Tu mensaje ha sido enviado exitosamente y sera respondido en el menor tiempo posible.")
            return redirect('contacto')  
        else:
            messages.error(request, "Por favor, ingresa un mensaje.")
            return redirect('contacto') 

    return render(request, 'contacto.html') 

def resetCorreo(request):
    return render(request, 'reset_correo.html')
def resetContrasena(request):
    return render(request, 'reset_contrasena.html')


@login_required
def comentarios(request):
    if request.method == 'POST':
        form = ComentarioClienteForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)  
            comentario.usuario = request.user  
            comentario.save() 
            messages.success(request, "Tu comentario ha sido publicado exitosamente.")
            return redirect('comentarios')  

    else:
        form = ComentarioClienteForm()

    return render(request, 'comentarios.html', {'form': form})



def get_horas(request):
    empresa_id = request.GET.get('empresa_id')
    servicio_id = request.GET.get('servicio_id')
    fecha_str = request.GET.get('fecha')
    if empresa_id and servicio_id and fecha_str:
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            if fecha_obj < timezone.now().date():
                return JsonResponse({'horas': []})

            reservas_existentes = Reserva.objects.filter(
                empresa_id=empresa_id,
                fecha=fecha_obj
            )

            # Solo toma las reservas que tengan el servicio seleccionado
            reservas_con_servicio = []
            for reserva in reservas_existentes:
                if ReservaServicio.objects.filter(reserva=reserva, servicio_id=servicio_id).exists():
                    reservas_con_servicio.append(reserva)

            horas_ocupadas = set(reserva.hora.strftime('%H:%M') for reserva in reservas_con_servicio)

            horas_disponibles = []
            for h in range(8, 21):  # 8:00 a 20:00
                hora_formateada = f"{h:02}:00"
                if fecha_obj == timezone.now().date() and h < timezone.now().hour:
                    continue
                if hora_formateada not in horas_ocupadas:
                    horas_disponibles.append(hora_formateada)

            return JsonResponse({'horas': horas_disponibles})

        except ValueError:
            return JsonResponse({'horas': []})

    return JsonResponse({'horas': []})




############################################################ comienzo de crud


def login_crud(request):
    if request.user.is_authenticated and hasattr(request.user, 'rol') and request.user.rol == 'admin':
        return redirect('homecrud')
    
    if request.method == 'POST':
        nombre_usuario = request.POST['nombre_usuario']
        contrasena = request.POST['contrasena']
        
        # Autenticación del usuario
        usuario = authenticate(request, username=nombre_usuario, password=contrasena)
        
        if usuario is not None:
            # Verificar si el usuario tiene rol de admin
            if hasattr(usuario, 'rol') and usuario.rol == 'admin':
                auth_login(request, usuario)  # Iniciar sesión con el usuario autenticado
                messages.success(request, f'Bienvenido administrador, {usuario.nombre_usuario}!')
                return redirect('homecrud')
            else:
                messages.error(request, 'Acceso denegado. Solo los administradores pueden acceder.')
                return redirect('logincrud')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return redirect('logincrud')
    
    return render(request, 'login_crud.html')
    

def logout_view(request):
    auth_logout(request)  # Cerrar sesión
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('home')  # Redirigir a la página de home normal


@admin_required
def comentarios_crud(request):
    comentarios = Comentario.objects.all()
    
    # Calcular estadísticas
    total_comentarios = comentarios.count()
    total_usuarios = comentarios.values('usuario').distinct().count()

    if request.method == "POST":
        # Manejar la eliminación de comenatrios
        if 'eliminar' in request.POST:
            comentario_id = request.POST.get('eliminar')
            comentario = get_object_or_404(Comentario, id_comentario=comentario_id)
            comentario.delete()
            messages.error(request, 'El comentario se a eliminado.')
            return redirect('comentarioscrud')
    else:
        form = ComentarioForm()
    
    context = {
        'comentarios': comentarios, 
        'form': form,
        'total_comentarios': total_comentarios,
        'total_usuarios': total_usuarios,
    }
    
    return render(request, 'comentarios_crud.html', context)




@admin_required
def quejas_crud(request):
    quejas =MensajeQueja.objects.all()

    if request.method == "POST":
        # Manejar la eliminación de comenatrios
        if 'eliminar' in request.POST:
            queja_id = request.POST.get('eliminar')
            queja = get_object_or_404(MensajeQueja, id_mensaje=queja_id)
            queja.delete()
            messages.error(request, 'La queja se a eliminado.')
            return redirect('quejascrud')

    if request.method == "POST":
        # Manejar la respuesta a la queja
        if 'id_reserva' in request.POST:
            respuesta = request.POST.get('respuesta')
            queja_id = request.POST.get('id_reserva')
            queja = get_object_or_404(MensajeQueja, id_mensaje=queja_id)

            # Obtener el usuario asociado a la queja (ajusta según tu modelo)
            usuario = get_object_or_404(Usuario, id_usuario=queja.usuario_id)  # Asumiendo que hay un campo id_usuario en MensajeQueja

            # Aquí puedes guardar la respuesta en tu modelo si es necesario
            queja.respuesta = respuesta
            queja.save()

            messages.success(request, 'La respuesta se ha enviado.')

            # Enviar mensaje de WhatsApp
            try:
                conn = http.client.HTTPSConnection("kqqk31.api.infobip.com")
                payload = json.dumps({
                    "messages": [
                        {
                            "from": "447860099299",  # Tu número de WhatsApp
                            "to": usuario.telefono,  # Número del destinatario desde la tabla Usuario
                            "messageId": "c2dbb13f-2a4a-48d7-97c2-085d5d3d6108",
                            "content": {
                                "templateName": "message_test",
                                "templateData": {
                                    "body": {
                                        "placeholders": [respuesta]  # Usar la respuesta como contenido
                                    }
                                },
                                "language": "es"
                            }
                        }
                    ]
                })
                headers = {
                    'Authorization': 'App e5eb011e80db665606dd35c15e897846-c8cf84ba-fd3f-401e-a267-7e95cc6bce48',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                conn.request("POST", "/whatsapp/1/message/template", payload, headers)
                res = conn.getresponse()
                data = res.read()
                print(data.decode("utf-8"))  # Puedes usar logging en lugar de print
            except Exception as e:
                print("Error al enviar mensaje:", e)
                messages.error(request, 'Error al enviar el mensaje de WhatsApp.')

            return redirect('quejascrud')
    else:
        form = QuejaForm()
    return render(request, 'quejas_crud.html', {'quejas': quejas, 'form': form})



@admin_required
def usuarios_crud(request):
    usuarios = Usuario.objects.all()
    form = UsuariosForm() 

    # Calcular estadísticas ANTES de aplicar filtros de búsqueda
    total_usuarios = usuarios.count()
    total_admins = usuarios.filter(rol='admin').count()
    total_clientes = usuarios.filter(rol='cliente').count()

    # Filtrar según los parámetros de búsqueda
    nombre_usuario = request.GET.get('nombre_usuario', '')
    correo = request.GET.get('correo', '')
    telefono = request.GET.get('telefono', '')
    rol = request.GET.get('rol', '')

    if nombre_usuario:
        usuarios = usuarios.filter(nombre_usuario__icontains=nombre_usuario)
    if correo:
        usuarios = usuarios.filter(correo__icontains=correo)
    if telefono:
        usuarios = usuarios.filter(telefono__icontains=telefono)
    if rol:
        usuarios = usuarios.filter(rol=rol)

    if request.method == "POST":
        # Manejar la eliminación de los usuarios
        if 'eliminar' in request.POST:
            usuario_id  = request.POST.get('eliminar')
            usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
            usuario.delete()
            messages.error(request, 'El usuario a sido eliminado.')
            return redirect('usuarioscrud')
        
        # Manejar la creación de nuevos usuarios
        if 'nombre_completo' in request.POST and 'id_usuario' not in request.POST:
            contrasena1 = request.POST.get('contrasena1')
            contrasena2= request.POST.get('contrasena2')
            nombre_usuario = request.POST.get('nombre_usuario')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono')

            # Verificar si el nombre de usuario ya está en uso
            if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
            # Verificar si el correo ya está en uso
            elif Usuario.objects.filter(correo=correo).exists():
                messages.error(request, 'El correo ya está en uso.')
            else:
                # Concatenar el prefijo "57" al teléfono ingresado
                telefono_completo = "57" + telefono
                if contrasena1 == contrasena2:
                    nuevo_usuario = Usuario(
                        nombre_completo=request.POST.get('nombre_completo'),
                        nombre_usuario=nombre_usuario,
                        correo=correo,
                        telefono=telefono_completo,  # Guardar el número completo
                        direccion=request.POST.get('direccion'),
                        rol=request.POST.get('rol'),
                        password=make_password(contrasena1)  # Hash de la contraseña
                    )
                    nuevo_usuario.save()
                    messages.success(request, 'El usuario ha sido creado.')
                    return redirect('usuarioscrud')
                else:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return redirect('usuarioscrud')

        # Manejar la actualización de usuarios
        if 'id_usuario' in request.POST:
            usuario_id = request.POST.get('id_usuario')
            usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
            usuario.nombre_completo = request.POST.get('nombre_completo')
            usuario.nombre_usuario = request.POST.get('nombre_usuario')
            usuario.correo = request.POST.get('correo')
            usuario.direccion = request.POST.get('direccion')
            usuario.rol = request.POST.get('rol')

            # Actualizar la contraseña solo si se proporciona una nueva
            contrasena11 = request.POST.get('contrasena11')
            contrasena22= request.POST.get('contrasena22')

            # Solo actualizar la contraseña si el campo no está vacío
            if contrasena11:
                if contrasena11 == contrasena22:
                    usuario.password = make_password(contrasena11)
                else:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return redirect('usuarioscrud')

            # Guardar los cambios en el usuario
            usuario.save()
            messages.success(request, 'El usuario ha sido actualizado.')
            return redirect('usuarioscrud')

    else:
        form = UsuariosForm()

    # Contexto con estadísticas calculadas
    context = {
        'usuarios': usuarios, 
        'form': form,
        'total_usuarios': total_usuarios,
        'total_admins': total_admins,
        'total_clientes': total_clientes,
    }

    return render(request, 'usuarios_crud.html', context)

@admin_required
def citas_crud(request):
    ahora = datetime.now()
    hoy = ahora.date()
    
    # Obtener reservas en estado 'no_completado' ordenadas por fecha y hora
    reservas = Reserva.objects.filter(estado='no_completado').select_related('empresa', 'usuario').prefetch_related('reservaservicio_set__servicio').order_by('fecha', 'hora')
    servicios = Servicio.objects.all() 
    empresas = Empresa.objects.all()

    horas_disponibles = {}
    ocupadas = {
        "fechas": {reserva.fecha for reserva in reservas},
        "horas": {}
    }

    # Obtener horas ocupadas
    for reserva in reservas:
        if reserva.fecha not in ocupadas["horas"]:
            ocupadas["horas"][reserva.fecha] = set()
        ocupadas["horas"][reserva.fecha].add(reserva.hora.strftime('%H:%M'))

    # Filtrar fechas y horas disponibles desde hoy
    for i in range(15):  # Desde hoy hasta 15 días adelante
        fecha = hoy + timedelta(days=i)
        horas_disponibles[fecha] = []

        for h in range(8, 16):  # De 08:00 a 15:00
            hora_formateada = f"{h:01}:00"

            # Si la fecha es hoy, verifica que la hora no haya pasado
            if fecha == hoy and h < ahora.hour:
                continue  # Ignora horas pasadas para hoy

            # Verifica si la hora está ocupada en la fecha seleccionada
            if hora_formateada not in ocupadas["horas"].get(fecha, set()):
                horas_disponibles[fecha].append(hora_formateada)

    if request.method == "POST":
        # Manejar la eliminación de reservas
        if 'eliminar' in request.POST:
            reserva_id = request.POST.get('eliminar')
            reserva = get_object_or_404(Reserva, id_reserva=reserva_id)
            reserva.delete()
            messages.error(request, 'Reserva eliminada con éxito.')
            return redirect('citascrud')

        # Manejar la creación o edición de reservas
        if 'id_reserva' in request.POST:  # Para editar
            reserva_id = request.POST.get('id_reserva')
            reserva = get_object_or_404(Reserva, id_reserva=reserva_id)

            # Actualizar los datos de la reserva
            empresa_id = request.POST.get('empresa')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            servicio_id = request.POST.get('servicio')

            if empresa_id:
                empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
                reserva.empresa = empresa
            
            if fecha:
                reserva.fecha = fecha
            
            if hora:
                reserva.hora = hora
            
            reserva.save()

            # Actualizar el servicio asociado
            if servicio_id:
                servicio = get_object_or_404(Servicio, id_servicio=servicio_id)
                # Eliminar la relación anterior
                ReservaServicio.objects.filter(reserva=reserva).delete()
                # Crear la nueva relación
                ReservaServicio.objects.create(reserva=reserva, servicio=servicio)

            messages.success(request, 'Reserva actualizada con éxito.')
            return redirect('citascrud')
        else:  # Para crear
            form = ReservaForm(request.POST)
            if form.is_valid():
                reserva = form.save(commit=False)
                reserva.usuario = request.user  # Asignar el usuario actual
                reserva.save()
                messages.success(request, 'Reserva creada con éxito.')
                return redirect('citascrud')
    else:
        form = ReservaForm()

    # Generar lista de fechas disponibles
    fechas_disponibles = [hoy + timedelta(days=i) for i in range(15)] 

    # Renderiza la vista con los datos necesarios
    return render(request, 'citas_crud.html', {
        'reservas': reservas,
        'form': form,
        'servicios': servicios,
        'empresas': empresas,
        'horas_disponibles': horas_disponibles,
        'fechas_disponibles': fechas_disponibles,
        'hoy': hoy,
    })



@admin_required
def citascom_crud(request):
    reservas = Reserva.objects.filter(estado='completado')
    servicios = Servicio.objects.all() 
    empresas = Empresa.objects.all()

    if request.method == "POST":
        # Manejar la eliminación de reservas
        if 'eliminar' in request.POST:
            reserva_id = request.POST.get('eliminar')
            reserva = get_object_or_404(Reserva, id_reserva=reserva_id)
            reserva.delete()
            messages.error(request, 'Reserva eliminada con éxito.')
            return redirect('citascomcrud')

    return render(request,'citascom_crud.html',{
                'reservas': reservas,
                'servicios': servicios,
                'empresas': empresas })



@admin_required
def cambiar_estado_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id_reserva=reserva_id)
    
    if reserva.estado == 'no_completado':
        reserva.estado = 'completado'
        reserva.save()
        messages.success(request, 'La reserva ha sido marcada como completada.')
    else:
        messages.info(request, 'La reserva ya está completada.')

    return redirect('citascrud') 


@admin_required
def servicios_crud(request):
    servicios = Servicio.objects.all()
    form = ServicioForm()

    # Calcular estadísticas
    total_asignaciones = EmpresaServicio.objects.count()

    # Filtrar según los parámetros de búsqueda
    nombre_servicio = request.GET.get('nombre_servicio', '')
    if nombre_servicio:
        servicios = servicios.filter(nombre_servicio__icontains=nombre_servicio)

    if request.method == "POST":
        # Manejar la eliminación de los servicios
        if 'eliminar' in request.POST:
            servicio_id = request.POST.get('eliminar')
            servicio_a_eliminar = get_object_or_404(Servicio, id_servicio=servicio_id)
            servicio_a_eliminar.delete()
            messages.error(request, 'El Servicio ha sido eliminado.')
            return redirect('servicioscrud')

        # Manejar la creación de nuevos servicios
        if 'nombre_servicio' in request.POST and 'id_servicio' not in request.POST:
            nombre_servicio = request.POST.get('nombre_servicio')
            descripcion = request.POST.get('descripcion')
            precio = request.POST.get('precio')

            nuevo_servicio = Servicio(
                nombre_servicio=nombre_servicio,
                descripcion=descripcion,
                precio=precio
            )
            nuevo_servicio.save()
            messages.success(request, 'El servicio ha sido creado.')
            return redirect('servicioscrud')

        # Manejar la actualización de servicios
        if 'id_servicio' in request.POST:
            servicio_id = request.POST.get('id_servicio')
            servicio = get_object_or_404(Servicio, id_servicio=servicio_id)

            # Obtener los nuevos valores desde el POST
            nuevo_nombre_servicio = request.POST.get('nombre_servicio')
            nueva_descripcion = request.POST.get('descripcion')
            nuevo_precio = request.POST.get('precio')

            # Solo actualizar si se proporciona un nuevo valor
            if nuevo_nombre_servicio:
                servicio.nombre_servicio = nuevo_nombre_servicio

            if nueva_descripcion:
                servicio.descripcion = nueva_descripcion

            if nuevo_precio:
                servicio.precio = nuevo_precio

            servicio.save()
            messages.success(request, 'El servicio ha sido actualizado.')
            return redirect('servicioscrud')

        # Manejar la asignación/desasignación de empresas
        if 'asignar_empresa' in request.POST:
            servicio_id = request.POST.get('servicio_id')
            servicio = get_object_or_404(Servicio, id_servicio=servicio_id)
            empresa_ids = request.POST.getlist('empresas')  # Recoge las empresas seleccionadas

            # Obtener las empresas que ya están asociadas al servicio
            empresas_asociadas = EmpresaServicio.objects.filter(servicio=servicio)

            # Eliminar las relaciones de empresa-servicio que no están seleccionadas
            for empresa_servicio in empresas_asociadas:
                if str(empresa_servicio.empresa.id_empresa) not in empresa_ids:
                    empresa_servicio.delete()

            # Crear las relaciones de empresa-servicio para las empresas nuevas seleccionadas
            for empresa_id in empresa_ids:
                empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
                # Crear la relación solo si no existe ya
                if not EmpresaServicio.objects.filter(servicio=servicio, empresa=empresa).exists():
                    EmpresaServicio.objects.create(empresa=empresa, servicio=servicio)

            messages.success(request, 'Las empresas han sido asignadas o desasignadas correctamente al servicio.')
            return redirect('servicioscrud')

    else:
        form = ServicioForm()

    # Obtener la lista de empresas disponibles
    empresas = Empresa.objects.all()

    # Obtener las empresas asociadas a cada servicio
    for servicio in servicios:
        servicio.empresas_asociadas = EmpresaServicio.objects.filter(servicio=servicio).values_list('empresa', flat=True)

    context = {
        'servicios': servicios, 
        'form': form, 
        'empresas': empresas,
        'total_asignaciones': total_asignaciones
    }

    return render(request, 'servicios_crud.html', context)




@admin_required
def empresas_crud(request):
    empresas = Empresa.objects.all()
    form = EmpresaForm()  # Si estás usando un formulario de Django para crear y actualizar empresas

    # Filtrar según los parámetros de búsqueda
    nombre_empresa = request.GET.get('nombre_empresa', '')

    if nombre_empresa:
        empresas = empresas.filter(nombre_empresa__icontains=nombre_empresa)

    if request.method == "POST":
        # Manejar la eliminación de empresas
        if 'eliminar' in request.POST:
            empresa_id = request.POST.get('eliminar')
            empresa_a_eliminar = get_object_or_404(Empresa, id_empresa=empresa_id)
            empresa_a_eliminar.delete()
            messages.error(request, 'La empresa ha sido eliminada.')
            return redirect('empresascrud')

        # Manejar la creación de una nueva empresa
        if 'nombre_empresa' in request.POST and 'id_empresa' not in request.POST:
            nombre_empresa = request.POST.get('nombre_empresa')
            direccion = request.POST.get('direccion')
            telefono = request.POST.get('telefono')  # Capturar el teléfono
            email = request.POST.get('email')  # Capturar el email

            nueva_empresa = Empresa(
                nombre_empresa=nombre_empresa,
                direccion=direccion,
                telefono=telefono,
                email=email
            )
            nueva_empresa.save()
            messages.success(request, 'La empresa ha sido creada.')
            return redirect('empresascrud')

        # Manejar la actualización de la empresa
        if 'id_empresa' in request.POST:
            empresa_id = request.POST.get('id_empresa')
            empresa = get_object_or_404(Empresa, id_empresa=empresa_id)

            # Obtener los nuevos valores desde el POST
            nuevo_nombre_empresa = request.POST.get('nombre_empresa')
            nueva_direccion = request.POST.get('direccion')
            nuevo_telefono = request.POST.get('telefono')
            nuevo_email = request.POST.get('email')

            # Solo actualizar si se proporciona un nuevo valor
            if nuevo_nombre_empresa:
                empresa.nombre_empresa = nuevo_nombre_empresa
            if nueva_direccion:
                empresa.direccion = nueva_direccion
            if nuevo_telefono:
                empresa.telefono = nuevo_telefono
            if nuevo_email:
                empresa.email = nuevo_email

            empresa.save()
            messages.success(request, 'La empresa ha sido actualizada.')
            return redirect('empresascrud')

    return render(request, 'empresas_crud.html', {'empresas': empresas, 'form': form})




@admin_required
def home_crud(request):
    return render(request, 'home_crud.html')

