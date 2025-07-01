from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

class AdminCRUDMiddleware(MiddlewareMixin):
    """
    Middleware para proteger todas las URLs del CRUD y asegurar que solo 
    administradores autenticados puedan acceder.
    """
    
    def process_request(self, request):
        # URLs que requieren protección de admin (SIN /homecrud)
        crud_patterns = [
            '/usuarioscrud', '/citascrud', '/quejascrud', 
            '/comentarioscrud', '/servicioscrud', '/empresascrud', '/citascomcrud'
        ]
        
        current_path = request.path_info.rstrip('/')
        
        # Excluir URLs que no necesitan protección
        excluded_patterns = ['/logincrud', '/logoutcrud', '/static', '/media', '/admin', '/', '/homecrud']
        if any(current_path.startswith(pattern) for pattern in excluded_patterns):
            return None
        
        # Si es una URL del CRUD, verificar acceso
        if any(current_path.startswith(pattern) for pattern in crud_patterns):
            print(f"\n🔍 MIDDLEWARE DEBUG:")
            print(f"   📍 URL solicitada: {current_path}")
            print(f"   👤 Usuario: {request.user}")
            print(f"   🔐 Autenticado: {request.user.is_authenticated}")
            
            if not request.user.is_authenticated:
                print(f"   ❌ Usuario NO autenticado - Redirigiendo a login")
                messages.error(request, 'Debes iniciar sesión como administrador.')
                return redirect('logincrud')
            
            # Si está autenticado, verificar rol
            if hasattr(request.user, 'nombre_usuario'):
                print(f"   👤 Nombre usuario: {request.user.nombre_usuario}")
            
            user_rol = getattr(request.user, 'rol', 'NO_ROL')
            print(f"   🎭 Rol del usuario: '{user_rol}'")
            print(f"   🔍 Tipo de rol: {type(user_rol)}")
            print(f"   ✅ Comparación rol == 'admin': {user_rol == 'admin'}")
            
            if user_rol != 'admin':
                print(f"   ❌ ACCESO DENEGADO - Rol incorrecto: '{user_rol}'")
                messages.error(request, f'Acceso denegado. Rol actual: {user_rol}')
                return redirect('logincrud')
            
            print(f"   ✅ ACCESO PERMITIDO para {request.user.nombre_usuario}")
        
        return None
