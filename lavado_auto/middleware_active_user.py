from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout

class ActiveUserMiddleware(MiddlewareMixin):
    """
    Middleware para verificar que los usuarios autenticados estén activos.
    Si un usuario está inactivo, cierra su sesión automáticamente.
    """
    
    def process_request(self, request):
        # URLs que no requieren verificación
        excluded_patterns = [
            '/login', '/logincrud', '/logout', '/logoutcrud', 
            '/static', '/media', '/admin', '/registro'
        ]
        
        current_path = request.path_info.rstrip('/')
        
        # Excluir URLs públicas
        if any(current_path.startswith(pattern) for pattern in excluded_patterns):
            return None
        
        # Si el usuario está autenticado, verificar que esté activo
        if request.user.is_authenticated:
            if hasattr(request.user, 'is_active') and not request.user.is_active:
                print(f"🔐 Usuario inactivo detectado: {request.user.nombre_usuario} - Cerrando sesión")
                logout(request)
                messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador para más información.')
                return redirect('login')
        
        return None
