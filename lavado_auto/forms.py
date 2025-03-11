from django import forms
from .models import Comentario,Reserva,Usuario, MensajeQueja,Servicio,Empresa,ReservaServicio


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
        fields = ['id_servicio','nombre_servicio', 'descripcion','precio']

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['id_empresa','nombre_empresa', 'direccion']

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