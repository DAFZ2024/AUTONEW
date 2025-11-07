from django.contrib import admin
from .models import (
    Usuario, Servicio, Reserva, Pago, PasarelaDePago, MensajeQueja, 
    Comentario, Plan, SuscripcionUsuario, HistorialPagosSuscripcion, 
    PlanServicio, Empresa
)

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre_usuario', 'correo', 'is_active', 'is_staff')
    search_fields = ('nombre_usuario', 'correo')
    list_filter = ('is_active', 'is_staff', 'rol')

class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre_servicio', 'precio')
    search_fields = ('nombre_servicio',)

class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mostrar_servicios', 'fecha', 'hora')
    search_fields = ('usuario__nombre_usuario', 'servicios__nombre_servicio')

    def mostrar_servicios(self, obj):
        return ", ".join([s.nombre_servicio for s in obj.servicios.all()])

    mostrar_servicios.short_description = "Servicios"


    
class PagoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'reserva', 'monto', 'fecha_pago')
    search_fields = ('usuario__nombre_usuario',)
    list_filter = ('metodo_pago',)

class PasarelaDePagoAdmin(admin.ModelAdmin):
    list_display = ('nombre_pasarela', 'estado_transaccion')

class MensajeQuejaAdmin(admin.ModelAdmin):
    list_display = ('numero_radicado', 'tipo_pqrs', 'usuario', 'urgencia', 'estado', 'fecha_envio')
    search_fields = ('numero_radicado', 'usuario__nombre_usuario', 'nombre_contacto', 'contenido')
    list_filter = ('tipo_pqrs', 'urgencia', 'estado', 'fecha_envio', 'servicio_bd')
    readonly_fields = ('numero_radicado', 'fecha_envio', 'fecha_actualizacion')
    ordering = ('-fecha_envio',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('numero_radicado', 'tipo_pqrs', 'urgencia', 'estado')
        }),
        ('Datos de Contacto', {
            'fields': ('usuario', 'nombre_contacto', 'email_contacto')
        }),
        ('Detalles del PQRS', {
            'fields': ('servicio_relacionado', 'servicio_bd', 'contenido')
        }),
        ('Respuesta', {
            'fields': ('respuesta', 'fecha_respuesta')
        }),
        ('Fechas', {
            'fields': ('fecha_envio', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
        ('Otros', {
            'fields': ('acepto_terminos',),
            'classes': ('collapse',)
        })
    )

class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'comentario')
    search_fields = ('usuario__nombre_usuario',)

class PlanServicioInline(admin.TabularInline):
    """Inline para gestionar servicios con descuentos desde el admin de Plan"""
    model = Plan.servicios_incluidos.through
    extra = 1
    fields = ('servicio', 'porcentaje_descuento')
    verbose_name = 'Servicio incluido'
    verbose_name_plural = 'Servicios incluidos con descuentos'

class PlanAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'precio_mensual', 'cantidad_servicios_mes', 'activo')
    search_fields = ('nombre', 'tipo')
    list_filter = ('tipo', 'activo', 'fecha_creacion')
    inlines = [PlanServicioInline]
    exclude = ('servicios_incluidos',)  # Excluimos el campo ManyToMany porque usamos el inline

class SuscripcionUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'plan', 'estado', 'fecha_inicio', 'fecha_fin', 'servicios_utilizados_mes')
    search_fields = ('usuario__nombre_usuario', 'plan__nombre')
    list_filter = ('estado', 'auto_renovar', 'fecha_inicio')
    readonly_fields = ('fecha_inicio',)

class HistorialPagosSuscripcionAdmin(admin.ModelAdmin):
    list_display = ('suscripcion', 'monto', 'estado', 'fecha_pago', 'referencia_pago')
    search_fields = ('suscripcion__usuario__nombre_usuario', 'referencia_pago')
    list_filter = ('estado', 'metodo_pago', 'fecha_pago')
    readonly_fields = ('fecha_pago',)


class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_empresa', 
        'email', 
        'telefono', 
        'verificada', 
        'datos_bancarios_verificados',
        'is_active'
    )
    search_fields = ('nombre_empresa', 'email', 'nit_empresa', 'razon_social')
    list_filter = (
        'verificada', 
        'datos_bancarios_verificados', 
        'is_active', 
        'tipo_cuenta',
        'regimen_tributario'
    )
    readonly_fields = ('fecha_registro', 'fecha_verificacion_bancaria')
    
    fieldsets = (
        ('Información Básica de la Empresa', {
            'fields': (
                'nombre_empresa',
                'razon_social',
                'nit_empresa',
                'direccion',
                'latitud',
                'longitud',
            )
        }),
        ('Información de Contacto', {
            'fields': (
                'email',
                'telefono',
                'email_facturacion',
                'telefono_facturacion',
                'responsable_pagos',
            )
        }),
        ('Información Bancaria', {
            'fields': (
                'titular_cuenta',
                'tipo_documento_titular',
                'numero_documento_titular',
                'banco',
                'tipo_cuenta',
                'numero_cuenta',
                'swift_code',
                'iban',
                'notas_bancarias',
            ),
            'description': 'Datos bancarios para realizar pagos a la empresa por los servicios prestados'
        }),
        ('Información Fiscal', {
            'fields': (
                'regimen_tributario',
            ),
            'classes': ('collapse',)
        }),
        ('Verificación de Datos Bancarios', {
            'fields': (
                'datos_bancarios_verificados',
                'fecha_verificacion_bancaria',
                'verificado_por',
            ),
            'classes': ('collapse',),
            'description': 'Información de verificación de los datos bancarios por el administrador'
        }),
        ('Seguridad y Acceso', {
            'fields': (
                'contrasena',
                'token_reset',
                'verificada',
                'is_active',
                'failed_login_attempts',
                'last_failed_login',
                'lockout_time',
                'first_warning_sent',
            ),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': (
                'fecha_registro',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Guardar el modelo y si se marca como verificado, 
        registrar la fecha y el usuario que lo verificó
        """
        if change:  # Solo si es una edición
            # Obtener el objeto anterior de la base de datos
            try:
                obj_anterior = Empresa.objects.get(pk=obj.pk)
                # Si datos_bancarios_verificados cambió de False a True
                if not obj_anterior.datos_bancarios_verificados and obj.datos_bancarios_verificados:
                    from django.utils import timezone
                    obj.fecha_verificacion_bancaria = timezone.now()
                    obj.verificado_por = request.user
            except Empresa.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)


# Registrar tus modelos aquí.
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(Reserva, ReservaAdmin) 
admin.site.register(Pago, PagoAdmin)
admin.site.register(PasarelaDePago, PasarelaDePagoAdmin)
admin.site.register(MensajeQueja, MensajeQuejaAdmin)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(SuscripcionUsuario, SuscripcionUsuarioAdmin)
admin.site.register(HistorialPagosSuscripcion, HistorialPagosSuscripcionAdmin)
admin.site.register(Empresa, EmpresaAdmin)