"""
URL configuration for autonew project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import RedirectView

from django.contrib.auth import views as auth_views
from lavado_auto.forms import CustomPasswordResetForm
from lavado_auto import views
from lavado_auto.views import get_horas, cambiar_estado_reserva
from lavado_auto.cookie_views import CookieConsentView, cookie_status, UserPreferencesView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/pagos/', views.gestion_pagos_empresas, name='admin_pagos'),
    path('',views.home, name = 'home'),
    path('ajax/servicios/', views.servicios_page_ajax, name='servicios_page_ajax'),
    path('ajax/servicios-home/', views.servicios_ajax, name='servicios_home_ajax'),
    path('ajax/empresas/', views.empresas_ajax, name='empresas_ajax'),
    path('ajax/planes/', views.planes_ajax, name='planes_ajax'),
    path('nosotros/',views.nosotros, name = 'nosotros'),
    path('servicios/',views.servicios, name = 'servicios'),
    path('planes/',views.planes_view, name = 'planes'),
    path('planes-empresariales/',views.planes_empresariales, name = 'planes_empresariales'),
    path('solicitar-contacto-plan/', views.solicitar_contacto_plan, name='solicitar_contacto_plan'),
    path('reservas/',views.reservas, name = 'reservas'),
    path('obtener-servicios/', views.obtener_servicios, name='obtener_servicios'),
    path('obtener_servicios_plan/', views.obtener_servicios_plan, name='obtener_servicios_plan'),
    path('obtener-empresas-por-servicios/', views.obtener_empresas_por_servicios, name='obtener_empresas_por_servicios'),
    path('obtener-info-empresa/', views.obtener_info_empresa, name='obtener_info_empresa'),
    path('obtener-info-servicio/', views.obtener_info_servicio, name='obtener_info_servicio'),
    path('get-horas/', views.get_horas, name='get_horas'),
    path('get-horas-edicion/', views.get_horas_edicion, name='get_horas_edicion'),
    path('obtener-horas/', views.get_horas, name='obtener_horas'),
    path('contacto/',views.contacto, name = 'contacto'),
    path('faq/',views.faq, name = 'faq'),
    path('blog/',views.blog, name = 'blog'),
    # Recuperación de contraseña (Django auth)
    path('resetcorreo/', auth_views.PasswordResetView.as_view(
        template_name='auth/reset_correo.html',
        form_class=CustomPasswordResetForm,
        email_template_name='auth/password_reset_email.txt',
        html_email_template_name='auth/password_reset_email.html',
        subject_template_name='auth/password_reset_subject.txt'
    ), name='password_reset'),
    path('resetcorreo/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='auth/reset_correo_enviado.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/reset_contrasena.html'), name='password_reset_confirm'),
    path('reset/completo/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/reset_completo.html'), name='password_reset_complete'),
    
    # Recuperación de contraseña para EMPRESAS
    path('empresa/reset/', views.empresa_password_reset, name='empresa_password_reset'),
    path('empresa/reset/enviado/', views.empresa_password_reset_done, name='empresa_password_reset_done'),
    path('empresa/reset/<str:token>/', views.empresa_password_reset_confirm, name='empresa_password_reset_confirm'),
    path('empresa/reset/completo/', views.empresa_password_reset_complete, name='empresa_password_reset_complete'),
    
    path('login/',views.login, name = 'login'),
    path('logout/', views.logout, name='logout'),
    path('comentarios/', views.comentarios, name='comentarios'),
    path('citas/', views.citas, name='citas'),
    path('api/hours/', get_horas, name='get_horas'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('empresas/', views.empresas, name='empresas'),
    
    # URLs para gestión avanzada de citas
    path('obtener-detalles-reserva/<int:reserva_id>/', views.obtener_detalles_reserva, name='obtener_detalles_reserva'),
    path('cancelar-reserva/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('editar-reserva/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path('repetir-reserva/<int:reserva_id>/', views.repetir_reserva, name='repetir_reserva'),
    path('calificar-servicio/<int:reserva_id>/', views.calificar_servicio, name='calificar_servicio'),
    path('get-empresas-verificadas/', views.get_empresas_verificadas, name='get_empresas_verificadas'),

    # crud
    path('logincrud/',views.login_crud, name='logincrud'),
    path('logoutcrud/', views.logout_view, name='logout_view'),
    path('homecrud/',views.home_crud, name='homecrud'),
    path('perfil-admin/', views.perfil_admin, name='perfil_admin'),
    path("comentarioscrud/",views.comentarios_crud, name="comentarioscrud"),
    path("quejascrud/",views.quejas_crud, name="quejascrud"),
    path("usuarioscrud/",views.usuarios_crud, name="usuarioscrud"),
    path("editar-usuario/<int:usuario_id>/",views.editar_usuario, name="editar_usuario"),
    path("desbloquear-usuario/<int:usuario_id>/",views.desbloquear_usuario, name="desbloquear_usuario"),
    path("citascrud/",views.citas_crud, name="citascrud"),
    path("crear-cita-admin/",views.crear_cita_admin, name="crear_cita_admin"),
    path("analisis-reservas-empresas/",views.analisis_reservas_empresas, name="analisis_reservas_empresas"),
    
    # URL para gestión de pagos de empresas
    path('mis-pagos/', views.empresa_mis_pagos, name='empresa_mis_pagos'),
    
    # NUEVAS URLs AJAX para CRUD de citas
    path('ajax/obtener-servicios-empresa/', views.obtener_servicios_empresa, name='obtener_servicios_empresa'),
    path('ajax/obtener-horas-disponibles/', views.obtener_horas_disponibles, name='obtener_horas_disponibles'),
    path('citascrud/cambiar_estado/<int:reserva_id>/', cambiar_estado_reserva, name='cambiar_estado_reserva'),
    path("servicioscrud/",views.servicios_crud, name="servicioscrud"),
    path("crear-servicio/",views.crear_servicio, name="crear_servicio"),
    path("editar-servicio/<int:servicio_id>/",views.editar_servicio, name="editar_servicio"),
    path("eliminar-servicio/<int:servicio_id>/",views.eliminar_servicio, name="eliminar_servicio"),
    path("detalle-servicio/<int:servicio_id>/",views.detalle_servicio, name="detalle_servicio"),
    path("gestionar-asignaciones-servicios/",views.gestionar_asignaciones_servicios, name="gestionar_asignaciones_servicios"),
    path("asignar-servicio-empresa/<int:empresa_id>/",views.asignar_servicio_empresa, name="asignar_servicio_empresa"),
    path("empresascrud/",views.empresas_crud, name="empresascrud"),
    path("editar-empresa/<int:empresa_id>/",views.editar_empresa, name="editar_empresa"),
    
    # URLs para planes y suscripciones
    path('suscribirse/<int:plan_id>/', views.suscribirse_plan, name='suscribirse_plan'),
    path('mi-suscripcion/', views.mi_suscripcion, name='mi_suscripcion'),
    path('cancelar-suscripcion/', views.cancelar_suscripcion, name='cancelar_suscripcion'),
    path('procesar-pago/<str:referencia>/', views.procesar_pago_suscripcion, name='procesar_pago_suscripcion'),
    
    
    # CRUD para suscripciones individuales (solo admin)
    path('planescrud/', views.planes_crud, name='planes_crud'),
    path('crear-plan/', views.crear_plan, name='crear_plan'),
    path('editar-plan/<int:plan_id>/', views.editar_plan, name='editar_plan'),
    path('eliminar-plan/<int:plan_id>/', views.eliminar_plan, name='eliminar_plan'),
    path('toggle-plan-estado/<int:plan_id>/', views.toggle_plan_estado, name='toggle_plan_estado'),
    path('suscripciones-individuales-crud/', views.suscripciones_individuales_crud, name='suscripciones_individuales_crud'),
    path('crear-suscripcion-individual/', views.crear_suscripcion_individual, name='crear_suscripcion_individual'),
    path('editar-suscripcion-individual/<int:suscripcion_id>/', views.editar_suscripcion_individual, name='editar_suscripcion_individual'),
    path('eliminar-suscripcion-individual/<int:suscripcion_id>/', views.eliminar_suscripcion_individual, name='eliminar_suscripcion_individual'),
    path('pausar-suscripcion-individual/<int:suscripcion_id>/', views.pausar_suscripcion_individual, name='pausar_suscripcion_individual'),
    path('historial-pagos-suscripcion/<int:suscripcion_id>/', views.historial_pagos_suscripcion, name='historial_pagos_suscripcion'),
    
    # CRUD para planes empresariales (solo admin)
    path('planes-empresariales-crud/', views.planes_empresariales_crud, name='planes_empresariales_crud'),
    path('crear-plan-empresarial/', views.crear_plan_empresarial, name='crear_plan_empresarial'),
    path('editar-plan-empresarial/<int:plan_id>/', views.editar_plan_empresarial, name='editar_plan_empresarial'),
    path('eliminar-plan-empresarial/<int:plan_id>/', views.eliminar_plan_empresarial, name='eliminar_plan_empresarial'),
    path('detalle-plan-empresarial/<int:plan_id>/', views.detalle_plan_empresarial, name='detalle_plan_empresarial'),
    path('aprobar-solicitud-empresarial/', views.aprobar_solicitud_empresarial, name='aprobar_solicitud_empresarial'),
    path('suscripciones-empresariales-crud/', views.suscripciones_empresariales_crud, name='suscripciones_empresariales_crud'),
    path('detalle-suscripcion-empresarial/<int:suscripcion_id>/', views.detalle_suscripcion_empresarial, name='detalle_suscripcion_empresarial'),
    path('editar-suscripcion-empresarial/<int:suscripcion_id>/', views.editar_suscripcion_empresarial, name='editar_suscripcion_empresarial'),
    
    # empresas
    path('home-empresas/',views.home_empresas, name='home_empresas'),
    path('citas-empresa/',views.citas_empresa, name='citas_empresa'),
    path('detalle-reserva-empresa/<int:reserva_id>/', views.detalle_reserva_empresa, name='detalle_reserva_empresa'),
    path('editar-reserva-empresa/<int:reserva_id>/', views.editar_reserva_empresa, name='editar_reserva_empresa'),
    path('reportes-empresa/',views.reportes_empresa, name='reportes_empresa'),
    path('exportar-reporte-empresa/',views.exportar_reporte_empresa, name='exportar_reporte_empresa'),
    path('perfil-empresa/',views.perfil_empresa, name='perfil_empresa'),
    path('solicitar-servicio-empresa/',views.solicitar_servicio_empresa, name='solicitar_servicio_empresa'),
    path('actualizar-estado-cita/', views.actualizar_estado_cita, name='actualizar_estado_cita'),
    path('generar-qr-reserva/<int:reserva_id>/', views.generar_codigo_qr_reserva, name='generar_codigo_qr_reserva'),
    # Endpoint público para completar reserva (si alguien abre el QR desde el navegador)
    path('completar-reserva/<str:numero_reserva>/', views.completar_reserva, name='completar_reserva'),
    # Endpoint AJAX para que la app cliente envíe el número escaneado y marque la reserva como completada
    path('ajax/completar-reserva/', views.ajax_completar_reserva, name='ajax_completar_reserva'),
    path('logout-empresa/', views.logout_empresa, name='logout_empresa'),
    
    # =================================
    # URLs PARA GESTIÓN DE PAGOS A EMPRESAS
    # =================================
    path('pagos-empresas/', views.gestion_pagos_empresas, name='gestion_pagos_empresas'),
    path('pagos-empresas/dashboard/', views.dashboard_pagos, name='dashboard_pagos'),
    path('pagos-empresas/detalle/<uuid:periodo_id>/', views.detalle_periodo_liquidacion, name='detalle_periodo_liquidacion'),
    path('pagos-empresas/empresa/<int:empresa_id>/', views.detalle_pagos_empresa, name='detalle_pagos_empresa'),
    path('pagos-empresas/exportar-empresa/<int:empresa_id>/', views.exportar_empresa_csv, name='exportar_empresa_csv'),
    path('pagos-empresas/marcar-reservas/<int:empresa_id>/', views.marcar_reservas_empresa, name='marcar_reservas_empresa'),
    path('pagos-empresas/cerrar-periodo/<uuid:periodo_id>/', views.cerrar_periodo_liquidacion, name='cerrar_periodo_liquidacion'),
    path('pagos-empresas/marcar-pagado/<uuid:periodo_id>/', views.marcar_como_pagado, name='marcar_como_pagado'),
    path('pagos-empresas/generar-periodos/', views.generar_periodos_faltantes, name='generar_periodos_faltantes'),
    path('pagos-empresas/exportar-csv/<uuid:periodo_id>/', views.exportar_periodo_csv, name='exportar_periodo_csv'),
    path('pagos-empresas/api/graficos/', views.api_datos_grafico_pagos, name='api_datos_grafico_pagos'),
    
    # Nuevas URLs para marcar pagos individuales y masivos
    path('marcar-reserva-pagada/<int:reserva_id>/', views.marcar_reserva_pagada, name='marcar_reserva_pagada'),
    path('marcar-empresa-pagada/<int:empresa_id>/', views.marcar_empresa_pagada, name='marcar_empresa_pagada'),
    path('marcar-reservas-seleccionadas/', views.marcar_reservas_seleccionadas, name='marcar_reservas_seleccionadas'),
    path('exportar-pagos-excel/', views.exportar_pagos_excel, name='exportar_pagos_excel'),
    
    # =================================
    # URLs PARA GESTIÓN DE COOKIES
    # =================================
    path('cookies/', include([
        path('consent/', CookieConsentView.as_view(), name='cookie_consent'),
        path('status/', cookie_status, name='cookie_status'),
        path('preferences/', UserPreferencesView.as_view(), name='user_preferences'),
        # path('politica/', CookieConsentView.as_view(), name='cookie_policy'), # Ahora es modal
    ])),
]

if settings.DEBUG:
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

