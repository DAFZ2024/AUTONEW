import http.client
import json

from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from django.db.models import Avg
from .models import Usuario,Comentario,MensajeQueja,Reserva,Servicio,Empresa,EmpresaServicio, ReservaServicio, Plan, SuscripcionUsuario, HistorialPagosSuscripcion, PlanEmpresarial, SuscripcionEmpresarial, SolicitudServicioEmpresa
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import ComentarioForm, ReservaForm, UsuariosForm,ComentarioClienteForm,QuejaForm,ServicioForm,EmpresaForm,ProfileUserForm,EmpresaRegistroForm, EmpresaPerfilForm, AdminProfileForm
from datetime import datetime,timedelta
from django.utils import timezone
from functools import wraps
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import uuid

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

def enviar_correo_confirmacion_reserva(usuario, empresa, servicios, fecha, hora, precio_total):
    """
    Envía un correo de confirmación de reserva al usuario
    """
    try:
        # Formatear la fecha en español
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        fecha_obj = datetime.strptime(str(fecha), '%Y-%m-%d')
        fecha_formateada = f"{dias_semana[fecha_obj.weekday()]}, {fecha_obj.day} de {meses[fecha_obj.month - 1]} de {fecha_obj.year}"
        
        # Preparar lista de servicios
        servicios_lista = []
        for servicio in servicios:
            servicios_lista.append({
                'nombre': servicio.nombre_servicio,
                'precio': servicio.precio
            })
        
        # Contexto para el template del correo
        context = {
            'usuario': usuario,
            'empresa': empresa,
            'servicios': servicios_lista,
            'fecha': fecha_formateada,
            'hora': hora,
            'precio_total': precio_total,
            'fecha_original': fecha
        }
        
        # Generar el contenido HTML del correo
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Confirmación de Reserva - AutoNew</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .info-card {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #2563eb; }}
                .service-item {{ padding: 10px; margin: 5px 0; background-color: #e5f3ff; border-radius: 5px; }}
                .total {{ font-size: 18px; font-weight: bold; color: #16a34a; text-align: right; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Reserva Confirmada!</h1>
                    <p>Tu cita ha sido reservada exitosamente</p>
                </div>
                
                <div class="content">
                    <p>Hola <strong>{usuario.nombre_completo}</strong>,</p>
                    <p>Tu reserva ha sido confirmada. Aquí tienes los detalles:</p>
                    
                    <div class="info-card">
                        <h3>📍 Punto de Lavado</h3>
                        <p><strong>{empresa.nombre_empresa}</strong></p>
                        <p>{empresa.direccion}</p>
                        <p>Teléfono: {empresa.telefono}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>✂️ Servicios Reservados</h3>
        """
        
        for servicio in servicios_lista:
            html_message += f"""
                        <div class="service-item">
                            <strong>{servicio['nombre']}</strong> - ${servicio['precio']}
                        </div>
            """
        
        html_message += f"""
                    </div>
                    
                    <div class="info-card">
                        <h3>📅 Fecha y Hora</h3>
                        <p><strong>{fecha_formateada}</strong></p>
                        <p><strong>Hora:</strong> {hora}</p>
                    </div>
                    
                    <div class="total">
                        Total a Pagar: ${precio_total}
                    </div>
                    
                    <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 20px;">
                        <p><strong>Importante:</strong></p>
                        <ul>
                            <li>Por favor, llega 10 minutos antes de tu cita</li>
                            <li>Si necesitas cancelar o reprogramar, hazlo con al menos 24 horas de anticipación</li>
                            <li>Trae una identificación válida</li>
                        </ul>
                    </div>
                    
                    <div class="footer">
                        <p>Gracias por elegir AutoNew</p>
                        <p>Si tienes alguna pregunta, contáctanos.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versión en texto plano
        plain_message = f"""
        ¡Reserva Confirmada!
        
        Hola {usuario.nombre_completo},
        
        Tu reserva ha sido confirmada. Aquí tienes los detalles:
        
        Punto de Lavado: {empresa.nombre_empresa}
        Dirección: {empresa.direccion}
        Teléfono: {empresa.telefono}
        
        Servicios Reservados:
        """
        
        for servicio in servicios_lista:
            plain_message += f"- {servicio['nombre']} - ${servicio['precio']}\n"
        
        plain_message += f"""
        
        Fecha: {fecha_formateada}
        Hora: {hora}
        
        Total a Pagar: ${precio_total}
        
        Importante:
        - Por favor, llega 10 minutos antes de tu cita
        - Si necesitas cancelar o reprogramar, hazlo con al menos 24 horas de anticipación
        - Trae una identificación válida
        
        Gracias por elegir AutoNew
        """
        
        # Enviar el correo
        send_mail(
            subject='Confirmación de Reserva - AutoNew',
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@autonew.com'),
            recipient_list=[usuario.correo],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False

# Decorador personalizado para verificar autenticación de empresa
def empresa_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        print(f"🔍 @empresa_required verificando acceso a {function.__name__}")
        
        # Verificar si la empresa está autenticada en la sesión
        if not request.session.get('es_empresa', False):
            print(f"❌ Empresa no autenticada")
            messages.error(request, 'Debes iniciar sesión como empresa para acceder a esta sección.')
            return redirect('logincrud')
        
        empresa_id = request.session.get('empresa_id')
        if not empresa_id:
            print(f"❌ No se encontró ID de empresa en sesión")
            messages.error(request, 'Error: Sesión de empresa inválida.')
            return redirect('logincrud')
        
        try:
            empresa = Empresa.objects.get(id_empresa=empresa_id)
            print(f"✅ Empresa autenticada: {empresa.nombre_empresa}")
            return function(request, *args, **kwargs)
        except Empresa.DoesNotExist:
            print(f"❌ Empresa no encontrada con ID: {empresa_id}")
            messages.error(request, 'Error: Empresa no encontrada.')
            return redirect('logincrud')
    return wrap

# Create your views here.



def home(request):
    comentarios = Comentario.objects.all().order_by('-fecha')  # Recupera todos los comentarios
    return render(request, 'home.html', {'comentarios': comentarios})

def empresas(request):
    if request.method == 'POST':
        form = EmpresaRegistroForm(request.POST)
        if form.is_valid():
            # Verificar que el email no esté ya registrado
            email = form.cleaned_data['email']
            if Empresa.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe una empresa registrada con este correo electrónico.')
                return render(request, 'empresas.html', {'form': form})
            
            # Crear la empresa
            empresa = form.save(commit=False)
            # Encriptar la contraseña
            empresa.contrasena = make_password(form.cleaned_data['contrasena'])
            empresa.save()
            
            messages.success(request, f'¡Empresa "{empresa.nombre_empresa}" registrada exitosamente! Bienvenido a AutoNew.')
            # Crear un nuevo formulario vacío después del registro exitoso
            form = EmpresaRegistroForm()
        else:
            messages.error(request, 'Hubo errores en el formulario. Por favor, verifica los datos ingresados.')
    else:
        form = EmpresaRegistroForm()
    
    return render(request, 'empresas/empresas.html', {'form': form})

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
            
            # Crear diccionario con los datos del formulario para preservarlos
            form_data = {
                'nombre_completo': nombre_completo,
                'nombre_usuario': nombre_usuario,
                'correo': correo,
                'telefono': telefono,
                'direccion': direccion,
            }
            
            # Validar que las contraseñas coincidan
            if contrasena1 != contrasena2:
                messages.error(request, "Las contraseñas no coinciden, intentalo de nuevo")
                return render(request, 'login.html', {
                    'show_register': True,
                    'form_data': form_data
                })
            
            # Validar que el nombre de usuario no exista
            if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
                messages.error(request, "El nombre de usuario ya esta registrado, intenta con otro.")
                return render(request, 'login.html', {
                    'show_register': True,
                    'form_data': form_data
                })
            
            # Validar que el correo no exista
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, "El correo ya esta registrado, intenta con otro.")
                return render(request, 'login.html', {
                    'show_register': True,
                    'form_data': form_data
                })
            
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
            
            # Verificar si el usuario existe y está activo
            try:
                usuario_check = Usuario.objects.get(nombre_usuario=nombre_usuario)
                if not usuario_check.is_active:
                    messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador para más información.')
                    return redirect('login')
            except Usuario.DoesNotExist:
                pass  # El usuario no existe, se manejará en la autenticación
            
            # Autenticar usuario
            usuario = authenticate(request, username=nombre_usuario, password=contrasena)
            
            if usuario is not None:
                # Verificar nuevamente que el usuario esté activo (por seguridad)
                if usuario.is_active:
                    auth_login(request, usuario)
                    messages.success(request, f'Bienvenido de nuevo, {usuario.nombre_usuario}!')
                    # Redirigir a la página solicitada o al home por defecto
                    next_url = request.GET.get('next', 'home')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador para más información.')
                    return redirect('login')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
                return redirect('login')
    
    # GET: Mostrar la página de login/registro
    else:
        # Verificar si se debe mostrar el formulario de registro
        show_register = request.GET.get('register') == 'true'
        return render(request, 'auth/login.html', {'show_register': show_register})
    

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

    return render(request, 'usuarios/perfil_usuario.html', {'usuario': usuario, 'form': form})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')



def nosotros(request):
    return render(request, 'pages_informativas/nosotros.html')



def servicios(request):
    comentarios = Comentario.objects.all().order_by('-fecha')  # Recupera todos los comentarios
    return render(request, 'servicios/servicios.html', {'comentarios': comentarios})


def reservas(request):
    ahora = timezone.now()
    hoy = ahora.date()
    servicios = Servicio.objects.all()  # Obtener todos los servicios disponibles
    empresas = Empresa.objects.filter(verificada=True)    # Obtener solo las empresas verificadas
    empresaservicio = EmpresaServicio.objects.all()
    
    # Obtener el usuario actual (si está autenticado)
    usuario = request.user if request.user.is_authenticated else None
    
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
        print(f"🔍 POST request recibido para reservas")
        print(f"📝 POST data: {dict(request.POST)}")
        
        opcion_empresa_id = request.POST.get('empresa')
        fecha_seleccionada = request.POST.get('fecha')
        hora_12h = request.POST.get('hora')  # Hora en formato 12h con AM/PM
        servicios_ids = request.POST.getlist('servicios')  # Cambio: obtener lista de servicios
        
        print(f"🏢 Empresa ID: {opcion_empresa_id}")
        print(f"📅 Fecha: {fecha_seleccionada}")
        print(f"🕐 Hora: {hora_12h}")
        print(f"🛠️ Servicios IDs: {servicios_ids}")
        
        # Convertir hora de 12h a 24h para procesamiento interno
        hora = convertir_hora_24h(hora_12h)
        
        # Verificar si es una petición AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Validar que se hayan seleccionado servicios
        if not servicios_ids:
            error_msg = "Debes seleccionar al menos un servicio."
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return redirect('reservas')
        
        # Verificar que todos los servicios existan
        try:
            servicios_seleccionados = Servicio.objects.filter(id_servicio__in=servicios_ids)
            if len(servicios_seleccionados) != len(servicios_ids):
                raise Servicio.DoesNotExist
        except (Servicio.DoesNotExist, ValueError):
            error_msg = "Uno o más servicios seleccionados no existen."
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return redirect('reservas')
        
        if opcion_empresa_id:
            try:
                empresa = Empresa.objects.get(id_empresa=opcion_empresa_id)
            except Empresa.DoesNotExist:
                error_msg = "El punto seleccionado no existe."
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_msg})
                messages.error(request, error_msg)
                return redirect('reservas')
            
            # Filtrar los servicios disponibles para la empresa seleccionada
            servicios_filtrados = Servicio.objects.filter(
                id_servicio__in=EmpresaServicio.objects.filter(empresa=empresa).values('servicio')
            )
            
            if not servicios_filtrados:
                error_msg = "No hay servicios disponibles para la empresa seleccionada."
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_msg})
                messages.error(request, error_msg)
                return redirect('reservas')
            
            # Verificar que todos los servicios seleccionados estén disponibles para esta empresa
            servicios_no_disponibles = []
            for servicio in servicios_seleccionados:
                if servicio not in servicios_filtrados:
                    servicios_no_disponibles.append(servicio.nombre_servicio)
            
            if servicios_no_disponibles:
                error_msg = f"Los siguientes servicios no están disponibles para esta empresa: {', '.join(servicios_no_disponibles)}"
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_msg})
                messages.error(request, error_msg)
                return redirect('reservas')
            
            # Verificar si la fecha y hora están ocupadas para esta empresa específica
            fecha_obj = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()
            
            # Verificación más específica: buscar reservas existentes para esta empresa y fecha/hora
            reserva_existente = Reserva.objects.filter(
                empresa=empresa,
                fecha=fecha_obj,
                hora=hora
            ).exists()
            
            print(f"🔍 Verificando disponibilidad:")
            print(f"   - Empresa: {empresa.nombre_empresa}")
            print(f"   - Fecha: {fecha_obj}")
            print(f"   - Hora: {hora} (convertida de {hora_12h})")
            print(f"   - ¿Existe reserva?: {reserva_existente}")
            
            if reserva_existente:
                error_msg = f"Lo siento, la fecha {fecha_seleccionada} a las {hora_12h} ya está ocupada en {empresa.nombre_empresa}."
                print(f"❌ {error_msg}")
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_msg})
                messages.error(request, error_msg)
                return redirect('reservas')
            
            # Verificar si el usuario tiene una suscripción activa
            suscripcion_activa = None
            tiene_suscripcion = False
            usar_suscripcion = False
            
            try:
                from .models import SuscripcionUsuario
                suscripcion_activa = SuscripcionUsuario.objects.filter(
                    usuario=usuario,
                    estado='activa'
                ).first()
                
                if suscripcion_activa and suscripcion_activa.esta_activa():
                    tiene_suscripcion = True
                    # Verificar si puede usar servicios de la suscripción
                    if suscripcion_activa.puede_usar_servicio():
                        usar_suscripcion = True
                    else:
                        print(f"⚠️ Usuario {usuario.nombre_usuario} ha agotado sus servicios del mes. Servicios restantes: {suscripcion_activa.servicios_restantes()}")
                        # No bloquear, solo usar pago individual
                        usar_suscripcion = False
            except Exception as e:
                print(f"Error verificando suscripción: {e}")
            
            # Crear la reserva
            reserva = Reserva(
                empresa=empresa,
                fecha=fecha_seleccionada,
                hora=hora,
                usuario=usuario,
                suscripcion_utilizada=suscripcion_activa if usar_suscripcion else None,
                es_pago_individual=not usar_suscripcion
            )
            reserva.save()
            
            # Crear las relaciones entre reserva y servicios (múltiples)
            precio_total = 0
            servicios_nombres = []
            for servicio in servicios_seleccionados:
                ReservaServicio.objects.create(reserva=reserva, servicio=servicio)
                precio_total += servicio.precio
                servicios_nombres.append(servicio.nombre_servicio)
            
            # Si usa suscripción, incrementar el contador de servicios utilizados
            if usar_suscripcion and suscripcion_activa:
                suscripcion_activa.servicios_utilizados_mes += len(servicios_seleccionados)
                suscripcion_activa.save()
                print(f"✅ Servicios utilizados actualizados: {suscripcion_activa.servicios_utilizados_mes}/{suscripcion_activa.plan.cantidad_servicios_mes if suscripcion_activa.plan.cantidad_servicios_mes > 0 else 'Ilimitado'}")
            else:
                print(f"💰 Reserva creada con pago individual. Precio total: ${precio_total}")
            
            # Enviar correo de confirmación
            try:
                correo_enviado = enviar_correo_confirmacion_reserva(
                    usuario=usuario,
                    empresa=empresa,
                    servicios=servicios_seleccionados,
                    fecha=fecha_seleccionada,
                    hora=hora_12h,
                    precio_total=precio_total
                )
                if correo_enviado:
                    print(f"✅ Correo de confirmación enviado a {usuario.correo}")
                else:
                    print(f"❌ Error enviando correo a {usuario.correo}")
            except Exception as e:
                print(f"❌ Excepción enviando correo: {e}")
            
            # Crear mensaje de éxito personalizado
            if len(servicios_nombres) == 1:
                base_msg = f"Tu cita para {servicios_nombres[0]} ha sido reservada para el {fecha_seleccionada} a las {hora_12h}."
            else:
                base_msg = f"Tu cita para {len(servicios_nombres)} servicios ha sido reservada para el {fecha_seleccionada} a las {hora_12h}."
            
            # Agregar información sobre el tipo de pago
            if usar_suscripcion:
                servicios_restantes = suscripcion_activa.servicios_restantes()
                success_msg = f"{base_msg} ✅ Pagado con tu suscripción. Te quedan {servicios_restantes} servicios este mes."
            else:
                if tiene_suscripcion:
                    success_msg = f"{base_msg} 💰 Has agotado tus servicios del mes, por lo que esta reserva se cobrará individualmente (${precio_total})."
                else:
                    success_msg = f"{base_msg} 💰 Total a pagar: ${precio_total}."
            
            if is_ajax:
                return JsonResponse({
                    'success': True, 
                    'message': success_msg,
                    'reserva': {
                        'empresa': empresa.nombre_empresa,
                        'servicios': servicios_nombres,
                        'precio_total': str(precio_total),
                        'fecha': fecha_seleccionada,
                        'hora': hora_12h,
                        'servicios_detalle': [
                            {
                                'nombre': servicio.nombre_servicio,
                                'precio': str(servicio.precio)
                            } for servicio in servicios_seleccionados
                        ]
                    }
                })
            
            messages.success(request, success_msg)
            return redirect('reservas')
        else:
            error_msg = "No se ha seleccionado un punto."
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return redirect('reservas')
    
    # Generar horas disponibles
    horas_disponibles = {}
    for i in range(15):
        fecha = hoy + timedelta(days=i)
        horas_disponibles[fecha] = []
        
        for h in range(8, 21):  # De 8:00 AM a 8:00 PM
            hora_formateada_24h = f"{h:02}:00"
            
            if fecha == hoy and h < ahora.hour:
                continue
            
            # Verifica si la hora está ocupada para esta fecha
            if hora_formateada_24h not in ocupadas["horas"].get(fecha, set()):
                # Convertir a formato 12h con AM/PM para mostrar al usuario
                hora_12h = convertir_hora_12h(hora_formateada_24h)
                horas_disponibles[fecha].append(hora_12h)
    
    fechas_disponibles = [hoy + timedelta(days=i) for i in range(15)]
    
    # Obtener información de la suscripción del usuario si está autenticado
    suscripcion_info = None
    if usuario and usuario.is_authenticated:
        try:
            from .models import SuscripcionUsuario
            suscripcion_activa = SuscripcionUsuario.objects.filter(
                usuario=usuario,
                estado='activa'
            ).first()
            
            if suscripcion_activa and suscripcion_activa.esta_activa():
                suscripcion_info = {
                    'tiene_suscripcion': True,
                    'plan_nombre': suscripcion_activa.plan.nombre,
                    'servicios_restantes': suscripcion_activa.servicios_restantes(),
                    'servicios_utilizados': suscripcion_activa.servicios_utilizados_mes,
                    'servicios_totales': suscripcion_activa.plan.cantidad_servicios_mes,
                    'fecha_fin': suscripcion_activa.fecha_fin,
                    'puede_usar_servicio': suscripcion_activa.puede_usar_servicio()
                }
            else:
                suscripcion_info = {'tiene_suscripcion': False}
        except Exception as e:
            print(f"Error obteniendo información de suscripción: {e}")
            suscripcion_info = {'tiene_suscripcion': False}
    
    return render(request, 'reservas/reservas.html', {
        'ocupadas': ocupadas,
        'horas_disponibles': horas_disponibles,
        'fechas_disponibles': fechas_disponibles,
        'hoy': hoy,
        'servicios_filtrados': servicios_filtrados,
        'empresas': empresas,
        'servicios': servicios,
        'empresaservicio': empresaservicio,
        'suscripcion_info': suscripcion_info
    })

# Vista para obtener servicios por empresa (AJAX)
def obtener_servicios(request):
    empresa_id = request.GET.get('empresa_id')
    if empresa_id:
        try:
            empresa = Empresa.objects.get(id_empresa=empresa_id)
            # Forma más directa: usar la relación many-to-many
            servicios = empresa.servicios.all()
            # (Si se quisiera mantener la otra forma correcta sería usando values_list('servicio', flat=True))
            servicios_data = [
                {
                    'id_servicio': s.id_servicio,
                    'nombre_servicio': s.nombre_servicio,
                    'descripcion': s.descripcion,
                    'precio': s.precio
                } for s in servicios
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

# Función helper para convertir hora de 24h a 12h con AM/PM
def convertir_hora_12h(hora_24h):
    """Convierte hora en formato 24h (HH:MM) a formato 12h con AM/PM"""
    try:
        hora_obj = datetime.strptime(hora_24h, '%H:%M').time()
        # Formatear a 12 horas con AM/PM
        return hora_obj.strftime('%I:%M %p')
    except:
        return hora_24h  # Retorna la hora original si hay error

# Función helper para convertir hora de 12h a 24h
def convertir_hora_24h(hora_12h):
    """Convierte hora en formato 12h con AM/PM a formato 24h (HH:MM)"""
    try:
        hora_obj = datetime.strptime(hora_12h, '%I:%M %p').time()
        return hora_obj.strftime('%H:%M')
    except:
        return hora_12h  # Retorna la hora original si hay error

# Vista para obtener horas disponibles (AJAX)
def get_horas(request):
    empresa_id = request.GET.get('empresa_id')
    servicio_id = request.GET.get('servicio_id')
    fecha_str = request.GET.get('fecha')
    
    print(f"🕐 get_horas llamado con empresa_id={empresa_id}, servicio_id={servicio_id}, fecha={fecha_str}")
    
    if empresa_id and servicio_id and fecha_str:
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            print(f"📅 Fecha objeto: {fecha_obj}")
            
            if fecha_obj < timezone.now().date():
                print(f"❌ Fecha en el pasado")
                return JsonResponse({'horas': []})

            # Obtener TODAS las reservas para esta empresa y fecha (no solo del servicio específico)
            reservas_existentes = Reserva.objects.filter(
                empresa_id=empresa_id,
                fecha=fecha_obj
            )
            
            print(f"🔍 Reservas existentes para empresa {empresa_id} en fecha {fecha_obj}: {reservas_existentes.count()}")
            
            # Obtener todas las horas ocupadas (independientemente del servicio)
            horas_ocupadas = set()
            for reserva in reservas_existentes:
                hora_str = reserva.hora.strftime('%H:%M')
                horas_ocupadas.add(hora_str)
                print(f"⏰ Hora ocupada: {hora_str}")

            print(f"🚫 Total horas ocupadas: {horas_ocupadas}")

            horas_disponibles = []
            ahora = timezone.now()
            
            for h in range(8, 21):  # 8:00 a 20:00
                hora_formateada_24h = f"{h:02}:00"
                
                # Si es hoy, no mostrar horas que ya pasaron
                if fecha_obj == ahora.date() and h <= ahora.hour:
                    print(f"⏳ Hora {hora_formateada_24h} ya pasó")
                    continue
                
                # Si la hora no está ocupada, agregarla
                if hora_formateada_24h not in horas_ocupadas:
                    # Convertir a formato 12h con AM/PM para mostrar al usuario
                    hora_12h = convertir_hora_12h(hora_formateada_24h)
                    horas_disponibles.append(hora_12h)
                    print(f"✅ Hora disponible: {hora_12h} ({hora_formateada_24h})")
                else:
                    print(f"❌ Hora ocupada: {hora_formateada_24h}")

            print(f"📋 Horas disponibles finales: {horas_disponibles}")
            return JsonResponse({'horas': horas_disponibles})

        except ValueError as e:
            print(f"❌ Error de valor: {e}")
            return JsonResponse({'horas': []})
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return JsonResponse({'horas': []})

    print(f"❌ Parámetros faltantes")
    return JsonResponse({'horas': []})




def planes(request):
    return render(request, 'planes/planes.html')


def planes_empresariales(request):
    """Vista para mostrar los planes empresariales disponibles"""
    # Obtener todos los planes empresariales activos, ordenados por precio
    planes_empresariales = PlanEmpresarial.objects.filter(activo=True).order_by('precio_mensual_por_vehiculo')
    
    context = {
        'planes_empresariales': planes_empresariales,
        'titulo': 'Planes Empresariales',
        'descripcion': 'Soluciones especializadas para flotas de vehículos y empresas de transporte'
    }
    
    return render(request, 'planes/planes_empresariales.html', context)


@login_required
def citas(request):
    ahora = datetime.now()
    hoy = ahora.date()
    
    # Obtener reservas del usuario actual with prefetch_related para optimizar
    reservas_pendientes = Reserva.objects.filter(
        estado='pendiente', 
        usuario=request.user
    ).prefetch_related('servicios', 'empresa')
    
    reservas_completadas = Reserva.objects.filter(
        estado='completado', 
        usuario=request.user
    ).prefetch_related('servicios', 'empresa')
    
    # Obtener todas las reservas del usuario para el total
    total_reservas = Reserva.objects.filter(usuario=request.user)
    
    # Debug: Imprimir información sobre las reservas
    print(f"Usuario: {request.user.nombre_usuario}")
    print(f"Reservas pendientes: {reservas_pendientes.count()}")
    print(f"Reservas completadas: {reservas_completadas.count()}")
    print(f"Total reservas: {total_reservas.count()}")
    for reserva in reservas_completadas:
        print(f"  - ID: {reserva.id_reserva}, Empresa: {reserva.empresa.nombre_empresa}, Usuario: {reserva.usuario.nombre_usuario}")
    
    servicios = Servicio.objects.all() 
    empresas = Empresa.objects.all()

    horas_disponibles = {}
    ocupadas = {
        "fechas": {reserva.fecha for reserva in reservas_pendientes},
        "horas": {}
    }

    # Obtener horas ocupadas de reservas no completadas
    for reserva in reservas_pendientes:
        if reserva.fecha not in ocupadas["horas"]:
            ocupadas["horas"][reserva.fecha] = set()
        ocupadas["horas"][reserva.fecha].add(reserva.hora.strftime('%H:%M'))

    # Filtrar fechas y horas disponibles desde hoy
    for i in range(15):  # Desde hoy hasta 15 días adelante
        fecha = hoy + timedelta(days=i)
        horas_disponibles[fecha] = []

        for h in range(8, 16):  # De 08:00 a 15:00
            hora_formateada_24h = f"{h:01}:00"

            # Si la fecha es hoy, verifica que la hora no haya pasado
            if fecha == hoy and h < ahora.hour:
                continue  # Ignora horas pasadas para hoy

            # Verifica si la hora está ocupada en la fecha seleccionada
            if hora_formateada_24h not in ocupadas["horas"].get(fecha, set()):
                # Convertir a formato 12h con AM/PM para mostrar al usuario
                hora_12h = convertir_hora_12h(hora_formateada_24h)
                horas_disponibles[fecha].append(hora_12h)

    if request.method == "POST":
        # Manejar la eliminación de reservas
        if 'eliminar' in request.POST:
            reserva_id = request.POST.get('eliminar')
            try:
                reserva = get_object_or_404(Reserva, id_reserva=reserva_id, usuario=request.user)  # Filtrar por usuario
                reserva_info = f"{reserva.empresa.nombre_empresa} - {reserva.fecha} {reserva.hora}"
                
                # Si la reserva utiliza suscripción, devolver los servicios utilizados
                if reserva.suscripcion_utilizada and not reserva.es_pago_individual:
                    suscripcion = reserva.suscripcion_utilizada
                    servicios_count = reserva.servicios.count()
                    if servicios_count == 0:
                        servicios_count = 1  # Al menos un servicio por defecto
                    
                    # Restar los servicios del contador (devolver servicios)
                    suscripcion.servicios_utilizados_mes = max(0, suscripcion.servicios_utilizados_mes - servicios_count)
                    suscripcion.save()
                    print(f"✅ Servicios devueltos a la suscripción. Servicios utilizados: {suscripcion.servicios_utilizados_mes}/{suscripcion.plan.cantidad_servicios_mes if suscripcion.plan.cantidad_servicios_mes > 0 else 'Ilimitado'}")
                
                reserva.delete()
                messages.success(request, f'Reserva eliminada con éxito: {reserva_info}')
                
            except Exception as e:
                print(f"Error al eliminar reserva {reserva_id}: {str(e)}")
                messages.error(request, 'Error al eliminar la reserva. Por favor, inténtelo de nuevo.')
            return redirect('citas')
        
        # Manejar la creación o edición de reservas
        if 'id_reserva' in request.POST:  # Para editar
            reserva_id = request.POST.get('id_reserva')
            reserva = get_object_or_404(Reserva, id_reserva=reserva_id, usuario=request.user)  # Filtrar por usuario

            # Actualiza la reserva
            reserva.empresa_id = request.POST.get('empresa')  # Actualiza el lugar
            reserva.fecha = request.POST.get('fecha')  # Actualiza la fecha
            # Convertir hora de 12h a 24h antes de guardar
            hora_12h = request.POST.get('hora')
            reserva.hora = convertir_hora_24h(hora_12h)  # Actualiza la hora
            reserva.servicio_id = request.POST.get('servicio')  # Actualiza el servicio
            reserva.save()
            messages.success(request, 'Reserva actualizada con éxito.')
            return redirect('citas')
        else:  # Para crear
            form = ReservaForm(request.POST)
            if form.is_valid():
                # Verificar si el usuario tiene una suscripción activa
                suscripcion_activa = None
                tiene_suscripcion = False
                
                try:
                    from .models import SuscripcionUsuario
                    suscripcion_activa = SuscripcionUsuario.objects.filter(
                        usuario=request.user,
                        estado='activa'
                    ).first()
                    
                    if suscripcion_activa and suscripcion_activa.esta_activa():
                        tiene_suscripcion = True
                        # Verificar si puede usar más servicios este mes
                        if not suscripcion_activa.puede_usar_servicio():
                            messages.error(request, f"Has agotado tus servicios del mes. Servicios restantes: {suscripcion_activa.servicios_restantes()}")
                            return redirect('citas')
                except Exception as e:
                    print(f"Error verificando suscripción: {e}")
                
                reserva = form.save(commit=False)
                reserva.usuario = request.user  # Asignar el usuario actual
                reserva.suscripcion_utilizada = suscripcion_activa if tiene_suscripcion else None
                reserva.es_pago_individual = not tiene_suscripcion
                reserva.save()
                
                # Si tiene suscripción activa, incrementar el contador de servicios utilizados
                if tiene_suscripcion and suscripcion_activa:
                    # Contar los servicios asociados a esta reserva
                    servicios_count = reserva.servicios.count()
                    if servicios_count == 0:
                        servicios_count = 1  # Al menos un servicio por defecto
                    
                    suscripcion_activa.servicios_utilizados_mes += servicios_count
                    suscripcion_activa.save()
                    print(f"✅ Servicios utilizados actualizados: {suscripcion_activa.servicios_utilizados_mes}/{suscripcion_activa.plan.cantidad_servicios_mes if suscripcion_activa.plan.cantidad_servicios_mes > 0 else 'Ilimitado'}")
                
                messages.success(request, 'Reserva creada con éxito.')
                return redirect('citas')
    else:
        form = ReservaForm()

    # Generar lista de fechas disponibles
    fechas_disponibles = [hoy + timedelta(days=i) for i in range(15)] 

    # Renderiza la vista con los datos necesarios
    return render(request, 'reservas/citas.html', {
        'reservas_pendientes': reservas_pendientes,
        'reservas_completadas': reservas_completadas,
        'total_reservas': total_reservas,
        'servicios': servicios,
        'empresas': empresas,
        'horas_disponibles': horas_disponibles,
        'fechas_disponibles': fechas_disponibles,
        'hoy': hoy,
    })

# =============================================================================
# NUEVAS VISTAS PARA LA GESTIÓN AVANZADA DE CITAS
# =============================================================================

@login_required
def obtener_detalles_reserva(request, reserva_id):
    """Vista AJAX para obtener detalles completos de una reserva"""
    try:
        reserva = get_object_or_404(Reserva, id_reserva=reserva_id, usuario=request.user)
        
        # Obtener los servicios asociados
        servicios_data = []
        total_precio = 0
        for servicio in reserva.servicios.all():
            servicios_data.append({
                'nombre': servicio.nombre_servicio,
                'descripcion': servicio.descripcion,
                'precio': float(servicio.precio)
            })
            total_precio += float(servicio.precio)
        
        # Formatear fecha en español
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        fecha_obj = reserva.fecha
        fecha_formateada = f"{dias_semana[fecha_obj.weekday()]}, {fecha_obj.day} de {meses[fecha_obj.month - 1]} de {fecha_obj.year}"
        
        # Formatear hora a 12h
        hora_formateada = reserva.hora.strftime('%I:%M %p')
        
        reserva_data = {
            'id': reserva.id_reserva,
            'empresa': {
                'nombre': reserva.empresa.nombre_empresa,
                'direccion': reserva.empresa.direccion,
                'telefono': reserva.empresa.telefono,
                'email': reserva.empresa.email
            },
            'fecha': fecha_formateada,
            'fecha_original': str(reserva.fecha),
            'hora': hora_formateada,
            'hora_original': str(reserva.hora),
            'estado': reserva.estado,
            'servicios': servicios_data,
            'total': total_precio,
            'es_pago_individual': reserva.es_pago_individual,
            'suscripcion_info': {
                'utilizada': reserva.suscripcion_utilizada is not None,
                'plan_nombre': reserva.suscripcion_utilizada.plan.nombre if reserva.suscripcion_utilizada else None
            } if reserva.suscripcion_utilizada else None
        }
        
        return JsonResponse({
            'success': True,
            'reserva': reserva_data
        })
        
    except Reserva.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Reserva no encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener detalles: {str(e)}'
        })

@login_required
def cancelar_reserva(request, reserva_id):
    """Vista AJAX para cancelar una reserva"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        reserva = get_object_or_404(Reserva, id_reserva=reserva_id, usuario=request.user)
        
        # Verificar que la reserva se pueda cancelar (no esté completada)
        if reserva.estado == 'completado':
            return JsonResponse({
                'success': False,
                'message': 'No se puede cancelar una reserva que ya está completada'
            })
        
        if reserva.estado == 'cancelada':
            return JsonResponse({
                'success': False,
                'message': 'Esta reserva ya está cancelada'
            })
        
        # Verificar que la cancelación sea con al menos 24 horas de anticipación
        from django.utils import timezone
        ahora = timezone.now()
        fecha_hora_reserva = timezone.make_aware(
            datetime.combine(reserva.fecha, reserva.hora)
        )
        
        if fecha_hora_reserva <= ahora + timedelta(hours=24):
            return JsonResponse({
                'success': False,
                'message': 'Las reservas deben cancelarse con al menos 24 horas de anticipación'
            })
        
        # Si la reserva utiliza suscripción, devolver los servicios
        if reserva.suscripcion_utilizada and not reserva.es_pago_individual:
            suscripcion = reserva.suscripcion_utilizada
            servicios_count = reserva.servicios.count()
            if servicios_count == 0:
                servicios_count = 1
            
            # Restar los servicios del contador (devolver servicios)
            suscripcion.servicios_utilizados_mes = max(0, suscripcion.servicios_utilizados_mes - servicios_count)
            suscripcion.save()
        
        # Cambiar estado a cancelada
        reserva.estado = 'cancelada'
        reserva.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Reserva cancelada exitosamente'
        })
        
    except Reserva.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Reserva no encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cancelar reserva: {str(e)}'
        })

@login_required
def editar_reserva(request, reserva_id):
    """Vista para editar una reserva existente"""
    try:
        reserva = get_object_or_404(Reserva, id_reserva=reserva_id, usuario=request.user)
        
        # Verificar que la reserva se pueda editar
        if reserva.estado != 'pendiente':
            messages.error(request, 'Solo se pueden editar reservas pendientes')
            return redirect('citas')
        
        # Verificar que la edición sea con al menos 24 horas de anticipación
        from django.utils import timezone
        ahora = timezone.now()
        fecha_hora_reserva = timezone.make_aware(
            datetime.combine(reserva.fecha, reserva.hora)
        )
        
        if fecha_hora_reserva <= ahora + timedelta(hours=24):
            messages.error(request, 'Las reservas deben editarse con al menos 24 horas de anticipación')
            return redirect('citas')
        
        if request.method == 'POST':
            # Procesar la edición de la reserva
            nueva_fecha = request.POST.get('fecha')
            nueva_hora_12h = request.POST.get('hora')
            nueva_empresa_id = request.POST.get('empresa')
            
            # Validaciones
            if not nueva_fecha or not nueva_hora_12h or not nueva_empresa_id:
                messages.error(request, 'Todos los campos son obligatorios')
                return redirect('editar_reserva', reserva_id=reserva_id)
            
            try:
                nueva_empresa = Empresa.objects.get(id_empresa=nueva_empresa_id)
                nueva_hora_24h = convertir_hora_24h(nueva_hora_12h)
                fecha_obj = datetime.strptime(nueva_fecha, '%Y-%m-%d').date()
                
                # Verificar disponibilidad de la nueva fecha/hora
                reserva_existente = Reserva.objects.filter(
                    empresa=nueva_empresa,
                    fecha=fecha_obj,
                    hora=nueva_hora_24h
                ).exclude(id_reserva=reserva_id).exists()
                
                if reserva_existente:
                    messages.error(request, 'La fecha y hora seleccionadas ya están ocupadas')
                    return redirect('editar_reserva', reserva_id=reserva_id)
                
                # Actualizar la reserva
                reserva.empresa = nueva_empresa
                reserva.fecha = fecha_obj
                reserva.hora = nueva_hora_24h
                reserva.save()
                
                messages.success(request, 'Reserva actualizada exitosamente')
                return redirect('citas')
                
            except (Empresa.DoesNotExist, ValueError) as e:
                messages.error(request, 'Datos inválidos proporcionados')
                return redirect('editar_reserva', reserva_id=reserva_id)
        
        # GET request: mostrar formulario de edición
        context = {
            'reserva': reserva,
            'empresas': Empresa.objects.filter(verificada=True),
        }
        return render(request, 'reservas/editar_reserva.html', context)
        
    except Reserva.DoesNotExist:
        messages.error(request, 'Reserva no encontrada')
        return redirect('citas')

@login_required
def repetir_reserva(request, reserva_id):
    """Vista para repetir una reserva completada"""
    try:
        reserva_original = get_object_or_404(Reserva, id_reserva=reserva_id, usuario=request.user)
        
        # Solo permitir repetir reservas completadas
        if reserva_original.estado != 'completado':
            messages.error(request, 'Solo se pueden repetir reservas completadas')
            return redirect('citas')
        
        # Redirigir a la página de reservas con los datos pre-cargados
        servicios_ids = list(reserva_original.servicios.values_list('id_servicio', flat=True))
        params = {
            'empresa': reserva_original.empresa.id_empresa,
            'servicios': ','.join(map(str, servicios_ids)),
            'repetir': 'true'
        }
        
        from urllib.parse import urlencode
        url = f"/reservas/?{urlencode(params, doseq=True)}"
        messages.info(request, 'Selecciona la nueva fecha y hora para tu cita')
        return redirect(url)
        
    except Reserva.DoesNotExist:
        messages.error(request, 'Reserva no encontrada')
        return redirect('citas')

@login_required
def calificar_servicio(request, reserva_id):
    """Vista para calificar un servicio completado"""
    try:
        reserva = get_object_or_404(Reserva, id_reserva=reserva_id, usuario=request.user)
        
        # Solo permitir calificar reservas completadas
        if reserva.estado != 'completado':
            messages.error(request, 'Solo se pueden calificar reservas completadas')
            return redirect('citas')
        
        if request.method == 'POST':
            calificacion = request.POST.get('calificacion')
            comentario_texto = request.POST.get('comentario', '')
            
            if not calificacion:
                messages.error(request, 'Debes seleccionar una calificación')
                return redirect('calificar_servicio', reserva_id=reserva_id)
            
            try:
                # Crear comentario con calificación
                comentario = Comentario.objects.create(
                    comentario=f"Calificación: {calificacion}/5 estrellas. {comentario_texto}".strip(),
                    usuario=request.user
                )
                
                messages.success(request, 'Gracias por tu calificación!')
                return redirect('citas')
                
            except Exception as e:
                messages.error(request, 'Error al guardar la calificación')
                return redirect('calificar_servicio', reserva_id=reserva_id)
        
        # GET request: mostrar formulario de calificación
        context = {
            'reserva': reserva,
        }
        return render(request, 'servicios/calificar_servicio.html', context)
        
    except Reserva.DoesNotExist:
        messages.error(request, 'Reserva no encontrada')
        return redirect('citas')

@login_required
def get_empresas_verificadas(request):
    """Vista AJAX para obtener empresas verificadas"""
    try:
        empresas = Empresa.objects.filter(verificada=True).values(
            'id_empresa', 'nombre_empresa', 'direccion'
        )
        
        empresas_data = []
        for empresa in empresas:
            empresas_data.append({
                'id': empresa['id_empresa'],
                'nombre': empresa['nombre_empresa'],
                'direccion': empresa['direccion']
            })
        
        return JsonResponse({
            'success': True,
            'empresas': empresas_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener empresas: {str(e)}'
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

    return render(request, 'pages_informativas/contacto.html') 

def resetCorreo(request):
    return render(request, 'auth/reset_correo.html')
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
            
            # Si es una solicitud AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Tu comentario ha sido publicado exitosamente.',
                    'comentario_id': comentario.id_comentario,
                    'usuario': comentario.usuario.username,
                    'texto': comentario.comentario,
                    'fecha': comentario.fecha.strftime('%d/%m/%Y %H:%M')
                })
            else:
                messages.success(request, "Tu comentario ha sido publicado exitosamente.")
                return redirect('comentarios')
        else:
            # Si es AJAX y hay errores
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Hubo un error al procesar tu comentario.'
                })

    else:
        form = ComentarioClienteForm()

    return render(request, 'comentarios/comentarios.html', {'form': form})






############################################################ comienzo de crud


def login_crud(request):
    # Si ya está logueado como admin, redirigir al home de admin
    if request.user.is_authenticated and hasattr(request.user, 'rol') and request.user.rol == 'admin':
        return redirect('homecrud')
    
    if request.method == 'POST':
        nombre_usuario = request.POST['nombre_usuario']
        contrasena = request.POST['contrasena']
        tipo_usuario = request.POST.get('tipo_usuario', 'admin')  # Por defecto admin
        
        print(f"🔍 Intento de login - Tipo: {tipo_usuario}, Usuario: {nombre_usuario}")
        
        if tipo_usuario == 'admin':
            # Verificar si el usuario existe y está activo
            try:
                usuario_check = Usuario.objects.get(nombre_usuario=nombre_usuario)
                if not usuario_check.is_active:
                    messages.error(request, 'Tu cuenta de administrador ha sido desactivada. Contacta al superadministrador.')
                    return redirect('logincrud')
            except Usuario.DoesNotExist:
                pass  # El usuario no existe, se manejará en la autenticación
            
            # Autenticación del administrador
            usuario = authenticate(request, username=nombre_usuario, password=contrasena)
            
            if usuario is not None:
                # Verificar si el usuario tiene rol de admin y está activo
                if hasattr(usuario, 'rol') and usuario.rol == 'admin' and usuario.is_active:
                    auth_login(request, usuario)  # Iniciar sesión con el usuario autenticado
                    messages.success(request, f'Bienvenido administrador, {usuario.nombre_usuario}!')
                    return redirect('homecrud')
                elif not usuario.is_active:
                    messages.error(request, 'Tu cuenta de administrador ha sido desactivada. Contacta al superadministrador.')
                    return redirect('logincrud')
                else:
                    messages.error(request, 'Acceso denegado. Solo los administradores pueden acceder.')
                    return redirect('logincrud')
            else:
                messages.error(request, 'Usuario o contraseña de administrador incorrectos.')
                return redirect('logincrud')
                
        elif tipo_usuario == 'empresa':
            # Autenticación de empresa
            try:
                # Buscar la empresa por email (usando nombre_usuario como email)
                empresa = Empresa.objects.get(email=nombre_usuario)
                
                # Verificar la contraseña
                if check_password(contrasena, empresa.contrasena):
                    # Verificar si la empresa está verificada
                    if empresa.verificada:
                        # Guardar información de la empresa en la sesión
                        request.session['empresa_id'] = empresa.id_empresa
                        request.session['empresa_nombre'] = empresa.nombre_empresa
                        request.session['empresa_email'] = empresa.email
                        request.session['es_empresa'] = True
                        
                        messages.success(request, f'Bienvenida empresa {empresa.nombre_empresa}!')
                        return redirect('home_empresas')  # Redirigir al home de empresas
                    else:
                        messages.warning(request, 'Su empresa aún no ha sido verificada. Por favor, espere la verificación de un administrador.')
                        return redirect('logincrud')
                else:
                    messages.error(request, 'Contraseña de empresa incorrecta.')
                    return redirect('logincrud')
                    
            except Empresa.DoesNotExist:
                messages.error(request, 'Email de empresa no encontrado. Verifique el correo electrónico.')
                return redirect('logincrud')
            except Exception as e:
                print(f"❌ Error en login de empresa: {str(e)}")
                messages.error(request, 'Error interno. Intente nuevamente.')
                return redirect('logincrud')
        else:
            messages.error(request, 'Tipo de usuario no válido.')
            return redirect('logincrud')
    
    return render(request, 'auth/login_crud.html')
    

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
    
    return render(request, 'comentarios/comentarios_crud.html', context)




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
    return render(request, 'comentarios/quejas_crud.html', {'quejas': quejas, 'form': form})



@admin_required
def usuarios_crud(request):
    # Obtener el tipo de usuarios a mostrar (activos o inactivos)
    tab = request.GET.get('tab', 'activos')
    
    if tab == 'inactivos':
        usuarios = Usuario.objects.filter(is_active=False)
    else:
        usuarios = Usuario.objects.filter(is_active=True)
    
    form = UsuariosForm() 

    # Calcular estadísticas GENERALES (todos los usuarios)
    todos_usuarios = Usuario.objects.all()
    total_usuarios = todos_usuarios.filter(is_active=True).count()
    total_usuarios_inactivos = todos_usuarios.filter(is_active=False).count()
    total_admins = todos_usuarios.filter(rol='admin', is_active=True).count()
    total_clientes = todos_usuarios.filter(rol='cliente', is_active=True).count()

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
        # Manejar la inactivación de los usuarios
        if 'eliminar' in request.POST:
            usuario_id  = request.POST.get('eliminar')
            usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
            usuario.is_active = False
            usuario.save()
            messages.success(request, 'El usuario ha sido inactivado.')
            return redirect('usuarioscrud')
        
        # Manejar la reactivación de los usuarios
        if 'reactivar' in request.POST:
            usuario_id  = request.POST.get('reactivar')
            usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
            usuario.is_active = True
            usuario.save()
            messages.success(request, 'El usuario ha sido reactivado.')
            return redirect('usuarioscrud?tab=activos')
        
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
        'total_usuarios_inactivos': total_usuarios_inactivos,
        'total_admins': total_admins,
        'total_clientes': total_clientes,
        'tab_actual': tab,
    }

    return render(request, 'usuarios/usuarios_crud.html', context)

@admin_required
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    if request.method == 'POST':
        form = UsuariosForm(request.POST, instance=usuario)
        if form.is_valid():
            # Manejar la actualización de contraseña si se proporciona
            contrasena1 = request.POST.get('contrasena1')
            contrasena2 = request.POST.get('contrasena2')
            
            # Solo actualizar la contraseña si se proporciona una nueva
            if contrasena1:
                if contrasena1 == contrasena2:
                    usuario.password = make_password(contrasena1)
                else:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return render(request, 'editar_usuario.html', {'form': form, 'usuario': usuario})
            
            # Guardar el formulario sin la contraseña primero
            usuario_actualizado = form.save(commit=False)
            
            # Concatenar el prefijo "57" al teléfono si no lo tiene ya
            telefono = usuario_actualizado.telefono
            if telefono and not telefono.startswith('57'):
                usuario_actualizado.telefono = '57' + telefono
            
            usuario_actualizado.save()
            messages.success(request, 'El usuario ha sido actualizado correctamente.')
            return redirect('usuarioscrud')
    else:
        # Remover el prefijo "57" del teléfono para mostrar solo el número local
        initial_data = {
            'nombre_completo': usuario.nombre_completo,
            'nombre_usuario': usuario.nombre_usuario,
            'correo': usuario.correo,
            'telefono': usuario.telefono[2:] if usuario.telefono and usuario.telefono.startswith('57') else usuario.telefono,
            'direccion': usuario.direccion,
            'rol': usuario.rol,
        }
        form = UsuariosForm(initial=initial_data)
    
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})

@admin_required
def citas_crud(request):
    # Auto-completar reservas vencidas (más de 4 horas después de la cita)
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Q
    
    ahora = timezone.now()
    hace_4_horas = ahora - timedelta(hours=4)
    
    # Buscar y actualizar reservas pendientes que ya pasaron más de 4 horas
    # Usando una consulta más eficiente con datetime combinado
    reservas_a_completar = Reserva.objects.filter(
        estado='pendiente'
    )
    
    # Filtrar manualmente las que ya pasaron 4 horas
    reservas_vencidas = []
    for reserva in reservas_a_completar:
        try:
            # Crear datetime combinando fecha y hora de la reserva
            fecha_hora_reserva = timezone.make_aware(
                datetime.combine(reserva.fecha, reserva.hora),
                timezone.get_current_timezone()
            )
            
            # Verificar si ya pasaron 4 horas
            if fecha_hora_reserva <= hace_4_horas:
                reservas_vencidas.append(reserva.id_reserva)
        except Exception:
            # Si hay error con alguna fecha, continuar con la siguiente
            continue
    
    # Actualizar todas las reservas vencidas de una vez
    reservas_actualizadas = 0
    if reservas_vencidas:
        reservas_actualizadas = Reserva.objects.filter(
            id_reserva__in=reservas_vencidas,
            estado='pendiente'
        ).update(estado='completado')
    
    # Mostrar mensaje si se completaron reservas automáticamente
    if reservas_actualizadas > 0:
        messages.info(
            request, 
            f"✅ {reservas_actualizadas} reserva{'s' if reservas_actualizadas != 1 else ''} fueron marcadas automáticamente como completadas por haber pasado más de 4 horas."
        )
        # Log para debugging (opcional)
        print(f"🔄 Auto-completado: {reservas_actualizadas} reservas marcadas como completadas automáticamente")
    
    hoy = ahora.date()
    
    # Inicializar el queryset de reservas (ordenadas por más recientes primero)
    reservas = Reserva.objects.select_related('empresa', 'usuario').prefetch_related('reservaservicio_set__servicio').order_by('-fecha', '-hora')
    servicios = Servicio.objects.all() 
    empresas = Empresa.objects.all()
    
    # Aplicar filtros basados en los parámetros GET
    filtros_aplicados = {}
    
    # Filtro por empresa
    empresa_id = request.GET.get('empresa')
    if empresa_id:
        reservas = reservas.filter(empresa_id=empresa_id)
        filtros_aplicados['empresa'] = empresa_id
    
    # Filtro por servicio
    servicio_id = request.GET.get('servicio')
    if servicio_id:
        reservas = reservas.filter(servicios__id_servicio=servicio_id)
        filtros_aplicados['servicio'] = servicio_id
    
    # Filtro por estado
    estado = request.GET.get('estado')
    if estado:
        if estado == 'no_completado':
            reservas = reservas.filter(estado='pendiente')
        elif estado == 'completado':
            reservas = reservas.filter(estado='completado')
        elif estado == 'cancelada':
            reservas = reservas.filter(estado='cancelada')
        filtros_aplicados['estado'] = estado
    # Nota: Removido el filtro por defecto para mostrar todas las citas
    
    # Filtro por cliente (nombre)
    cliente = request.GET.get('cliente')
    if cliente:
        reservas = reservas.filter(usuario__nombre_completo__icontains=cliente)
        filtros_aplicados['cliente'] = cliente
    
    # Filtro por fecha desde
    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        reservas = reservas.filter(fecha__gte=fecha_desde)
        filtros_aplicados['fecha_desde'] = fecha_desde
    
    # Filtro por fecha hasta
    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        reservas = reservas.filter(fecha__lte=fecha_hasta)
        filtros_aplicados['fecha_hasta'] = fecha_hasta
    
    # Filtro por nombre de usuario
    usuario = request.GET.get('usuario')
    if usuario:
        reservas = reservas.filter(usuario__nombre_usuario__icontains=usuario)
        filtros_aplicados['usuario'] = usuario
    
    # Filtro por ID de cita
    id_cita = request.GET.get('id_cita')
    if id_cita:
        reservas = reservas.filter(id_reserva=id_cita)
        filtros_aplicados['id_cita'] = id_cita

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
            hora_formateada_24h = f"{h:01}:00"

            # Si la fecha es hoy, verifica que la hora no haya pasado
            if fecha == hoy and h < ahora.hour:
                continue  # Ignora horas pasadas para hoy

            # Verifica si la hora está ocupada en la fecha seleccionada
            if hora_formateada_24h not in ocupadas["horas"].get(fecha, set()):
                # Convertir a formato 12h con AM/PM para mostrar al usuario
                hora_12h = convertir_hora_12h(hora_formateada_24h)
                horas_disponibles[fecha].append(hora_12h)

    if request.method == "POST":
        # Manejar la cancelación de reservas
        if 'eliminar' in request.POST:
            reserva_id = request.POST.get('eliminar')
            reserva = get_object_or_404(Reserva, id_reserva=reserva_id)
            
            # Si la reserva utiliza suscripción, devolver los servicios utilizados
            if reserva.suscripcion_utilizada and not reserva.es_pago_individual:
                suscripcion = reserva.suscripcion_utilizada
                servicios_count = reserva.servicios.count()
                if servicios_count == 0:
                    servicios_count = 1  # Al menos un servicio por defecto
                
                # Restar los servicios del contador (devolver servicios)
                suscripcion.servicios_utilizados_mes = max(0, suscripcion.servicios_utilizados_mes - servicios_count)
                suscripcion.save()
                print(f"✅ Servicios devueltos a la suscripción (Admin). Servicios utilizados: {suscripcion.servicios_utilizados_mes}/{suscripcion.plan.cantidad_servicios_mes if suscripcion.plan.cantidad_servicios_mes > 0 else 'Ilimitado'}")
            
            # Cambiar estado a cancelada en lugar de eliminar
            reserva.estado = 'cancelada'
            reserva.save()
            messages.success(request, 'Reserva cancelada con éxito.')
            return redirect('citascrud')

        # Manejar la creación o edición de reservas
        if 'id_reserva' in request.POST:  # Para editar
            reserva_id = request.POST.get('id_reserva')
            reserva = get_object_or_404(Reserva, id_reserva=reserva_id)

            # Actualizar los datos de la reserva
            empresa_id = request.POST.get('empresa')
            fecha = request.POST.get('fecha')
            hora_12h = request.POST.get('hora')
            servicio_id = request.POST.get('servicio')

            if empresa_id:
                empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
                reserva.empresa = empresa
            
            if fecha:
                reserva.fecha = fecha
            
            if hora_12h:
                # Convertir hora de 12h a 24h antes de guardar
                reserva.hora = convertir_hora_24h(hora_12h)
            
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
                # En el caso del admin, usar el usuario logueado como fallback
                if not reserva.usuario:
                    reserva.usuario = request.user
                
                # Verificar si el usuario de la reserva tiene una suscripción activa
                suscripcion_activa = None
                tiene_suscripcion = False
                
                try:
                    from .models import SuscripcionUsuario
                    suscripcion_activa = SuscripcionUsuario.objects.filter(
                        usuario=reserva.usuario,
                        estado='activa'
                    ).first()
                    
                    if suscripcion_activa and suscripcion_activa.esta_activa():
                        tiene_suscripcion = True
                        # Verificar si puede usar más servicios este mes
                        if not suscripcion_activa.puede_usar_servicio():
                            messages.error(request, f"El usuario {reserva.usuario.nombre_usuario} ha agotado sus servicios del mes. Servicios restantes: {suscripcion_activa.servicios_restantes()}")
                            return redirect('citascrud')
                except Exception as e:
                    print(f"Error verificando suscripción: {e}")
                
                reserva.suscripcion_utilizada = suscripcion_activa if tiene_suscripcion else None
                reserva.es_pago_individual = not tiene_suscripcion
                reserva.save()
                
                # Si tiene suscripción activa, incrementar el contador de servicios utilizados
                if tiene_suscripcion and suscripcion_activa:
                    # Contar los servicios asociados a esta reserva
                    servicios_count = reserva.servicios.count()
                    if servicios_count == 0:
                        servicios_count = 1  # Al menos un servicio por defecto
                    
                    suscripcion_activa.servicios_utilizados_mes += servicios_count
                    suscripcion_activa.save()
                    print(f"✅ Servicios utilizados actualizados (Admin): {suscripcion_activa.servicios_utilizados_mes}/{suscripcion_activa.plan.cantidad_servicios_mes if suscripcion_activa.plan.cantidad_servicios_mes > 0 else 'Ilimitado'}")
                
                messages.success(request, 'Reserva creada con éxito.')
                return redirect('citascrud')
    else:
        form = ReservaForm()

    # Generar lista de fechas disponibles
    fechas_disponibles = [hoy + timedelta(days=i) for i in range(15)] 

    # Para las estadísticas, necesitamos todas las reservas sin filtrar (ordenadas por más recientes primero)
    todas_las_reservas = Reserva.objects.select_related('empresa', 'usuario').prefetch_related('reservaservicio_set__servicio').order_by('-fecha', '-hora')

    # Renderiza la vista con los datos necesarios
    return render(request, 'reservas/citas_crud.html', {
        'reservas': reservas,
        'todas_las_reservas': todas_las_reservas,  # Para las estadísticas
        'form': form,
        'servicios': servicios,
        'empresas': empresas,
        'horas_disponibles': horas_disponibles,
        'fechas_disponibles': fechas_disponibles,
        'hoy': hoy,
        'filtros_aplicados': filtros_aplicados,
    })


@admin_required
def crear_cita_admin(request):
    """Vista para que el administrador cree citas desde el CRUD"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    ahora = timezone.now()
    hoy = ahora.date()
    servicios = Servicio.objects.all()
    empresas = Empresa.objects.filter(verificada=True)
    usuarios = User.objects.filter(is_superuser=False)  # Obtener usuarios no admin
    
    # Obtener reservas existentes para calcular horas ocupadas
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
        usuario_id = request.POST.get('usuario')
        empresa_id = request.POST.get('empresa')
        fecha_seleccionada = request.POST.get('fecha')
        hora_12h = request.POST.get('hora')
        servicios_ids = request.POST.getlist('servicios')
        
        # Validaciones
        if not usuario_id:
            messages.error(request, "Debes seleccionar un usuario.")
            return redirect('crear_cita_admin')
            
        if not empresa_id:
            messages.error(request, "Debes seleccionar una empresa.")
            return redirect('crear_cita_admin')
            
        if not fecha_seleccionada:
            messages.error(request, "Debes seleccionar una fecha.")
            return redirect('crear_cita_admin')
            
        if not hora_12h:
            messages.error(request, "Debes seleccionar una hora.")
            return redirect('crear_cita_admin')
            
        if not servicios_ids:
            messages.error(request, "Debes seleccionar al menos un servicio.")
            return redirect('crear_cita_admin')
        
        try:
            usuario = User.objects.get(id=usuario_id)
            empresa = Empresa.objects.get(id_empresa=empresa_id)
            servicios_seleccionados = Servicio.objects.filter(id_servicio__in=servicios_ids)
            
            if len(servicios_seleccionados) != len(servicios_ids):
                messages.error(request, "Uno o más servicios seleccionados no existen.")
                return redirect('crear_cita_admin')
            
            # Convertir hora a formato 24h
            hora = convertir_hora_24h(hora_12h)
            
            # Verificar si la fecha y hora están ocupadas
            fecha_obj = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()
            if fecha_obj in ocupadas["fechas"] and hora in ocupadas["horas"].get(fecha_obj, set()):
                messages.error(request, f"La fecha {fecha_seleccionada} a las {hora_12h} ya está ocupada.")
                return redirect('crear_cita_admin')
            
            # Verificar suscripción del usuario
            suscripcion_activa = None
            usar_suscripcion = False
            
            try:
                from .models import SuscripcionUsuario
                suscripcion_activa = SuscripcionUsuario.objects.filter(
                    usuario=usuario,
                    estado='activa'
                ).first()
                
                if suscripcion_activa and suscripcion_activa.esta_activa():
                    if suscripcion_activa.puede_usar_servicio():
                        usar_suscripcion = True
            except Exception as e:
                print(f"Error verificando suscripción: {e}")
            
            # Crear la reserva
            reserva = Reserva(
                empresa=empresa,
                fecha=fecha_seleccionada,
                hora=hora,
                usuario=usuario,
                suscripcion_utilizada=suscripcion_activa if usar_suscripcion else None,
                es_pago_individual=not usar_suscripcion
            )
            reserva.save()
            
            # Crear las relaciones entre reserva y servicios
            precio_total = 0
            servicios_nombres = []
            for servicio in servicios_seleccionados:
                ReservaServicio.objects.create(reserva=reserva, servicio=servicio)
                precio_total += servicio.precio
                servicios_nombres.append(servicio.nombre_servicio)
            
            # Si usa suscripción, incrementar el contador
            if usar_suscripcion and suscripcion_activa:
                suscripcion_activa.servicios_utilizados_mes += len(servicios_seleccionados)
                suscripcion_activa.save()
            
            messages.success(request, f"Cita creada exitosamente para {usuario.nombre_usuario} el {fecha_seleccionada} a las {hora_12h}.")
            return redirect('citascrud')
            
        except User.DoesNotExist:
            messages.error(request, "El usuario seleccionado no existe.")
        except Empresa.DoesNotExist:
            messages.error(request, "La empresa seleccionada no existe.")
        except Exception as e:
            messages.error(request, f"Error al crear la cita: {str(e)}")
        
        return redirect('crear_cita_admin')
    
    # Generar fechas disponibles (próximos 15 días)
    fechas_disponibles = []
    for i in range(15):
        fecha = hoy + timedelta(days=i)
        fechas_disponibles.append(fecha)
    
    # Generar horas disponibles (8:00 AM a 3:00 PM)
    horas_disponibles = []
    for h in range(8, 16):
        hora_24h = f"{h:02d}:00"
        hora_12h = convertir_hora_12h(hora_24h)
        horas_disponibles.append({
            'valor': hora_12h,
            'texto': hora_12h
        })
    
    context = {
        'servicios': servicios,
        'empresas': empresas,
        'usuarios': usuarios,
        'fechas_disponibles': fechas_disponibles,
        'horas_disponibles': horas_disponibles,
        'ocupadas': ocupadas,
    }
    
    return render(request, 'reservas/crear_cita_admin.html', context)






@admin_required
def cambiar_estado_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id_reserva=reserva_id)
    
    if reserva.estado == 'pendiente':
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
    
    # Obtener solicitudes de servicios pendientes
    solicitudes_servicios = SolicitudServicioEmpresa.objects.filter(estado='pendiente').select_related('empresa', 'servicio_solicitado')

    # Calcular estadísticas
    total_asignaciones = EmpresaServicio.objects.count()
    total_solicitudes_pendientes = solicitudes_servicios.count()

    # Filtrar según los parámetros de búsqueda
    nombre_servicio = request.GET.get('nombre_servicio', '')
    if nombre_servicio:
        servicios = servicios.filter(nombre_servicio__icontains=nombre_servicio)

    if request.method == "POST":
        # Manejar aprobación/rechazo de solicitudes
        if 'aprobar_solicitud' in request.POST:
            solicitud_id = request.POST.get('aprobar_solicitud')
            try:
                solicitud = get_object_or_404(SolicitudServicioEmpresa, id_solicitud=solicitud_id)
                resultado = solicitud.aprobar_solicitud()
                if resultado:
                    messages.success(request, f'Solicitud de {solicitud.empresa.nombre_empresa} para el servicio {solicitud.servicio_solicitado.nombre_servicio} aprobada exitosamente.')
                else:
                    messages.info(request, f'Solicitud de {solicitud.empresa.nombre_empresa} procesada. La empresa ya tenía acceso al servicio {solicitud.servicio_solicitado.nombre_servicio}.')
            except Exception as e:
                messages.error(request, f'Error al aprobar la solicitud: {str(e)}')
            return redirect('servicioscrud')

        if 'rechazar_solicitud' in request.POST:
            solicitud_id = request.POST.get('rechazar_solicitud')
            motivo = request.POST.get('motivo_rechazo', 'Solicitud rechazada por el administrador')
            try:
                solicitud = get_object_or_404(SolicitudServicioEmpresa, id_solicitud=solicitud_id)
                solicitud.rechazar_solicitud(motivo)
                messages.warning(request, f'Solicitud de {solicitud.empresa.nombre_empresa} para el servicio {solicitud.servicio_solicitado.nombre_servicio} rechazada.')
            except Exception as e:
                messages.error(request, f'Error al rechazar la solicitud: {str(e)}')
            return redirect('servicioscrud')

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
        'total_asignaciones': total_asignaciones,
        'solicitudes_servicios': solicitudes_servicios,
        'total_solicitudes_pendientes': total_solicitudes_pendientes
    }

    return render(request, 'servicios/servicios_crud.html', context)


@admin_required
def crear_servicio(request):
    """Vista para crear un nuevo servicio"""
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio creado exitosamente.')
            return redirect('servicioscrud')
        else:
            messages.error(request, 'Error al crear el servicio. Verifica los datos ingresados.')
    else:
        form = ServicioForm()

    return render(request, 'servicios/crear_servicio.html', {'form': form})


@admin_required
def editar_servicio(request, servicio_id):
    """Vista para editar un servicio existente"""
    servicio = get_object_or_404(Servicio, id_servicio=servicio_id)
    
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, f'Servicio "{servicio.nombre_servicio}" actualizado exitosamente.')
            return redirect('servicioscrud')
        else:
            messages.error(request, 'Error al actualizar el servicio. Verifica los datos ingresados.')
    else:
        form = ServicioForm(instance=servicio)
    
    return render(request, 'servicios/editar_servicio.html', {'form': form, 'servicio': servicio})


@admin_required
def eliminar_servicio(request, servicio_id):
    """Vista para eliminar un servicio"""
    servicio = get_object_or_404(Servicio, id_servicio=servicio_id)
    
    if request.method == 'POST':
        nombre_servicio = servicio.nombre_servicio
        servicio.delete()
        messages.success(request, f'Servicio "{nombre_servicio}" eliminado exitosamente.')
        return redirect('servicioscrud')
    
    return render(request, 'servicios/eliminar_servicio.html', {'servicio': servicio})


@admin_required
def gestionar_asignaciones_servicios(request):
    """Vista para gestionar las asignaciones de servicios a empresas"""
    empresas = Empresa.objects.all().order_by('nombre_empresa')
    servicios = Servicio.objects.all().order_by('nombre_servicio')
    asignaciones = EmpresaServicio.objects.select_related('empresa', 'servicio').all()
    
    # Crear diccionario para manejo eficiente de asignaciones
    asignaciones_dict = {}
    for asignacion in asignaciones:
        if asignacion.empresa.id_empresa not in asignaciones_dict:
            asignaciones_dict[asignacion.empresa.id_empresa] = []
        asignaciones_dict[asignacion.empresa.id_empresa].append(asignacion.servicio.id_servicio)
    
    # Filtros
    empresa_filtro = request.GET.get('empresa_filtro', '')
    servicio_filtro = request.GET.get('servicio_filtro', '')
    
    if empresa_filtro:
        empresas = empresas.filter(nombre_empresa__icontains=empresa_filtro)
    
    if servicio_filtro:
        servicios = servicios.filter(nombre_servicio__icontains=servicio_filtro)
    
    # Procesar formulario de asignación masiva
    if request.method == 'POST':
        if 'asignacion_masiva' in request.POST:
            empresa_id = request.POST.get('empresa_id')
            servicios_ids = request.POST.getlist('servicios')
            
            if empresa_id and servicios_ids:
                empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
                
                # Eliminar asignaciones actuales
                EmpresaServicio.objects.filter(empresa=empresa).delete()
                
                # Crear nuevas asignaciones
                for servicio_id in servicios_ids:
                    servicio = get_object_or_404(Servicio, id_servicio=servicio_id)
                    EmpresaServicio.objects.create(empresa=empresa, servicio=servicio)
                
                messages.success(request, f'Servicios asignados exitosamente a {empresa.nombre_empresa}.')
                return redirect('gestionar_asignaciones_servicios')
        
        elif 'eliminar_asignacion' in request.POST:
            asignacion_ids = request.POST.getlist('asignaciones_eliminar')
            if asignacion_ids:
                count = EmpresaServicio.objects.filter(id__in=asignacion_ids).delete()[0]
                messages.success(request, f'{count} asignaciones eliminadas exitosamente.')
                return redirect('gestionar_asignaciones_servicios')
    
    # Estadísticas
    total_empresas = empresas.count()
    total_servicios = servicios.count()
    total_asignaciones = EmpresaServicio.objects.count()
    empresas_sin_servicios = empresas.exclude(id_empresa__in=asignaciones_dict.keys()).count()
    
    context = {
        'empresas': empresas,
        'servicios': servicios,
        'asignaciones': asignaciones,
        'asignaciones_dict': asignaciones_dict,
        'total_empresas': total_empresas,
        'total_servicios': total_servicios,
        'total_asignaciones': total_asignaciones,
        'empresas_sin_servicios': empresas_sin_servicios,
        'empresa_filtro': empresa_filtro,
        'servicio_filtro': servicio_filtro,
    }
    
    return render(request, 'empresas/gestionar_asignaciones_servicios.html', context)


@admin_required
def asignar_servicio_empresa(request, empresa_id):
    """Vista para asignar servicios específicos a una empresa"""
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
    servicios = Servicio.objects.all()
    servicios_asignados = EmpresaServicio.objects.filter(empresa=empresa).values_list('servicio_id', flat=True)
    
    if request.method == 'POST':
        servicios_ids = request.POST.getlist('servicios')
        
        # Eliminar asignaciones actuales
        EmpresaServicio.objects.filter(empresa=empresa).delete()
        
        # Crear nuevas asignaciones
        for servicio_id in servicios_ids:
            servicio = get_object_or_404(Servicio, id_servicio=servicio_id)
            EmpresaServicio.objects.create(empresa=empresa, servicio=servicio)
        
        messages.success(request, f'Servicios actualizados para {empresa.nombre_empresa}.')
        return redirect('gestionar_asignaciones_servicios')
    
    context = {
        'empresa': empresa,
        'servicios': servicios,
        'servicios_asignados': list(servicios_asignados),
    }
    
    return render(request, 'servicios/asignar_servicio_empresa.html', context)


@admin_required
def detalle_servicio(request, servicio_id):
    """Vista para ver el detalle de un servicio y sus empresas asignadas"""
    servicio = get_object_or_404(Servicio, id_servicio=servicio_id)
    empresas_asignadas = EmpresaServicio.objects.filter(servicio=servicio).select_related('empresa')
    reservas_servicio = ReservaServicio.objects.filter(servicio=servicio).select_related('reserva').count()
    
    # Estadísticas del servicio
    total_empresas_asignadas = empresas_asignadas.count()
    total_reservas = reservas_servicio
    
    context = {
        'servicio': servicio,
        'empresas_asignadas': empresas_asignadas,
        'total_empresas_asignadas': total_empresas_asignadas,
        'total_reservas': total_reservas,
    }
    
    return render(request, 'servicios/detalle_servicio.html', context)


@admin_required
def empresas_crud(request):
    empresas = Empresa.objects.all()
    form = EmpresaForm()  # Si estás usando un formulario de Django para crear y actualizar empresas

    # Filtrar según los parámetros de búsqueda
    nombre_empresa = request.GET.get('nombre_empresa', '')
    verificacion = request.GET.get('verificacion', '')

    if nombre_empresa:
        empresas = empresas.filter(nombre_empresa__icontains=nombre_empresa)
    
    if verificacion == 'verificada':
        empresas = empresas.filter(verificada=True)
    elif verificacion == 'sin_verificar':
        empresas = empresas.filter(verificada=False)

    if request.method == "POST":
        # Manejar la eliminación de empresas
        if 'eliminar' in request.POST:
            empresa_id = request.POST.get('eliminar')
            empresa_a_eliminar = get_object_or_404(Empresa, id_empresa=empresa_id)
            empresa_a_eliminar.delete()
            messages.error(request, 'La empresa ha sido eliminada.')
            return redirect('empresascrud')

        # Manejar el cambio de estado de verificación
        if 'cambiar_verificacion' in request.POST:
            empresa_id = request.POST.get('cambiar_verificacion')
            empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
            empresa.verificada = not empresa.verificada  # Cambiar el estado
            empresa.save()
            estado_mensaje = 'verificada' if empresa.verificada else 'sin verificar'
            messages.success(request, f'La empresa ha sido marcada como {estado_mensaje}.')
            return redirect('empresascrud')

        # Manejar la verificación de empresas
        if 'verificar' in request.POST:
            empresa_id = request.POST.get('verificar')
            empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
            empresa.verificada = True
            empresa.save()
            messages.success(request, f'La empresa "{empresa.nombre_empresa}" ha sido verificada exitosamente.')
            return redirect('empresascrud')

        # Manejar la desverificación de empresas
        if 'desverificar' in request.POST:
            empresa_id = request.POST.get('desverificar')
            empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
            empresa.verificada = False
            empresa.save()
            messages.warning(request, f'La empresa "{empresa.nombre_empresa}" ha sido desverificada.')
            return redirect('empresascrud')

        # Manejar la creación de una nueva empresa
        if 'nombre_empresa' in request.POST and 'id_empresa' not in request.POST:
            nombre_empresa = request.POST.get('nombre_empresa')
            direccion = request.POST.get('direccion')
            telefono = request.POST.get('telefono')
            email = request.POST.get('email')
            contrasena = request.POST.get('contrasena', 'temp_password')

            # Encriptar la contraseña si se proporciona
            if contrasena and contrasena != 'temp_password':
                contrasena_encriptada = make_password(contrasena)
            else:
                contrasena_encriptada = 'temp_password'

            nueva_empresa = Empresa(
                nombre_empresa=nombre_empresa,
                direccion=direccion,
                telefono=telefono,
                email=email,
                contrasena=contrasena_encriptada
            )
            nueva_empresa.save()
            messages.success(request, 'La empresa ha sido creada exitosamente.')
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
            nueva_contrasena = request.POST.get('contrasena')

            # Solo actualizar si se proporciona un nuevo valor
            if nuevo_nombre_empresa:
                empresa.nombre_empresa = nuevo_nombre_empresa
            if nueva_direccion:
                empresa.direccion = nueva_direccion
            if nuevo_telefono:
                empresa.telefono = nuevo_telefono
            if nuevo_email:
                empresa.email = nuevo_email
            if nueva_contrasena:
                empresa.contrasena = make_password(nueva_contrasena)

            empresa.save()
            messages.success(request, 'La empresa ha sido actualizada exitosamente.')
            return redirect('empresascrud')

    # Calcular estadísticas basadas en el filtro actual
    total_empresas = Empresa.objects.all()
    empresas_verificadas_total = total_empresas.filter(verificada=True).count()
    empresas_sin_verificar_total = total_empresas.filter(verificada=False).count()
    
    # Calcular empresas con servicios asignados
    empresas_con_servicios_total = total_empresas.filter(
        empresaservicio__isnull=False
    ).distinct().count()
    
    return render(request, 'empresas/empresas_crud.html', {
        'empresas': empresas, 
        'form': form,
        'empresas_verificadas': empresas_verificadas_total,
        'empresas_sin_verificar': empresas_sin_verificar_total,
        'empresas_pendientes': empresas_sin_verificar_total,  # Las pendientes son las sin verificar
        'empresas_con_servicios': empresas_con_servicios_total,
        'total_empresas': total_empresas.count()
    })


@admin_required
def editar_empresa(request, empresa_id):
    """Vista para editar una empresa específica"""
    empresa = get_object_or_404(Empresa, id_empresa=empresa_id)
    
    if request.method == "POST":
        # Obtener los datos del formulario
        nombre_empresa = request.POST.get('nombre_empresa')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        contrasena = request.POST.get('contrasena')
        
        # Actualizar los campos de la empresa
        if nombre_empresa:
            empresa.nombre_empresa = nombre_empresa
        if direccion:
            empresa.direccion = direccion
        if telefono:
            empresa.telefono = telefono
        if email:
            empresa.email = email
        if contrasena:
            empresa.contrasena = make_password(contrasena)
        
        empresa.save()
        messages.success(request, f'La empresa "{empresa.nombre_empresa}" ha sido actualizada exitosamente.')
        return redirect('empresascrud')
    
    # Para GET, mostrar el formulario con los datos actuales
    form = EmpresaForm(instance=empresa)
    
    return render(request, 'empresas/editar_empresa.html', {
        'empresa': empresa,
        'form': form
    })




@admin_required
def home_crud(request):
    """Vista del dashboard principal con estadísticas completas del sistema"""
    from django.db.models import Count, Sum, Q
    from datetime import date, timedelta
    
    # Obtener fechas para filtros
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=7)
    inicio_mes = hoy.replace(day=1)
    
    # === ESTADÍSTICAS DE USUARIOS ===
    total_usuarios = Usuario.objects.count()
    # Usuarios registrados este mes
    usuarios_mes = Usuario.objects.filter(fecha_registro__gte=inicio_mes).count()
    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    usuarios_admin = Usuario.objects.filter(rol='admin').count()
    usuarios_cliente = Usuario.objects.filter(rol='cliente').count()
    
    # === ESTADÍSTICAS DE EMPRESAS ===
    total_empresas = Empresa.objects.count()
    empresas_verificadas = Empresa.objects.filter(verificada=True).count()
    empresas_pendientes = Empresa.objects.filter(verificada=False).count()
    
    # === ESTADÍSTICAS DE RESERVAS/CITAS ===
    total_reservas = Reserva.objects.count()
    reservas_hoy = Reserva.objects.filter(fecha=hoy).count()
    reservas_pendientes = Reserva.objects.filter(estado='pendiente').count()
    reservas_completadas = Reserva.objects.filter(estado='completado').count()
    reservas_canceladas = Reserva.objects.filter(estado='cancelada').count()
    reservas_semana = Reserva.objects.filter(fecha__gte=inicio_semana).count()
    reservas_mes = Reserva.objects.filter(fecha__gte=inicio_mes).count()
    
    # Reservas por estado
    reservas_por_estado = Reserva.objects.values('estado').annotate(
        total=Count('id_reserva')
    ).order_by('estado')
    
    # === ESTADÍSTICAS DE SERVICIOS ===
    total_servicios = Servicio.objects.count()
    servicios_mas_reservados = Servicio.objects.annotate(
        total_reservas=Count('reserva__id_reserva')
    ).order_by('-total_reservas')[:5]
    
    # === ESTADÍSTICAS DE PLANES ===
    total_planes = Plan.objects.filter(activo=True).count()
    total_planes_empresariales = PlanEmpresarial.objects.filter(activo=True).count()
    total_suscripciones_activas = SuscripcionUsuario.objects.filter(estado='activa').count()
    total_suscripciones_empresariales = SuscripcionEmpresarial.objects.filter(estado='activa').count()
    
    # === ESTADÍSTICAS DE COMENTARIOS Y QUEJAS ===
    total_comentarios = Comentario.objects.count()
    comentarios_mes = Comentario.objects.filter(fecha__gte=inicio_mes).count()
    total_quejas = MensajeQueja.objects.count()
    quejas_pendientes = MensajeQueja.objects.filter(estado='no respondido').count()
    quejas_respondidas = MensajeQueja.objects.exclude(estado='no respondido').count()
    
    # === ACTIVIDAD RECIENTE ===
    reservas_recientes = Reserva.objects.select_related('usuario', 'empresa').order_by('-id_reserva')[:5]
    comentarios_recientes = Comentario.objects.select_related('usuario').order_by('-fecha')[:5]
    empresas_recientes = Empresa.objects.order_by('-fecha_registro')[:5]
    
    # === MÉTRICAS DE RENDIMIENTO ===
    # Tasa de finalización de reservas
    if total_reservas > 0:
        tasa_completadas = round((reservas_completadas / total_reservas) * 100, 1)
        tasa_canceladas = round((reservas_canceladas / total_reservas) * 100, 1)
        porcentaje_pendientes = round((reservas_pendientes / total_reservas) * 100, 1)
    else:
        tasa_completadas = 0
        tasa_canceladas = 0
        porcentaje_pendientes = 0
    
    # Ingresos estimados (basado en precios de servicios)
    try:
        ingresos_potenciales = Servicio.objects.aggregate(
            total=Sum('precio')
        )['total'] or 0
        ingresos_estimados_mes = reservas_mes * (ingresos_potenciales / max(total_servicios, 1))
    except:
        ingresos_estimados_mes = 0
    
    # === DATOS PARA GRÁFICOS ===
    # Reservas por día en la última semana
    reservas_por_dia = []
    for i in range(7):
        fecha = hoy - timedelta(days=6-i)
        total_dia = Reserva.objects.filter(fecha=fecha).count()
        reservas_por_dia.append({
            'fecha': fecha.strftime('%d/%m'),
            'total': total_dia
        })
    
    # Empresas más activas
    empresas_activas = Empresa.objects.annotate(
        total_reservas=Count('reserva')
    ).filter(total_reservas__gt=0).order_by('-total_reservas')[:5]
    
    context = {
        # Estadísticas principales
        'total_usuarios': total_usuarios,
        'usuarios_mes': usuarios_mes,
        'usuarios_activos': usuarios_activos,
        'usuarios_admin': usuarios_admin,
        'usuarios_cliente': usuarios_cliente,
        
        'total_empresas': total_empresas,
        'empresas_verificadas': empresas_verificadas,
        'empresas_pendientes': empresas_pendientes,
        
        'total_reservas': total_reservas,
        'reservas_hoy': reservas_hoy,
        'reservas_pendientes': reservas_pendientes,
        'reservas_completadas': reservas_completadas,
        'reservas_canceladas': reservas_canceladas,
        'reservas_semana': reservas_semana,
        'reservas_mes': reservas_mes,
        
        'total_servicios': total_servicios,
        'servicios_mas_reservados': servicios_mas_reservados,
        
        'total_planes': total_planes,
        'total_planes_empresariales': total_planes_empresariales,
        'total_suscripciones_activas': total_suscripciones_activas,
        'total_suscripciones_empresariales': total_suscripciones_empresariales,
        
        'total_comentarios': total_comentarios,
        'comentarios_mes': comentarios_mes,
        'total_quejas': total_quejas,
        'quejas_pendientes': quejas_pendientes,
        'quejas_respondidas': quejas_respondidas,
        
        # Métricas de rendimiento
        'tasa_completadas': tasa_completadas,
        'tasa_canceladas': tasa_canceladas,
        'porcentaje_pendientes': porcentaje_pendientes,
        'ingresos_estimados_mes': round(ingresos_estimados_mes, 2),
        
        # Datos para actividad reciente
        'reservas_recientes': reservas_recientes,
        'comentarios_recientes': comentarios_recientes,
        'empresas_recientes': empresas_recientes,
        
        # Datos para gráficos
        'reservas_por_dia': reservas_por_dia,
        'reservas_por_estado': list(reservas_por_estado),
        'empresas_activas': empresas_activas,
        
        # Información adicional
        'fecha_hoy': hoy,
        'usuario_actual': request.user,
    }
    
    return render(request, 'home_crud.html', context)

@empresa_required
def home_empresas(request):
    """Vista del home para empresas"""
    try:
        empresa_id = request.session.get('empresa_id')
        empresa = Empresa.objects.get(id_empresa=empresa_id)
        
        # Obtener estadísticas básicas de la empresa
        reservas_empresa = Reserva.objects.filter(empresa=empresa)
        total_reservas = reservas_empresa.count()
        reservas_completadas = reservas_empresa.filter(estado='completado').count()
        reservas_pendientes = reservas_empresa.filter(estado='pendiente').count()
        
        # Reservas de hoy y próximas
        hoy = timezone.now().date()
        reservas_hoy = reservas_empresa.filter(fecha=hoy).count()
        reservas_proximas = reservas_empresa.filter(
            fecha__gte=hoy,
            fecha__lte=hoy + timedelta(days=7),
            estado='pendiente'
        ).order_by('fecha', 'hora')[:5]
        
        # Actividad reciente (últimas 10 reservas)
        actividad_reciente = []
        reservas_recientes = reservas_empresa.order_by('-fecha', '-hora')[:10]
        
        for reserva in reservas_recientes:
            servicios = reserva.servicios.all()
            precio_total = sum(servicio.precio for servicio in servicios)
            
            actividad_reciente.append({
                'reserva': reserva,
                'servicios': servicios,
                'precio_total': precio_total,
                'tiempo_transcurrido': timezone.now().date() - reserva.fecha if reserva.fecha <= timezone.now().date() else None
            })
        
        # Obtener servicios de la empresa
        servicios_empresa = empresa.servicios.all()
        
        # Ingresos del mes
        primer_dia_mes = hoy.replace(day=1)
        reservas_mes = reservas_empresa.filter(
            fecha__gte=primer_dia_mes,
            fecha__lte=hoy,
            estado='completado'
        )
        
        print(f"🔍 Debug - Fecha actual: {hoy}")
        print(f"🔍 Debug - Primer día del mes: {primer_dia_mes}")
        print(f"🔍 Debug - Reservas del mes completadas: {reservas_mes.count()}")
        
        ingresos_mes = 0
        for reserva in reservas_mes:
            servicios = reserva.servicios.all()
            precio_reserva = sum(servicio.precio for servicio in servicios)
            print(f"🔍 Debug - Reserva {reserva.id_reserva}: servicios={servicios.count()}, precio={precio_reserva}")
            ingresos_mes += precio_reserva
            
        print(f"🔍 Debug - Total ingresos del mes: {ingresos_mes}")
        
        # También calcular ingresos totales como respaldo
        ingresos_totales = 0
        todas_reservas_completadas = reservas_empresa.filter(estado='completado')
        for reserva in todas_reservas_completadas:
            servicios = reserva.servicios.all()
            ingresos_totales += sum(servicio.precio for servicio in servicios)
        
        print(f"🔍 Debug - Ingresos totales (todas las reservas): {ingresos_totales}")
        
        # Convertir a enteros para evitar decimales en el template
        ingresos_mes = int(ingresos_mes) if ingresos_mes else 0
        ingresos_totales = int(ingresos_totales) if ingresos_totales else 0
        
        context = {
            'empresa': empresa,
            'total_reservas': total_reservas,
            'reservas_completadas': reservas_completadas,
            'reservas_pendientes': reservas_pendientes,
            'reservas_hoy': reservas_hoy,
            'reservas_proximas': reservas_proximas,
            'actividad_reciente': actividad_reciente,
            'servicios_empresa': servicios_empresa,
            'ingresos_mes': ingresos_mes,
            'ingresos_totales': ingresos_totales,
        }
        
        return render(request, 'home_empresas.html', context)
        
    except Empresa.DoesNotExist:
        messages.error(request, 'Error: Empresa no encontrada.')
        return redirect('logincrud')
    except Exception as e:
        print(f"❌ Error en home_empresas: {str(e)}")
        messages.error(request, 'Error interno. Intente nuevamente.')
        return redirect('logincrud')

def logout_empresa(request):
    """Vista para cerrar sesión de empresa"""
    empresa_nombre = request.session.get('empresa_nombre', 'Empresa')
    
    # Limpiar todas las variables de sesión relacionadas con la empresa
    request.session.pop('empresa_id', None)
    request.session.pop('empresa_nombre', None)
    request.session.pop('empresa_email', None)
    request.session.pop('es_empresa', None)
    
    messages.success(request, f'Has cerrado sesión correctamente, {empresa_nombre}.')
    return redirect('home')  # Redirigir a la página principal

@empresa_required
def citas_empresa(request):
    """Vista para mostrar todas las citas de la empresa"""
    try:
        empresa_id = request.session.get('empresa_id')
        empresa = Empresa.objects.get(id_empresa=empresa_id)
        
        # Obtener todas las reservas de la empresa
        reservas = Reserva.objects.filter(empresa=empresa).order_by('-fecha', '-hora')
        
        # Obtener reservas con sus servicios
        reservas_con_servicios = []
        for reserva in reservas:
            servicios = reserva.servicios.all()
            reservas_con_servicios.append({
                'reserva': reserva,
                'servicios': servicios,
                'total_servicios': servicios.count(),
                'precio_total': sum(servicio.precio for servicio in servicios)
            })
        
        # Estadísticas
        total_reservas = reservas.count()
        reservas_completadas = reservas.filter(estado='completado').count()
        reservas_pendientes = reservas.filter(estado='pendiente').count()
        reservas_canceladas = reservas.filter(estado='cancelada').count()
        # Reservas por estado
        reservas_hoy = reservas.filter(fecha=timezone.now().date())
        reservas_semana = reservas.filter(
            fecha__gte=timezone.now().date(),
            fecha__lte=timezone.now().date() + timedelta(days=7)
        )
        context = {
            'empresa': empresa,
            'reservas_con_servicios': reservas_con_servicios,
            'total_reservas': total_reservas,
            'reservas_completadas': reservas_completadas,
            'reservas_pendientes': reservas_pendientes,
            'reservas_canceladas': reservas_canceladas,
            'reservas_hoy': reservas_hoy.count(),
            'reservas_semana': reservas_semana.count(),
        }

        return render(request, 'empresas/citas_empresa.html', context)

    except Empresa.DoesNotExist:
        messages.error(request, 'Error: Empresa no encontrada.')
        return redirect('logincrud')
    except Exception as e:
        print(f"❌ Error en citas_empresa: {str(e)}")
        messages.error(request, 'Error interno. Intente nuevamente.')
        return redirect('home_empresas')

@empresa_required
def actualizar_estado_cita(request):
    """Vista para actualizar el estado de una cita"""
    if request.method == 'POST':
        try:
            reserva_id = request.POST.get('reserva_id')
            nuevo_estado = request.POST.get('nuevo_estado')
            
            empresa_id = request.session.get('empresa_id')
            empresa = Empresa.objects.get(id_empresa=empresa_id)
            
            # Verificar que la reserva pertenece a la empresa
            reserva = Reserva.objects.get(id_reserva=reserva_id, empresa=empresa)
            
            if nuevo_estado in ['completado', 'pendiente', 'cancelada']:
                reserva.estado = nuevo_estado
                reserva.save()
                if nuevo_estado == 'completado':
                    estado_texto = 'completada'
                elif nuevo_estado == 'pendiente':
                    estado_texto = 'pendiente'
                else:
                    estado_texto = 'cancelada'
                messages.success(request, f'Cita marcada como {estado_texto} exitosamente.')
            else:
                messages.error(request, 'Estado no válido.')
                
        except Reserva.DoesNotExist:
            messages.error(request, 'Cita no encontrada o no pertenece a tu empresa.')
        except Exception as e:
            print(f"❌ Error al actualizar estado: {str(e)}")
            messages.error(request, 'Error al actualizar el estado de la cita.')
    
    return redirect('citas_empresa')

@empresa_required
def reportes_empresa(request):
    """Vista para mostrar reportes y estadísticas de la empresa"""
    empresa = get_object_or_404(Empresa, email=request.session.get('empresa_email'))
    
    # Obtener período seleccionado (por defecto últimos 12 meses)
    periodo = int(request.GET.get('periodo', 12))
    
    # Estadísticas generales
    total_reservas = Reserva.objects.filter(empresa=empresa).count()
    reservas_completadas = Reserva.objects.filter(empresa=empresa, estado='completado').count()
    reservas_pendientes = Reserva.objects.filter(empresa=empresa, estado='pendiente').count()
    
    # Estadísticas por mes (según período seleccionado)
    # Usar la fecha actual para asegurar que incluimos todos los meses hasta hoy
    from datetime import datetime, date, timedelta
    import calendar
    from django.db.models import Sum, Count, Q
    
    # Usar datetime.now() para obtener la fecha actual exacta
    now = datetime.now()
    hoy = now.date()
    
    reservas_por_mes = []
    ingresos_por_mes = []
    meses = []
    
    # Debug: Mostrar la fecha actual que se está usando
    print(f"🕒 Debug - Fecha/hora actual: {now}")
    print(f"🕒 Debug - Fecha actual utilizada: {hoy} (Mes: {hoy.month}, Año: {hoy.year})")
    print(f"🕒 Debug - Generando los últimos 6 meses incluyendo el actual:")
    print(f"   Esperado: Jul 2025, Jun 2025, May 2025, Abr 2025, Mar 2025, Feb 2025")
    
    # Generar lista de meses desde el más reciente hacia atrás
    meses_a_procesar = []
    
    for i in range(periodo):
        # Usar aritmética simple de meses
        mes_target = hoy.month - i
        ano_target = hoy.year
        
        # Ajustar si el mes es menor a 1
        while mes_target <= 0:
            mes_target += 12
            ano_target -= 1
        
        meses_a_procesar.append({
            'mes': mes_target,
            'ano': ano_target,
            'nombre': f"{calendar.month_name[mes_target][:3]} {ano_target}"
        })
        
        print(f"  📊 Mes {i}: {mes_target}/{ano_target} ({calendar.month_name[mes_target]})")
    
    # Procesar cada mes en orden cronológico inverso (más reciente primero)
    for mes_info in meses_a_procesar:
        mes_actual = mes_info['mes']
        ano_actual = mes_info['ano']
        
        # Obtener reservas del mes
        reservas_mes = Reserva.objects.filter(
            empresa=empresa,
            fecha__month=mes_actual,
            fecha__year=ano_actual
        ).count()
        
        # Calcular ingresos del mes
        ingresos_mes = 0
        reservas_completadas_mes = Reserva.objects.filter(
            empresa=empresa,
            fecha__month=mes_actual,
            fecha__year=ano_actual,
            estado='completado'
        )
        
        for reserva in reservas_completadas_mes:
            try:
                precio_total = sum([rs.servicio.precio for rs in ReservaServicio.objects.filter(reserva=reserva)])
                ingresos_mes += precio_total
            except:
                continue
        
        # Agregar al principio para mantener orden cronológico inverso para las gráficas
        reservas_por_mes.insert(0, reservas_mes)
        ingresos_por_mes.insert(0, round(ingresos_mes, 2))
        meses.insert(0, mes_info['nombre'])
        
        print(f"    → Reservas: {reservas_mes}, Ingresos: {round(ingresos_mes, 2)}")
    
    print(f"📊 Debug - Meses finales: {meses}")
    print(f"📊 Debug - Reservas finales: {reservas_por_mes}")
    print(f"📊 Debug - Ingresos finales: {ingresos_por_mes}")
    
    # Servicios más solicitados
    servicios_populares = []
    for servicio in Servicio.objects.all():
        count = ReservaServicio.objects.filter(
            reserva__empresa=empresa,
            servicio=servicio
        ).count()
        if count > 0:
            porcentaje = (count / total_reservas * 100) if total_reservas > 0 else 0
            servicios_populares.append({
                'servicio': servicio,
                'count': count,
                'ingresos': round(count * servicio.precio, 2),
                'porcentaje': round(porcentaje, 1)
            })
    
    servicios_populares = sorted(servicios_populares, key=lambda x: x['count'], reverse=True)[:5]
    
    # Estadísticas por día de la semana
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    reservas_por_dia = []
    
    for i in range(7):
        # Django week_day: 1=Sunday, 2=Monday, etc.
        dia_django = (i + 1) % 7 + 1  # Convertir para que Monday=2
        if dia_django == 1:  # Sunday
            dia_django = 8
        
        count = Reserva.objects.filter(
            empresa=empresa,
            fecha__week_day=dia_django
        ).count()
        reservas_por_dia.append(count)
    
    # Ingresos totales
    ingresos_totales = sum(ingresos_por_mes)
    
    # Promedio de reservas por día
    from datetime import timedelta
    dias_transcurridos = max((hoy - empresa.fecha_registro.date()).days, 1)
    promedio_reservas_dia = total_reservas / dias_transcurridos
    
    # Tasa de completado
    tasa_completado = (reservas_completadas / total_reservas * 100) if total_reservas > 0 else 0
    
    # Reservas del mes actual
    reservas_mes_actual = Reserva.objects.filter(
        empresa=empresa,
        fecha__month=hoy.month,
        fecha__year=hoy.year
    ).count()
    
    # Ingresos del mes actual
    ingresos_mes_actual = 0
    for reserva in Reserva.objects.filter(empresa=empresa, fecha__month=hoy.month, fecha__year=hoy.year, estado='completado'):
        try:
            precio_total = sum([rs.servicio.precio for rs in ReservaServicio.objects.filter(reserva=reserva)])
            ingresos_mes_actual += precio_total
        except:
            continue
    
    # Calcular crecimiento mes anterior
    mes_anterior = hoy.month - 1
    ano_anterior = hoy.year
    if mes_anterior <= 0:
        mes_anterior = 12
        ano_anterior -= 1
    
    reservas_mes_anterior = Reserva.objects.filter(
        empresa=empresa,
        fecha__month=mes_anterior,
        fecha__year=ano_anterior
    ).count()
    
    crecimiento_reservas = 0
    if reservas_mes_anterior > 0:
        crecimiento_reservas = ((reservas_mes_actual - reservas_mes_anterior) / reservas_mes_anterior) * 100
    
    # Crear datos estructurados para la tabla (mostrar los últimos 6 meses más recientes incluyendo el actual)
    datos_tabla = []
    
    # Generar los últimos 6 meses incluyendo el mes actual (Julio 2025)
    meses_tabla = []
    for i in range(6):  # 6 meses: Julio, Junio, Mayo, Abril, Marzo, Febrero
        mes_target = hoy.month - i
        ano_target = hoy.year
        
        # Ajustar si el mes es menor a 1
        while mes_target <= 0:
            mes_target += 12
            ano_target -= 1
        
        mes_nombre = f"{calendar.month_name[mes_target][:3]} {ano_target}"
        meses_tabla.append({
            'mes': mes_target,
            'ano': ano_target,
            'nombre': mes_nombre
        })
        
        print(f"  📊 Tabla - Mes {i}: {mes_target}/{ano_target} ({mes_nombre})")
    
    # Procesar cada mes para la tabla
    for i, mes_info in enumerate(meses_tabla):
        mes_actual = mes_info['mes']
        ano_actual = mes_info['ano']
        # Obtener reservas del mes
        reservas_mes = Reserva.objects.filter(
            empresa=empresa,
            fecha__month=mes_actual,
            fecha__year=ano_actual
        ).count()
        # Calcular reservas completadas del mes
        completadas_mes = Reserva.objects.filter(
            empresa=empresa,
            fecha__month=mes_actual,
            fecha__year=ano_actual,
            estado='completado'
        ).count()
        # Calcular reservas pendientes del mes
        pendientes_mes = Reserva.objects.filter(
            empresa=empresa,
            fecha__month=mes_actual,
            fecha__year=ano_actual,
            estado='pendiente'
        ).count()
        # Calcular reservas canceladas del mes
        canceladas_mes = Reserva.objects.filter(
            empresa=empresa,
            fecha__month=mes_actual,
            fecha__year=ano_actual,
            estado='cancelada'
        ).count()
        # Calcular ingresos del mes
        ingresos_mes = 0
        reservas_completadas_mes = Reserva.objects.filter(
            empresa=empresa,
            fecha__month=mes_actual,
            fecha__year=ano_actual,
            estado='completado'
        )
        for reserva in reservas_completadas_mes:
            try:
                precio_total = sum([rs.servicio.precio for rs in ReservaServicio.objects.filter(reserva=reserva)])
                ingresos_mes += precio_total
            except:
                continue
        # Calcular porcentaje de progreso basado en el máximo de reservas de todos los meses
        max_reservas_tabla = 1  # Valor por defecto
        for mes_temp in meses_tabla:
            reservas_temp = Reserva.objects.filter(
                empresa=empresa,
                fecha__month=mes_temp['mes'],
                fecha__year=mes_temp['ano']
            ).count()
            if reservas_temp > max_reservas_tabla:
                max_reservas_tabla = reservas_temp
        porcentaje_progreso = (reservas_mes / max_reservas_tabla * 100) if max_reservas_tabla > 0 else 0
        # Calcular crecimiento comparando con el mes anterior
        crecimiento_mes = 0
        if i < len(meses_tabla) - 1:  # Si no es el último mes (más antiguo)
            mes_anterior_info = meses_tabla[i + 1]
            reservas_mes_anterior = Reserva.objects.filter(
                empresa=empresa,
                fecha__month=mes_anterior_info['mes'],
                fecha__year=mes_anterior_info['ano']
            ).count()
            if reservas_mes_anterior > 0:
                crecimiento_mes = ((reservas_mes - reservas_mes_anterior) / reservas_mes_anterior) * 100
        datos_tabla.append({
            'mes': mes_info['nombre'],
            'reservas': reservas_mes,
            'completadas': completadas_mes,
            'pendientes': pendientes_mes,
            'canceladas': canceladas_mes,
            'porcentaje_progreso': round(porcentaje_progreso, 1),
            'ingresos': round(ingresos_mes, 2),
            'crecimiento': round(crecimiento_mes, 1) if crecimiento_mes != 0 else 0
        })
        print(f"    → Tabla {mes_info['nombre']}: Reservas: {reservas_mes}, Completadas: {completadas_mes}, Pendientes: {pendientes_mes}, Canceladas: {canceladas_mes}, Ingresos: {round(ingresos_mes, 2)}")
    
    print(f"🔍 Debug - Datos tabla final generados: {len(datos_tabla)} filas")
    for i, dato in enumerate(datos_tabla):
        print(f"  Fila {i}: {dato}")
    
    # Convertir datos a JSON para JavaScript
    import json
    
    context = {
        'empresa': empresa,
        'periodo': periodo,
        'total_reservas': total_reservas,
        'reservas_completadas': reservas_completadas,
        'reservas_pendientes': reservas_pendientes,
        'reservas_por_mes': json.dumps(reservas_por_mes),
        'ingresos_por_mes': json.dumps(ingresos_por_mes),
        'meses': json.dumps(meses),
        'servicios_populares': servicios_populares,
        'reservas_por_dia': json.dumps(reservas_por_dia),
        'dias_semana': json.dumps(dias_semana),
        'ingresos_totales': round(ingresos_totales, 2),
        'promedio_reservas_dia': round(promedio_reservas_dia, 1),
        'tasa_completado': round(tasa_completado, 1),
        'reservas_mes_actual': reservas_mes_actual,
        'ingresos_mes_actual': round(ingresos_mes_actual, 2),
        'crecimiento_reservas': round(crecimiento_reservas, 1),
        'datos_tabla': datos_tabla,
    }
    
    return render(request, 'empresas/reportes_empresa.html', context)


# =============================================================================
# VISTAS PARA MANEJO DE PLANES Y SUSCRIPCIONES
# =============================================================================

def planes_view(request):
    """Vista para mostrar todos los planes disponibles"""
    planes = Plan.objects.filter(activo=True).order_by('precio_mensual')
    
    # Si el usuario está logueado, obtener su suscripción actual
    suscripcion_actual = None
    if request.user.is_authenticated:
        suscripcion_actual = SuscripcionUsuario.objects.filter(
            usuario=request.user,
            estado='activa'
        ).first()
    
    context = {
        'planes': planes,
        'suscripcion_actual': suscripcion_actual,
    }
    return render(request, 'planes/planes.html', context)

@login_required
def suscribirse_plan(request, plan_id):
    """Vista para suscribirse a un plan"""
    plan = get_object_or_404(Plan, id_plan=plan_id, activo=True)
    
    # Verificar si el usuario ya tiene una suscripción activa
    suscripcion_existente = SuscripcionUsuario.objects.filter(
        usuario=request.user,
        estado='activa'
    ).first()
    
    if suscripcion_existente:
        messages.warning(request, 'Ya tienes una suscripción activa. Cancela la actual para cambiar de plan.')
        return redirect('mi_suscripcion')
    
    if request.method == 'POST':
        # Crear nueva suscripción
        suscripcion = SuscripcionUsuario.objects.create(
            usuario=request.user,
            plan=plan,
            fecha_inicio=timezone.now(),
            fecha_fin=timezone.now() + timezone.timedelta(days=30)
        )
        
        # Crear registro de pago
        referencia = str(uuid.uuid4())
        HistorialPagosSuscripcion.objects.create(
            suscripcion=suscripcion,
            monto=plan.precio_mensual,
            referencia_pago=referencia,
            metodo_pago='PayU',  # O el método que uses
            estado='pendiente'
        )
        
        # Aquí integrarías con PayU o tu pasarela de pago
        # Por ahora, redirigimos a una página de confirmación
        messages.success(request, f'Te has suscrito al plan {plan.nombre}. Procesando pago...')
        return redirect('procesar_pago_suscripcion', referencia=referencia)
    
    context = {
        'plan': plan,
    }
    return render(request, 'planes/suscribirse.html', context)

@login_required
def mi_suscripcion(request):
    """Vista del dashboard de suscripción del usuario"""
    suscripcion = SuscripcionUsuario.objects.filter(
        usuario=request.user,
        estado='activa'
    ).first()
    
    historial_pagos = []
    if suscripcion:
        historial_pagos = HistorialPagosSuscripcion.objects.filter(
            suscripcion=suscripcion
        ).order_by('-fecha_pago')[:5]
    
    # Obtener reservas recientes relacionadas con la suscripción
    reservas_recientes = Reserva.objects.filter(
        usuario=request.user,
        suscripcion_utilizada=suscripcion
    ).order_by('-fecha')[:5] if suscripcion else []
    
    context = {
        'suscripcion': suscripcion,
        'historial_pagos': historial_pagos,
        'reservas_recientes': reservas_recientes,
        'servicios_restantes': suscripcion.servicios_restantes() if suscripcion else 0,
    }
    return render(request, 'planes/mi_suscripcion.html', context)

@login_required
def cancelar_suscripcion(request):
    """Vista para cancelar suscripción"""
    suscripcion = get_object_or_404(
        SuscripcionUsuario,
        usuario=request.user,
        estado='activa'
    )
    
    if request.method == 'POST':
        suscripcion.estado = 'cancelada'
        suscripcion.auto_renovar = False
        suscripcion.save()
        
        messages.success(request, 'Tu suscripción ha sido cancelada exitosamente.')
        return redirect('planes')
    
    context = {
        'suscripcion': suscripcion,
    }
    return render(request, 'planes/cancelar_suscripcion.html', context)

@login_required
def procesar_pago_suscripcion(request, referencia):
    """Vista para procesar el pago de la suscripción"""
    pago = get_object_or_404(HistorialPagosSuscripcion, referencia_pago=referencia)
    
    # Aquí integrarías con PayU
    # Por ahora simulamos un pago exitoso
    if request.method == 'POST':
        pago.estado = 'aprobado'
        pago.save()
        
        # Activar la suscripción
        pago.suscripcion.estado = 'activa'
        pago.suscripcion.save()
        
        messages.success(request, '¡Pago procesado exitosamente! Tu suscripción está activa.')
        return redirect('mi_suscripcion')
    
    context = {
        'pago': pago,
        'plan': pago.suscripcion.plan,
    }
    return render(request, 'planes/procesar_pago.html', context)

# Función auxiliar para verificar si el usuario puede hacer una reserva
def verificar_disponibilidad_suscripcion(usuario):
    """Verifica si el usuario puede hacer una reserva con su suscripción"""
    suscripcion = SuscripcionUsuario.objects.filter(
        usuario=usuario,
        estado='activa'
    ).first()
    
    if not suscripcion:
        return False, "No tienes una suscripción activa"
    
    if not suscripcion.esta_activa():
        return False, "Tu suscripción ha vencido"
    
    if not suscripcion.puede_usar_servicio():
        return False, f"Has agotado tus servicios del mes. Restantes: {suscripcion.servicios_restantes()}"
    
    return True, suscripcion

@admin_required
def planes_crud(request):
    """Vista CRUD para gestionar planes (solo admin)"""
    planes = Plan.objects.all().order_by('precio_mensual')
    
    # Calcular estadísticas
    planes_activos = planes.filter(activo=True).count()
    precio_promedio = planes.aggregate(promedio=Avg('precio_mensual'))['promedio'] or 0
    
    context = {
        'planes': planes,
        'planes_activos': planes_activos,
        'precio_promedio': precio_promedio,
    }
    return render(request, 'planes/planes_crud.html', context)

@admin_required
def crear_plan(request):
    """Vista para crear un nuevo plan"""
    if request.method == 'POST':
        plan = Plan.objects.create(
            nombre=request.POST.get('nombre'),
            tipo=request.POST.get('tipo'),
            descripcion=request.POST.get('descripcion'),
            precio_mensual=request.POST.get('precio_mensual'),
            cantidad_servicios_mes=request.POST.get('cantidad_servicios_mes', 0),
            incluye_lavado_asientos=request.POST.get('incluye_lavado_asientos') == 'on',
            incluye_aspirado=request.POST.get('incluye_aspirado') == 'on',
            incluye_lavado_exterior=request.POST.get('incluye_lavado_exterior') == 'on',
            incluye_lavado_interior_humedo=request.POST.get('incluye_lavado_interior_humedo') == 'on',
            incluye_encerado=request.POST.get('incluye_encerado') == 'on',
            incluye_detallado_completo=request.POST.get('incluye_detallado_completo') == 'on',
        )
        
        # Agregar servicios incluidos
        servicios_ids = request.POST.getlist('servicios_incluidos')
        for servicio_id in servicios_ids:
            servicio = Servicio.objects.get(id_servicio=servicio_id)
            plan.servicios_incluidos.add(servicio)
        
        messages.success(request, f'Plan "{plan.nombre}" creado exitosamente.')
        return redirect('planes_crud')
    
    servicios = Servicio.objects.all()
    context = {
        'servicios': servicios,
    }
    return render(request, 'planes/crear_plan.html', context)

@admin_required
def editar_plan(request, plan_id):
    """Vista para editar un plan existente"""
    plan = get_object_or_404(Plan, id_plan=plan_id)
    
    if request.method == 'POST':
        plan.nombre = request.POST.get('nombre')
        plan.tipo = request.POST.get('tipo')
        plan.descripcion = request.POST.get('descripcion')
        plan.precio_mensual = request.POST.get('precio_mensual')
        plan.cantidad_servicios_mes = request.POST.get('cantidad_servicios_mes', 0)
        plan.incluye_lavado_asientos = request.POST.get('incluye_lavado_asientos') == 'on'
        plan.incluye_aspirado = request.POST.get('incluye_aspirado') == 'on'
        plan.incluye_lavado_exterior = request.POST.get('incluye_lavado_exterior') == 'on'
        plan.incluye_lavado_interior_humedo = request.POST.get('incluye_lavado_interior_humedo') == 'on'
        plan.incluye_encerado = request.POST.get('incluye_encerado') == 'on'
        plan.incluye_detallado_completo = request.POST.get('incluye_detallado_completo') == 'on'
        plan.save()
        
        # Actualizar servicios incluidos
        plan.servicios_incluidos.clear()
        servicios_ids = request.POST.getlist('servicios_incluidos')
        for servicio_id in servicios_ids:
            servicio = Servicio.objects.get(id_servicio=servicio_id)
            plan.servicios_incluidos.add(servicio)
        
        messages.success(request, f'Plan "{plan.nombre}" actualizado exitosamente.')
        return redirect('planes_crud')
    
    servicios = Servicio.objects.all()
    context = {
        'plan': plan,
        'servicios': servicios,
    }
    return render(request, 'palnes/editar_plan.html', context)

@admin_required
def eliminar_plan(request, plan_id):
    """Vista para eliminar un plan"""
    plan = get_object_or_404(Plan, id_plan=plan_id)
    
    if request.method == 'POST':
        plan.activo = False
        plan.save()
        messages.success(request, f'Plan "{plan.nombre}" desactivado exitosamente.')
        return redirect('planes_crud')
    
    context = {
        'plan': plan,
    }
    return render(request, 'eliminar_plan.html', context)

@admin_required
def suscripciones_crud(request):
    """Vista para gestionar suscripciones (solo admin)"""
    suscripciones = SuscripcionUsuario.objects.all().order_by('-fecha_inicio')
    context = {
        'suscripciones': suscripciones,
    }
    return render(request, 'planes/suscripciones_crud.html', context)


@empresa_required
def perfil_empresa(request):
    """Vista para gestionar el perfil de la empresa"""
    try:
        empresa_id = request.session.get('empresa_id')
        empresa = Empresa.objects.get(id_empresa=empresa_id)
        
        if request.method == 'POST':
            form = EmpresaPerfilForm(request.POST, instance=empresa)
            if form.is_valid():
                # Guardar los datos básicos de la empresa
                empresa_actualizada = form.save()
                
                # Manejar cambio de contraseña si se proporcionó
                contrasena_actual = form.cleaned_data.get('contrasena_actual')
                nueva_contrasena = form.cleaned_data.get('nueva_contrasena')
                
                if nueva_contrasena and contrasena_actual:
                    # Verificar contraseña actual
                    if check_password(contrasena_actual, empresa.contrasena):
                        # Actualizar con la nueva contraseña
                        empresa_actualizada.contrasena = make_password(nueva_contrasena)
                        empresa_actualizada.save()
                        messages.success(request, 'Perfil y contraseña actualizados exitosamente.')
                    else:
                        messages.error(request, 'La contraseña actual es incorrecta.')
                        return render(request, 'perfil_empresa.html', {'form': form, 'empresa': empresa})
                else:
                    messages.success(request, 'Perfil actualizado exitosamente.')
                
                # Actualizar datos en la sesión
                request.session['empresa_nombre'] = empresa_actualizada.nombre_empresa
                request.session['empresa_email'] = empresa_actualizada.email
                
                return redirect('perfil_empresa')
            else:
                messages.error(request, 'Por favor, corrija los errores en el formulario.')
        else:
            form = EmpresaPerfilForm(instance=empresa)
        
        # Obtener estadísticas adicionales para mostrar en el perfil
        total_reservas = Reserva.objects.filter(empresa=empresa).count()
        reservas_completadas = Reserva.objects.filter(empresa=empresa, estado='completado').count()
        servicios_ofrecidos = empresa.servicios.count()
        
        # Fecha de registro formateada
        fecha_registro = empresa.fecha_registro.strftime('%d de %B de %Y') if empresa.fecha_registro else 'No disponible'
        
        # ===== NUEVOS DATOS PARA GESTIÓN DE SERVICIOS =====
        # Servicios ya asignados a la empresa
        servicios_asignados = empresa.servicios.all()
        
        # Servicios disponibles que la empresa aún no tiene
        servicios_disponibles = Servicio.objects.exclude(id_servicio__in=servicios_asignados.values_list('id_servicio', flat=True))
        
        # Solicitudes pendientes de la empresa
        solicitudes_pendientes = SolicitudServicioEmpresa.objects.filter(
            empresa=empresa,
            estado__in=['pendiente', 'en_revision']
        ).order_by('-fecha_solicitud')
        
        context = {
            'form': form,
            'empresa': empresa,
            'total_reservas': total_reservas,
            'reservas_completadas': reservas_completadas,
            'servicios_ofrecidos': servicios_ofrecidos,
            'fecha_registro': fecha_registro,
            # Nuevos contextos para servicios
            'servicios_asignados': servicios_asignados,
            'servicios_disponibles': servicios_disponibles,
            'solicitudes_pendientes': solicitudes_pendientes,
        }

        return render(request, 'empresas/perfil_empresa.html', context)

    except Empresa.DoesNotExist:
        messages.error(request, 'Error: Empresa no encontrada.')
        return redirect('logincrud')
    except Exception as e:
        print(f"❌ Error en perfil_empresa: {str(e)}")
        messages.error(request, 'Error interno. Intente nuevamente.')
        return redirect('home_empresas')


@empresa_required
def solicitar_servicio_empresa(request):
    """Vista para procesar solicitudes de servicios por parte de empresas"""
    print(f"🔍 solicitar_servicio_empresa llamada con método: {request.method}")
    print(f"📋 POST data: {dict(request.POST)}")
    print(f"👤 Empresa en sesión: {request.session.get('empresa_id')}")
    
    if request.method == 'POST':
        try:
            empresa_id = request.session.get('empresa_id')
            print(f"🏢 Empresa ID: {empresa_id}")
            empresa = Empresa.objects.get(id_empresa=empresa_id)
            print(f"✅ Empresa encontrada: {empresa.nombre_empresa}")
            
            servicio_id = request.POST.get('servicio_id')
            usuario_responsable = request.POST.get('usuario_responsable')
            telefono_contacto = request.POST.get('telefono_contacto')
            motivo_solicitud = request.POST.get('motivo_solicitud')
            
            print(f"📝 Datos recibidos:")
            print(f"   - Servicio ID: {servicio_id}")
            print(f"   - Usuario responsable: {usuario_responsable}")
            print(f"   - Teléfono: {telefono_contacto}")
            print(f"   - Motivo: {motivo_solicitud}")
            
            # Validaciones básicas
            if not all([servicio_id, usuario_responsable, telefono_contacto, motivo_solicitud]):
                print("❌ Faltan campos requeridos")
                messages.error(request, 'Todos los campos son requeridos.')
                return redirect('perfil_empresa')
            
            try:
                servicio = Servicio.objects.get(id_servicio=servicio_id)
                print(f"🛠️ Servicio encontrado: {servicio.nombre_servicio}")
            except Servicio.DoesNotExist:
                print("❌ Servicio no existe")
                messages.error(request, 'El servicio solicitado no existe.')
                return redirect('perfil_empresa')
            
            # Verificar si la empresa ya tiene este servicio
            if empresa.servicios.filter(id_servicio=servicio_id).exists():
                print("⚠️ Empresa ya tiene este servicio")
                messages.error(request, f'Tu empresa ya tiene acceso al servicio "{servicio.nombre_servicio}".')
                return redirect('perfil_empresa')
            
            # Verificar si ya existe una solicitud pendiente para este servicio
            solicitud_existente = SolicitudServicioEmpresa.objects.filter(
                empresa=empresa,
                servicio_solicitado=servicio,
                estado__in=['pendiente', 'en_revision']
            ).first()
            
            if solicitud_existente:
                print("⚠️ Ya existe solicitud pendiente")
                messages.warning(request, f'Ya tienes una solicitud pendiente para el servicio "{servicio.nombre_servicio}".')
                return redirect('perfil_empresa')
            
            # Crear la nueva solicitud
            nueva_solicitud = SolicitudServicioEmpresa.objects.create(
                empresa=empresa,
                servicio_solicitado=servicio,
                motivo_solicitud=motivo_solicitud,
                usuario_responsable=usuario_responsable,
                telefono_contacto=telefono_contacto,
                estado='pendiente'
            )
            
            print(f"✅ Nueva solicitud creada con ID: {nueva_solicitud.id_solicitud}")
            messages.success(request, f'Solicitud enviada exitosamente para el servicio "{servicio.nombre_servicio}". Te contactaremos pronto.')
            
            # Log para debugging
            print(f"✅ Nueva solicitud de servicio creada:")
            print(f"   - Empresa: {empresa.nombre_empresa}")
            print(f"   - Servicio: {servicio.nombre_servicio}")
            print(f"   - Responsable: {usuario_responsable}")
            print(f"   - ID Solicitud: {nueva_solicitud.id_solicitud}")
            
            return redirect('perfil_empresa')
            
        except Empresa.DoesNotExist:
            messages.error(request, 'Error: Empresa no encontrada.')
            return redirect('logincrud')
        except Exception as e:
            print(f"❌ Error en solicitar_servicio_empresa: {str(e)}")
            messages.error(request, 'Error interno al procesar la solicitud. Intente nuevamente.')
            return redirect('perfil_empresa')
    
    # Si no es POST, redirigir al perfil
    return redirect('perfil_empresa')


@empresa_required
def exportar_reporte_empresa(request):
    """Vista para exportar reportes de la empresa en formato CSV"""
    try:
        import csv
        from django.http import HttpResponse
        from datetime import datetime, timedelta
        import calendar
        
        empresa_id = request.session.get('empresa_id')
        empresa = Empresa.objects.get(id_empresa=empresa_id)
        
        # Obtener el período seleccionado (por defecto 6 meses)
        periodo = int(request.GET.get('periodo', 6))
        formato = request.GET.get('formato', 'csv')  # csv o pdf
        
        # Calcular fechas
        hoy = timezone.now().date()
        fecha_inicio = hoy - timedelta(days=30 * periodo)
        
        print(f"🔍 Exportando reporte para empresa {empresa.nombre_empresa}")
        print(f"📅 Período: {periodo} meses (desde {fecha_inicio} hasta {hoy})")
        
        # Obtener datos de reservas
        reservas_empresa = Reserva.objects.filter(
            empresa=empresa,
            fecha__gte=fecha_inicio,
            fecha__lte=hoy
        ).order_by('-fecha')
        
        # Estadísticas generales
        total_reservas = reservas_empresa.count()
        reservas_completadas = reservas_empresa.filter(estado='completado').count()
        reservas_pendientes = reservas_empresa.filter(estado='pendiente').count()
        tasa_completado = (reservas_completadas / total_reservas * 100) if total_reservas > 0 else 0
        
        # Calcular ingresos
        ingresos_totales = 0
        for reserva in reservas_empresa.filter(estado='completado'):
            try:
                servicios = reserva.servicios.all()
                precio_reserva = sum(servicio.precio for servicio in servicios)
                ingresos_totales += precio_reserva
            except Exception as e:
                print(f"❌ Error calculando ingresos para reserva {reserva.id_reserva}: {e}")
                continue
        
        # Datos por mes
        datos_mensuales = []
        for i in range(periodo):
            fecha_mes = hoy - timedelta(days=30 * i)
            mes_actual = fecha_mes.month
            ano_actual = fecha_mes.year
            
            reservas_mes = reservas_empresa.filter(
                fecha__month=mes_actual,
                fecha__year=ano_actual
            )
            
            completadas_mes = reservas_mes.filter(estado='completado').count()
            ingresos_mes = 0
            
            for reserva in reservas_mes.filter(estado='completado'):
                try:
                    servicios = reserva.servicios.all()
                    ingresos_mes += sum(servicio.precio for servicio in servicios)
                except:
                    continue
            
            datos_mensuales.append({
                'mes': f"{calendar.month_name[mes_actual]} {ano_actual}",
                'total_reservas': reservas_mes.count(),
                'completadas': completadas_mes,
                'pendientes': reservas_mes.filter(estado='pendiente').count(),
                'ingresos': ingresos_mes,
                'tasa_completado': (completadas_mes / reservas_mes.count() * 100) if reservas_mes.count() > 0 else 0
            })
        
        # Servicios más populares
        servicios_populares = []
        servicios_stats = {}
        
        for reserva in reservas_empresa:
            for servicio in reserva.servicios.all():
                if servicio.nombre_servicio not in servicios_stats:
                    servicios_stats[servicio.nombre_servicio] = {
                        'count': 0,
                        'ingresos': 0,
                        'precio': servicio.precio
                    }
                servicios_stats[servicio.nombre_servicio]['count'] += 1
                if reserva.estado == 'completado':
                    servicios_stats[servicio.nombre_servicio]['ingresos'] += servicio.precio
        
        # Ordenar servicios por popularidad
        servicios_populares = sorted(
            [{'servicio': k, **v} for k, v in servicios_stats.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:5]  # Top 5
        
        if formato == 'csv':
            # Crear respuesta CSV
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="reporte_empresa_{empresa.nombre_empresa}_{periodo}meses_{hoy.strftime("%Y%m%d")}.csv"'
            
            # Agregar BOM para UTF-8
            response.write('\ufeff')
            
            writer = csv.writer(response)
            
            # Encabezado del reporte
            writer.writerow(['REPORTE DE ANÁLISIS DE NEGOCIO - AUTONEW'])
            writer.writerow([''])
            writer.writerow(['Información de la Empresa'])
            writer.writerow(['Empresa:', empresa.nombre_empresa])
            writer.writerow(['Email:', empresa.email])
            writer.writerow(['Teléfono:', empresa.telefono])
            writer.writerow(['Dirección:', empresa.direccion])
            writer.writerow(['Fecha de Reporte:', hoy.strftime('%d/%m/%Y')])
            writer.writerow(['Período Analizado:', f'Últimos {periodo} meses'])
            writer.writerow(['Fecha Inicio:', fecha_inicio.strftime('%d/%m/%Y')])
            writer.writerow(['Fecha Fin:', hoy.strftime('%d/%m/%Y')])
            writer.writerow([''])
            
            # Métricas principales
            writer.writerow(['MÉTRICAS PRINCIPALES'])
            writer.writerow(['Métrica', 'Valor'])
            writer.writerow(['Total de Reservas', total_reservas])
            writer.writerow(['Reservas Completadas', reservas_completadas])
            writer.writerow(['Reservas Pendientes', reservas_pendientes])
            writer.writerow(['Tasa de Completado (%)', f"{tasa_completado:.1f}%"])
            writer.writerow(['Ingresos Totales', f"${ingresos_totales:,.2f}"])
            writer.writerow(['Promedio por Reserva', f"${(ingresos_totales/total_reservas):,.2f}" if total_reservas > 0 else "$0.00"])
            writer.writerow([''])
            
            # Análisis mensual
            writer.writerow(['ANÁLISIS MENSUAL DETALLADO'])
            writer.writerow(['Mes/Año', 'Total Reservas', 'Completadas', 'Pendientes', 'Tasa Completado (%)', 'Ingresos'])
            
            for dato in reversed(datos_mensuales):  # Mostrar del más antiguo al más reciente
                writer.writerow([
                    dato['mes'],
                    dato['total_reservas'],
                    dato['completadas'],
                    dato['pendientes'],
                    f"{dato['tasa_completado']:.1f}%",
                    f"${dato['ingresos']:,.2f}"
                ])
            
            writer.writerow([''])
            
            # Servicios más populares
            writer.writerow(['SERVICIOS MÁS POPULARES'])
            writer.writerow(['Servicio', 'Total Reservas', 'Ingresos Generados', 'Precio Unitario'])
            
            for servicio in servicios_populares:
                writer.writerow([
                    servicio['servicio'],
                    servicio['count'],
                    f"${servicio['ingresos']:,.2f}",
                    f"${servicio['precio']:,.2f}"
                ])
            
            writer.writerow([''])
            
            # Detalle de reservas
            writer.writerow(['DETALLE DE RESERVAS'])
            writer.writerow(['Fecha', 'Cliente', 'Servicios', 'Estado', 'Total'])
            
            for reserva in reservas_empresa.order_by('-fecha')[:50]:  # Últimas 50 reservas
                servicios_nombres = ', '.join([s.nombre_servicio for s in reserva.servicios.all()])
                total_reserva = sum(s.precio for s in reserva.servicios.all()) if reserva.estado == 'completado' else 0
                
                writer.writerow([
                    reserva.fecha.strftime('%d/%m/%Y'),
                    reserva.usuario.nombre_completo if reserva.usuario else 'N/A',
                    servicios_nombres or 'Sin servicios',
                    'Completada' if reserva.estado == 'completado' else 'Pendiente',
                    f"${total_reserva:,.2f}"
                ])
            
            writer.writerow([''])
            writer.writerow(['Reporte generado por AUTONEW - Sistema de Gestión de Lavado de Autos'])
            writer.writerow([f'Generado el {datetime.now().strftime("%d/%m/%Y a las %H:%M")}'])
            
            print(f"✅ Reporte CSV generado exitosamente para {empresa.nombre_empresa}")
            return response
            
        else:
            # Formato no soportado por ahora
            messages.error(request, 'Formato de reporte no soportado.')
            return redirect('reportes_empresa')
            
    except Empresa.DoesNotExist:
        messages.error(request, 'Error: Empresa no encontrada.')
        return redirect('logincrud')
    except Exception as e:
        print(f"❌ Error generando reporte: {str(e)}")
        messages.error(request, 'Error generando el reporte. Intente nuevamente.')
        return redirect('reportes_empresa')


# ================================
# VISTAS CRUD PARA PLANES EMPRESARIALES
# ================================

@admin_required
def planes_empresariales_crud(request):
    """Vista CRUD para gestionar planes empresariales (solo admin)"""
    planes = PlanEmpresarial.objects.all().order_by('precio_mensual_por_vehiculo')
    context = {
        'planes': planes,
    }
    return render(request, 'planes/planes_empresariales_crud.html', context)

@admin_required
def crear_plan_empresarial(request):
    """Vista para crear un nuevo plan empresarial"""
    if request.method == 'POST':
        try:
            plan = PlanEmpresarial.objects.create(
                nombre=request.POST.get('nombre'),
                tipo=request.POST.get('tipo'),
                descripcion=request.POST.get('descripcion'),
                precio_mensual_por_vehiculo=request.POST.get('precio_mensual_por_vehiculo'),
                precio_base_mensual=request.POST.get('precio_base_mensual', 0),
                vehiculos_minimos=request.POST.get('vehiculos_minimos', 5),
                vehiculos_maximos=request.POST.get('vehiculos_maximos') or None,
                servicios_por_vehiculo_mes=request.POST.get('servicios_por_vehiculo_mes', 0),
                descuento_volumen=request.POST.get('descuento_volumen', 0),
                incluye_lavado_asientos=request.POST.get('incluye_lavado_asientos') == 'on',
                incluye_aspirado=request.POST.get('incluye_aspirado') == 'on',
                incluye_lavado_exterior=request.POST.get('incluye_lavado_exterior') == 'on',
                incluye_lavado_interior_humedo=request.POST.get('incluye_lavado_interior_humedo') == 'on',
                incluye_encerado=request.POST.get('incluye_encerado') == 'on',
                incluye_detallado_completo=request.POST.get('incluye_detallado_completo') == 'on',
                incluye_servicio_domicilio=request.POST.get('incluye_servicio_domicilio') == 'on',
                incluye_mantenimiento_programado=request.POST.get('incluye_mantenimiento_programado') == 'on',
                incluye_reporte_mensual=request.POST.get('incluye_reporte_mensual') == 'on',
                incluye_soporte_24_7=request.POST.get('incluye_soporte_24_7') == 'on',
            )
            
            # Agregar servicios incluidos
            servicios_ids = request.POST.getlist('servicios_incluidos')
            for servicio_id in servicios_ids:
                servicio = Servicio.objects.get(id_servicio=servicio_id)
                plan.servicios_incluidos.add(servicio)
            
            messages.success(request, f'Plan empresarial "{plan.nombre}" creado exitosamente.')
            return redirect('planes_empresariales_crud')
            
        except Exception as e:
            messages.error(request, f'Error al crear el plan empresarial: {str(e)}')
    
    servicios = Servicio.objects.all()
    context = {
        'servicios': servicios,
    }
    return render(request, 'planes/crear_plan_empresarial.html', context)

@admin_required
def editar_plan_empresarial(request, plan_id):
    """Vista para editar un plan empresarial existente"""
    plan = get_object_or_404(PlanEmpresarial, id_plan=plan_id)
    
    if request.method == 'POST':
        try:
            plan.nombre = request.POST.get('nombre')
            plan.tipo = request.POST.get('tipo')
            plan.descripcion = request.POST.get('descripcion')
            plan.precio_mensual_por_vehiculo = request.POST.get('precio_mensual_por_vehiculo')
            plan.precio_base_mensual = request.POST.get('precio_base_mensual', 0)
            plan.vehiculos_minimos = request.POST.get('vehiculos_minimos', 5)
            plan.vehiculos_maximos = request.POST.get('vehiculos_maximos') or None
            plan.servicios_por_vehiculo_mes = request.POST.get('servicios_por_vehiculo_mes', 0)
            plan.descuento_volumen = request.POST.get('descuento_volumen', 0)
            plan.incluye_lavado_asientos = request.POST.get('incluye_lavado_asientos') == 'on'
            plan.incluye_aspirado = request.POST.get('incluye_aspirado') == 'on'
            plan.incluye_lavado_exterior = request.POST.get('incluye_lavado_exterior') == 'on'
            plan.incluye_lavado_interior_humedo = request.POST.get('incluye_lavado_interior_humedo') == 'on'
            plan.incluye_encerado = request.POST.get('incluye_encerado') == 'on'
            plan.incluye_detallado_completo = request.POST.get('incluye_detallado_completo') == 'on'
            plan.incluye_servicio_domicilio = request.POST.get('incluye_servicio_domicilio') == 'on'
            plan.incluye_mantenimiento_programado = request.POST.get('incluye_mantenimiento_programado') == 'on'
            plan.incluye_reporte_mensual = request.POST.get('incluye_reporte_mensual') == 'on'
            plan.incluye_soporte_24_7 = request.POST.get('incluye_soporte_24_7') == 'on'
            plan.save()
            
            # Actualizar servicios incluidos
            plan.servicios_incluidos.clear()
            servicios_ids = request.POST.getlist('servicios_incluidos')
            for servicio_id in servicios_ids:
                servicio = Servicio.objects.get(id_servicio=servicio_id)
                plan.servicios_incluidos.add(servicio)
            
            messages.success(request, f'Plan empresarial "{plan.nombre}" actualizado exitosamente.')
            return redirect('planes_empresariales_crud')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el plan empresarial: {str(e)}')
    
    servicios = Servicio.objects.all()
    context = {
        'plan': plan,
        'servicios': servicios,
    }
    return render(request, 'planes/editar_plan_empresarial.html', context)

@admin_required
def eliminar_plan_empresarial(request, plan_id):
    """Vista para eliminar un plan empresarial"""
    plan = get_object_or_404(PlanEmpresarial, id_plan=plan_id)
    
    if request.method == 'POST':
        try:
            # Verificar si hay suscripciones activas
            suscripciones_activas = SuscripcionEmpresarial.objects.filter(
                plan=plan, 
                estado='activa'
            ).count()
            
            if suscripciones_activas > 0:
                messages.warning(request, f'No se puede eliminar el plan "{plan.nombre}" porque tiene {suscripciones_activas} suscripciones activas. Desactivando el plan.')
                plan.activo = False
                plan.save()
            else:
                plan_nombre = plan.nombre
                plan.delete()
                messages.success(request, f'Plan empresarial "{plan_nombre}" eliminado exitosamente.')

            return redirect('planes/planes_empresariales_crud')

        except Exception as e:
            messages.error(request, f'Error al eliminar el plan empresarial: {str(e)}')
    
    # Obtener información de suscripciones para mostrar en la confirmación
    suscripciones_activas = SuscripcionEmpresarial.objects.filter(
        plan=plan, 
        estado='activa'
    ).count()
    
    context = {
        'plan': plan,
        'suscripciones_activas': suscripciones_activas,
    }
    return render(request, 'eliminar_plan_empresarial.html', context)

@admin_required
def detalle_plan_empresarial(request, plan_id):
    """Vista para ver detalles del plan empresarial"""
    plan = get_object_or_404(PlanEmpresarial, id_plan=plan_id)
    
    # Obtener suscripciones relacionadas
    suscripciones = SuscripcionEmpresarial.objects.filter(plan=plan).order_by('-fecha_inicio')[:10]
    
    # Calcular estadísticas
    total_suscripciones = SuscripcionEmpresarial.objects.filter(plan=plan).count()
    suscripciones_activas = SuscripcionEmpresarial.objects.filter(plan=plan, estado='activa').count()
    
    context = {
        'plan': plan,
        'suscripciones': suscripciones,
        'total_suscripciones': total_suscripciones,
        'suscripciones_activas': suscripciones_activas,
    }
    return render(request, 'detalle_plan_empresarial.html', context)

@admin_required
def suscripciones_empresariales_crud(request):
    """Vista para gestionar suscripciones empresariales (solo admin)"""
    suscripciones = SuscripcionEmpresarial.objects.all().order_by('-fecha_inicio')
    context = {
        'suscripciones': suscripciones,
    }
    return render(request, 'planes/suscripciones_empresariales_crud.html', context)


# ==================== VISTAS PARA SUSCRIPCIONES INDIVIDUALES ====================

@admin_required
def suscripciones_individuales_crud(request):
    """Vista para gestionar suscripciones de usuarios individuales (solo admin)"""
    suscripciones = SuscripcionUsuario.objects.select_related('usuario', 'plan').all().order_by('-fecha_inicio')
    
    # Calcular estadísticas
    suscripciones_activas = suscripciones.filter(estado='activa').count()
    suscripciones_vencidas = suscripciones.filter(estado='vencida').count()
    
    # Calcular ingresos mensuales estimados
    ingresos_mensuales = sum(
        suscripcion.plan.precio_mensual 
        for suscripcion in suscripciones.filter(estado='activa')
    )
    
    # Obtener planes disponibles para el filtro
    planes_disponibles = Plan.objects.filter(activo=True)
    
    context = {
        'suscripciones': suscripciones,
        'suscripciones_activas': suscripciones_activas,
        'suscripciones_vencidas': suscripciones_vencidas,
        'ingresos_mensuales': ingresos_mensuales,
        'planes_disponibles': planes_disponibles,
    }
    return render(request, 'planes/suscripciones_individuales_crud.html', context)

@admin_required
def crear_suscripcion_individual(request):
    """Vista para crear una nueva suscripción individual"""
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        plan_id = request.POST.get('plan')
        
        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            plan = Plan.objects.get(id_plan=plan_id)
            
            # Verificar si el usuario ya tiene una suscripción activa
            suscripcion_existente = SuscripcionUsuario.objects.filter(
                usuario=usuario, 
                estado='activa'
            ).first()
            
            if suscripcion_existente:
                messages.error(request, f'El usuario {usuario.nombre_completo} ya tiene una suscripción activa.')
                return redirect('suscripciones_individuales_crud')
            
            # Crear nueva suscripción
            fecha_inicio = timezone.now()
            fecha_fin = fecha_inicio + timedelta(days=30)  # 30 días por defecto
            
            suscripcion = SuscripcionUsuario.objects.create(
                usuario=usuario,
                plan=plan,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado='activa',
                servicios_utilizados_mes=0,
                ultimo_reinicio_contador=fecha_inicio,
                auto_renovar=True
            )
            
            messages.success(request, f'Suscripción creada exitosamente para {usuario.nombre_completo}.')
            return redirect('suscripciones_individuales_crud')
            
        except (Usuario.DoesNotExist, Plan.DoesNotExist):
            messages.error(request, 'Usuario o plan no encontrado.')
            return redirect('suscripciones_individuales_crud')
    
    # GET request - mostrar formulario
    usuarios = Usuario.objects.filter(rol='cliente').order_by('nombre_completo')
    planes = Plan.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'usuarios': usuarios,
        'planes': planes,
    }
    return render(request, 'planes/crear_suscripcion_individual.html', context)

@admin_required
def editar_suscripcion_individual(request, suscripcion_id):
    """Vista para editar una suscripción individual"""
    try:
        suscripcion = SuscripcionUsuario.objects.get(id_suscripcion=suscripcion_id)
    except SuscripcionUsuario.DoesNotExist:
        messages.error(request, 'Suscripción no encontrada.')
        return redirect('suscripciones_individuales_crud')
    
    if request.method == 'POST':
        estado = request.POST.get('estado')
        auto_renovar = request.POST.get('auto_renovar') == 'on'
        fecha_fin = request.POST.get('fecha_fin')
        
        # Actualizar suscripción
        suscripcion.estado = estado
        suscripcion.auto_renovar = auto_renovar
        
        if fecha_fin:
            try:
                from datetime import datetime
                suscripcion.fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Formato de fecha inválido.')
                return redirect('editar_suscripcion_individual', suscripcion_id=suscripcion_id)
        
        suscripcion.save()
        
        messages.success(request, f'Suscripción de {suscripcion.usuario.nombre_completo} actualizada exitosamente.')
        return redirect('suscripciones_individuales_crud')
    
    context = {
        'suscripcion': suscripcion,
    }
    return render(request, 'planes/editar_suscripcion_individual.html', context)

@admin_required
def eliminar_suscripcion_individual(request, suscripcion_id):
    """Vista para eliminar una suscripción individual"""
    try:
        suscripcion = SuscripcionUsuario.objects.get(id_suscripcion=suscripcion_id)
    except SuscripcionUsuario.DoesNotExist:
        messages.error(request, 'Suscripción no encontrada.')
        return redirect('suscripciones_individuales_crud')
    
    if request.method == 'POST':
        usuario_nombre = suscripcion.usuario.nombre_completo
        suscripcion.delete()
        messages.success(request, f'Suscripción de {usuario_nombre} eliminada exitosamente.')
        return redirect('suscripciones_individuales_crud')
    
    context = {
        'suscripcion': suscripcion,
    }
    return render(request, 'planes/eliminar_suscripcion_individual.html', context)

@admin_required
def pausar_suscripcion_individual(request, suscripcion_id):
    """Vista para pausar una suscripción individual"""
    try:
        suscripcion = SuscripcionUsuario.objects.get(id_suscripcion=suscripcion_id)
    except SuscripcionUsuario.DoesNotExist:
        messages.error(request, 'Suscripción no encontrada.')
        return redirect('suscripciones_individuales_crud')
    
    if suscripcion.estado == 'activa':
        suscripcion.estado = 'pausada'
        suscripcion.save()
        messages.success(request, f'Suscripción de {suscripcion.usuario.nombre_completo} pausada exitosamente.')
    else:
        messages.warning(request, 'Solo se pueden pausar suscripciones activas.')
    
    return redirect('suscripciones_individuales_crud')

@admin_required
def historial_pagos_suscripcion(request, suscripcion_id):
    """Vista para ver el historial de pagos de una suscripción"""
    try:
        suscripcion = SuscripcionUsuario.objects.get(id_suscripcion=suscripcion_id)
    except SuscripcionUsuario.DoesNotExist:
        messages.error(request, 'Suscripción no encontrada.')
        return redirect('suscripciones_individuales_crud')
    
    pagos = HistorialPagosSuscripcion.objects.filter(suscripcion=suscripcion).order_by('-fecha_pago')
    
    context = {
        'suscripcion': suscripcion,
        'pagos': pagos,
    }
    return render(request, 'planes/historial_pagos_suscripcion.html', context)


@admin_required
def perfil_admin(request):
    """Vista para editar el perfil del administrador"""
    admin_user = request.user
    
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, request.FILES, instance=admin_user)
        
        if form.is_valid():
            # Guardar los datos del formulario
            admin_actualizado = form.save()
            
            # Cambiar la contraseña si se proporcionó
            nueva_contrasena = form.cleaned_data.get('nueva_contrasena')
            if nueva_contrasena:
                admin_actualizado.set_password(nueva_contrasena)
                admin_actualizado.save()
                messages.success(request, 'Perfil y contraseña actualizados correctamente.')
            else:
                messages.success(request, 'Perfil actualizado correctamente.')
            
            return redirect('perfil_admin')
        else:
            # Si hay errores en el formulario, mostrarlos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AdminProfileForm(instance=admin_user)
    
    context = {
        'form': form,
        'admin_user': admin_user,
    }
    return render(request, 'usuarios/perfil_admin.html', context)


# NUEVAS VISTAS AJAX PARA CRUD DE CITAS
@admin_required
def obtener_servicios_empresa(request):
    """Vista AJAX para obtener los servicios que presta una empresa específica"""
    print(f"🔧 obtener_servicios_empresa llamada")
    empresa_id = request.GET.get('empresa_id')
    print(f"🔧 empresa_id recibido: {empresa_id}")
    
    if not empresa_id:
        print(f"❌ No se proporcionó empresa_id")
        return JsonResponse({'error': 'ID de empresa requerido'}, status=400)
    
    try:
        empresa = Empresa.objects.get(id_empresa=empresa_id)
        print(f"🔧 Empresa encontrada: {empresa.nombre_empresa}")
        
        # Método 1: Intentar obtener servicios a través del modelo intermedio EmpresaServicio
        servicios_empresa = EmpresaServicio.objects.filter(empresa=empresa).select_related('servicio')
        print(f"🔧 Servicios encontrados via EmpresaServicio: {servicios_empresa.count()}")
        
        servicios = []
        
        # Si hay servicios asignados a través de EmpresaServicio
        if servicios_empresa.exists():
            for empresa_servicio in servicios_empresa:
                servicios.append({
                    'id_servicio': empresa_servicio.servicio.id_servicio,
                    'nombre_servicio': empresa_servicio.servicio.nombre_servicio,
                    'precio': empresa_servicio.servicio.precio,
                    'descripcion': empresa_servicio.servicio.descripcion
                })
        else:
            # Método 2: Si no hay registros en EmpresaServicio, usar la relación ManyToMany directamente
            print(f"🔧 No hay servicios en EmpresaServicio, usando relación directa many-to-many")
            servicios_directos = empresa.servicios.all()
            print(f"🔧 Servicios encontrados via many-to-many: {servicios_directos.count()}")
            
            for servicio in servicios_directos:
                servicios.append({
                    'id_servicio': servicio.id_servicio,
                    'nombre_servicio': servicio.nombre_servicio,
                    'precio': servicio.precio,
                    'descripcion': servicio.descripcion
                })
        
        # Método 3: Si aún no hay servicios, devolver todos los servicios disponibles como fallback
        if not servicios:
            print(f"🔧 No hay servicios asignados, devolviendo todos los servicios disponibles")
            todos_servicios = Servicio.objects.all()
            for servicio in todos_servicios:
                servicios.append({
                    'id_servicio': servicio.id_servicio,
                    'nombre_servicio': servicio.nombre_servicio,
                    'precio': servicio.precio,
                    'descripcion': servicio.descripcion
                })
        
        print(f"🔧 Servicios procesados: {len(servicios)}")
        resultado = {
            'servicios': servicios,
            'empresa_nombre': empresa.nombre_empresa
        }
        print(f"🔧 Resultado final: {resultado}")
        
        return JsonResponse(resultado)
    except Empresa.DoesNotExist:
        print(f"❌ Empresa no encontrada con ID: {empresa_id}")
        return JsonResponse({'error': 'Empresa no encontrada'}, status=404)
    except Exception as e:
        print(f"❌ Error en obtener_servicios_empresa: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@admin_required  
def obtener_horas_disponibles(request):
    """Vista AJAX para obtener las horas disponibles para una fecha y empresa específica"""
    fecha_str = request.GET.get('fecha')
    empresa_id = request.GET.get('empresa_id')
    
    if not fecha_str:
        return JsonResponse({'error': 'Fecha requerida'}, status=400)
    
    try:
        from datetime import datetime
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hoy = datetime.now().date()
        ahora = datetime.now()
        
        # Obtener reservas existentes para esa fecha
        reservas_fecha = Reserva.objects.filter(fecha=fecha)
        
        # Si se especifica empresa, filtrar por empresa
        if empresa_id:
            reservas_fecha = reservas_fecha.filter(empresa_id=empresa_id)
        
        # Obtener horas ocupadas
        horas_ocupadas = set()
        for reserva in reservas_fecha:
            horas_ocupadas.add(reserva.hora.strftime('%H:%M'))
        
        # Generar horas disponibles
        horas_disponibles = []
        
        for h in range(8, 16):  # De 08:00 a 15:00
            hora_formateada = f"{h:02d}:00"
            
            # Si la fecha es hoy, verificar que la hora no haya pasado
            if fecha == hoy and h <= ahora.hour:
                continue
            
            # Verificar si la hora no está ocupada
            if hora_formateada not in horas_ocupadas:
                # Convertir a formato 12h para mostrar
                hora_12h = convertir_hora_12h(hora_formateada)
                horas_disponibles.append({
                    'valor': hora_12h,
                    'texto': hora_12h
                })
        
        return JsonResponse({
            'horas_disponibles': horas_disponibles,
            'fecha': fecha_str
        })
        
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


