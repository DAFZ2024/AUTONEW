
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

# Formulario personalizado para recuperación de contraseña por campo 'correo'
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Correo electrónico", max_length=254)

    def get_users(self, email):
        UserModel = get_user_model()
        return UserModel.objects.filter(correo__iexact=email, is_active=True)
from django import forms
from .models import Comentario,Reserva,Usuario, MensajeQueja,Servicio,Empresa,ReservaServicio,SolicitudServicioEmpresa,Plan


class ComentarioClienteForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario']  # Solo el campo comentario se muestra al usuario
        widgets = {
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Escribe la descripción'}),
        }


class ReservaForm(forms.ModelForm):
    servicios = forms.ModelMultipleChoiceField(
        queryset=Servicio.objects.all(),    
        widget=forms.CheckboxSelectMultiple  # Puedes cambiar el widget según necesites
    )

    class Meta:
        model = Reserva
        fields = ['empresa', 'fecha', 'hora', 'servicios']



class UsuariosForm(forms.ModelForm):
    ROLES = [
        ('admin', 'Admin'),
        ('cliente', 'Cliente'),
    ]
    rol = forms.ChoiceField(choices=ROLES)
    class Meta:
        model = Usuario 
        fields = ['nombre_completo', 'nombre_usuario', 'correo','telefono','direccion','rol']


class ReservaCrudForm(forms.ModelForm):
    servicios = forms.ModelMultipleChoiceField(
        queryset=Servicio.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Reserva
        fields = ['empresa', 'fecha', 'hora', 'servicios', 'estado'] 


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['id_comentario', 'comentario', 'fecha', 'usuario']


class QuejaForm(forms.ModelForm):
    class Meta:
        model = MensajeQueja
        fields = ['id_mensaje', 'contenido','estado']

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre_servicio', 'descripcion', 'precio']
        widgets = {
            'nombre_servicio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Lavado Premium',
                'maxlength': '255'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe detalladamente qué incluye este servicio...',
                'rows': 4
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'step': '0.01'
            }),
        }
        labels = {
            'nombre_servicio': 'Nombre del Servicio',
            'descripcion': 'Descripción',
            'precio': 'Precio (COP)',
        }
        help_texts = {
            'nombre_servicio': 'Nombre único para identificar el servicio',
            'descripcion': 'Explica qué incluye y cómo se realiza este servicio',
            'precio': 'Precio en pesos colombianos (COP)',
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_nombre_servicio(self):
        nombre = self.cleaned_data.get('nombre_servicio')
        if nombre:
            nombre = nombre.strip()
            # Verificar si ya existe otro servicio con el mismo nombre (excluyendo el actual si es edición)
            if self.instance and self.instance.pk:
                if Servicio.objects.filter(nombre_servicio__iexact=nombre).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("Ya existe un servicio con este nombre.")
            else:
                if Servicio.objects.filter(nombre_servicio__iexact=nombre).exists():
                    raise forms.ValidationError("Ya existe un servicio con este nombre.")
        return nombre

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['id_empresa','nombre_empresa', 'direccion']

class EmpresaRegistroForm(forms.ModelForm):
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingresa tu contraseña',
            'minlength': '6'
        }),
        min_length=6,
        help_text="La contraseña debe tener al menos 6 caracteres"
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirma tu contraseña',
            'minlength': '6'
        }),
        min_length=6
    )
    
    class Meta:
        model = Empresa
        fields = ['nombre_empresa', 'direccion', 'telefono', 'email']
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre de la empresa',
                'required': True
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Dirección completa',
                'required': True
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Número de teléfono',
                'pattern': '[0-9]{10}',
                'title': 'Ingresa un número de teléfono válido (10 dígitos)',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Correo electrónico',
                'required': True
            }),
        }
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.isdigit():
            raise forms.ValidationError("El teléfono debe contener solo números")
        if telefono and len(telefono) < 10:
            raise forms.ValidationError("El teléfono debe tener al menos 10 dígitos")
        return telefono
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Empresa.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una empresa registrada con este correo electrónico")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get("contrasena")
        confirmar_contrasena = cleaned_data.get("confirmar_contrasena")
        
        if contrasena and confirmar_contrasena:
            if contrasena != confirmar_contrasena:
                raise forms.ValidationError("Las contraseñas no coinciden")
        
        return cleaned_data

class ProfileUserForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'nombre_completo',
            'nombre_usuario',
            'correo',
            'telefono',
            'direccion',
            'profile_picture',
        ]

class EmpresaPerfilForm(forms.ModelForm):
    """Formulario para editar el perfil de la empresa"""
    
    contrasena_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual (opcional para cambiar contraseña)'
        }),
        required=False,
        label='Contraseña Actual'
    )
    
    nueva_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña (opcional)'
        }),
        required=False,
        label='Nueva Contraseña'
    )
    
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        required=False,
        label='Confirmar Nueva Contraseña'
    )
    
    class Meta:
        model = Empresa
        fields = ['nombre_empresa', 'direccion', 'telefono', 'email']
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección de la empresa'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        contrasena_actual = cleaned_data.get('contrasena_actual')
        nueva_contrasena = cleaned_data.get('nueva_contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')
        
        # Si se quiere cambiar la contraseña
        if nueva_contrasena or confirmar_contrasena:
            if not contrasena_actual:
                raise forms.ValidationError("Debe proporcionar la contraseña actual para cambiar la contraseña.")
            
            if nueva_contrasena != confirmar_contrasena:
                raise forms.ValidationError("Las nuevas contraseñas no coinciden.")
            
            if len(nueva_contrasena) < 6:
                raise forms.ValidationError("La nueva contraseña debe tener al menos 6 caracteres.")
        
        return cleaned_data


class SolicitudServicioEmpresaForm(forms.ModelForm):
    """Formulario para solicitar nuevos servicios por parte de las empresas"""
    
    class Meta:
        model = SolicitudServicioEmpresa
        fields = ['servicio_solicitado', 'motivo_solicitud', 'usuario_responsable', 'telefono_contacto']
        widgets = {
            'servicio_solicitado': forms.Select(attrs={
                'class': 'form-control',
            }),
            'motivo_solicitud': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explique por qué necesita este servicio y cómo lo utilizará...',
                'rows': 4
            }),
            'usuario_responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del responsable'
            }),
            'telefono_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono para contacto'
            }),
        }
        labels = {
            'servicio_solicitado': 'Servicio Solicitado',
            'motivo_solicitud': 'Motivo de la Solicitud',
            'usuario_responsable': 'Persona Responsable',
            'telefono_contacto': 'Teléfono de Contacto',
        }
    
    def clean_telefono_contacto(self):
        telefono = self.cleaned_data.get('telefono_contacto')
        if telefono:
            # Validación básica de formato de teléfono
            import re
            if not re.match(r'^[\d\s\+\-\(\)]{7,15}$', telefono):
                raise forms.ValidationError("Ingrese un número de teléfono válido.")
        return telefono
    
    def clean_motivo_solicitud(self):
        motivo = self.cleaned_data.get('motivo_solicitud')
        if motivo and len(motivo.strip()) < 20:
            raise forms.ValidationError("Por favor, proporcione una explicación más detallada (mínimo 20 caracteres).")
        return motivo


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = [
            'nombre', 'tipo', 'descripcion', 'precio_mensual', 
            'cantidad_servicios_mes', 'servicios_incluidos',
            'incluye_lavado_asientos', 'incluye_aspirado', 'incluye_lavado_exterior',
            'incluye_lavado_interior_humedo', 'incluye_encerado', 'incluye_detallado_completo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300',
                'placeholder': 'Ej: Plan Premium'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300',
                'placeholder': 'Describe los beneficios y características del plan...',
                'rows': 4
            }),
            'precio_mensual': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01'
            }),
            'cantidad_servicios_mes': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300',
                'placeholder': '0 = Ilimitado',
                'min': '0'
            }),
            'servicios_incluidos': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre': 'Nombre del Plan',
            'tipo': 'Tipo de Plan',
            'descripcion': 'Descripción',
            'precio_mensual': 'Precio Mensual ($)',
            'cantidad_servicios_mes': 'Servicios por Mes',
            'servicios_incluidos': 'Servicios Incluidos',
            'incluye_lavado_asientos': 'Lavado de Asientos',
            'incluye_aspirado': 'Aspirado',
            'incluye_lavado_exterior': 'Lavado Exterior',
            'incluye_lavado_interior_humedo': 'Lavado Interior Húmedo',
            'incluye_encerado': 'Encerado',
            'incluye_detallado_completo': 'Detallado Completo',
        }
    
    def clean_precio_mensual(self):
        precio = self.cleaned_data.get('precio_mensual')
        if precio and precio < 0:
            raise forms.ValidationError("El precio debe ser mayor o igual a 0.")
        return precio
    
    def clean_cantidad_servicios_mes(self):
        cantidad = self.cleaned_data.get('cantidad_servicios_mes')
        if cantidad and cantidad < 0:
            raise forms.ValidationError("La cantidad de servicios debe ser mayor o igual a 0.")
        return cantidad


class AdminProfileForm(forms.ModelForm):
    """Formulario para editar el perfil del administrador"""
    
    contrasena_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-6 py-4 bg-slate-50/50 border-2 border-slate-200/70 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 hover:border-slate-300 hover:bg-white placeholder-slate-400 text-slate-700 font-medium',
            'placeholder': 'Contraseña actual (opcional para cambiar contraseña)'
        }),
        required=False,
        label='Contraseña Actual'
    )
    
    nueva_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-6 py-4 bg-slate-50/50 border-2 border-slate-200/70 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 hover:border-slate-300 hover:bg-white placeholder-slate-400 text-slate-700 font-medium',
            'placeholder': 'Nueva contraseña (opcional)'
        }),
        required=False,
        label='Nueva Contraseña'
    )
    
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-6 py-4 bg-slate-50/50 border-2 border-slate-200/70 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 hover:border-slate-300 hover:bg-white placeholder-slate-400 text-slate-700 font-medium',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        required=False,
        label='Confirmar Nueva Contraseña'
    )
    
    class Meta:
        model = Usuario
        fields = [
            'nombre_completo',
            'nombre_usuario',
            'correo',
            'telefono',
            'direccion',
            'profile_picture',
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'w-full px-6 py-4 bg-slate-50/50 border-2 border-slate-200/70 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 hover:border-slate-300 hover:bg-white placeholder-slate-400 text-slate-700 font-medium',
                'placeholder': 'Ingresa tu nombre completo'
            }),
            'nombre_usuario': forms.TextInput(attrs={
                'class': 'w-full px-6 py-4 bg-slate-50/50 border-2 border-slate-200/70 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 hover:border-slate-300 hover:bg-white placeholder-slate-400 text-slate-700 font-medium',
                'placeholder': 'Tu nombre de usuario'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'w-full px-6 py-4 bg-slate-50/50 border-2 border-slate-200/70 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 hover:border-slate-300 hover:bg-white placeholder-slate-400 text-slate-700 font-medium',
                'placeholder': 'tu@email.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-6 py-4 bg-slate-50/50 border-2 border-slate-200/70 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 hover:border-slate-300 hover:bg-white placeholder-slate-400 text-slate-700 font-medium',
                'placeholder': '+57 300 123 4567'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'w-full px-6 py-4 bg-slate-50/50 border-2 border-slate-200/70 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 hover:border-slate-300 hover:bg-white placeholder-slate-400 text-slate-700 font-medium',
                'placeholder': 'Ingresa tu dirección completa'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'nombre_usuario': 'Nombre de Usuario',
            'correo': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección Completa',
            'profile_picture': 'Foto de Perfil',
        }
    
    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data.get('nombre_usuario')
        if nombre_usuario:
            # Verificar que el nombre de usuario no esté en uso por otro usuario
            if Usuario.objects.filter(nombre_usuario=nombre_usuario).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return nombre_usuario
    
    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if correo:
            # Verificar que el correo no esté en uso por otro usuario
            if Usuario.objects.filter(correo=correo).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return correo
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            import re
            if not re.match(r'^[\d\s\+\-\(\)]{7,15}$', telefono):
                raise forms.ValidationError("Ingrese un número de teléfono válido.")
        return telefono
    
    def clean(self):
        cleaned_data = super().clean()
        contrasena_actual = cleaned_data.get('contrasena_actual')
        nueva_contrasena = cleaned_data.get('nueva_contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')
        
        # Si se quiere cambiar la contraseña
        if nueva_contrasena or confirmar_contrasena:
            if not contrasena_actual:
                raise forms.ValidationError("Debe proporcionar la contraseña actual para cambiar la contraseña.")
            
            # Verificar que la contraseña actual sea correcta
            if contrasena_actual and not self.instance.check_password(contrasena_actual):
                raise forms.ValidationError("La contraseña actual no es correcta.")
            
            if nueva_contrasena != confirmar_contrasena:
                raise forms.ValidationError("Las nuevas contraseñas no coinciden.")
            
            if len(nueva_contrasena) < 6:
                raise forms.ValidationError("La nueva contraseña debe tener al menos 6 caracteres.")
        
        return cleaned_data