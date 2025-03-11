from django.contrib import admin
from .models import Usuario, Servicio, Reserva, Pago, PasarelaDePago, MensajeQueja, Comentario

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
    list_display = ('usuario', 'fecha_envio', 'estado')
    search_fields = ('usuario__nombre_usuario',)

class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'comentario')
    search_fields = ('usuario__nombre_usuario',)

# Registrar tus modelos aquí.
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(Reserva, ReservaAdmin) 
admin.site.register(Pago, PagoAdmin)
admin.site.register(PasarelaDePago, PasarelaDePagoAdmin)
admin.site.register(MensajeQueja, MensajeQuejaAdmin)
admin.site.register(Comentario, ComentarioAdmin)