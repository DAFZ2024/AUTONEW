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
from django.urls import path
from lavado_auto import views
from lavado_auto.views import get_horas,cambiar_estado_reserva

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name = 'home'),
    path('nosotros/',views.nosotros, name = 'nosotros'),
    path('servicios/',views.servicios, name = 'servicios'),
    path('planes/',views.planes, name = 'planes'),
    path('reservas/',views.reservas, name = 'reservas'),
    path('obtener-servicios/', views.obtener_servicios, name='obtener_servicios'),
    path('obtener-info-empresa/', views.obtener_info_empresa, name='obtener_info_empresa'),
    path('obtener-info-servicio/', views.obtener_info_servicio, name='obtener_info_servicio'),
    path('get-horas/', views.get_horas, name='get_horas'),
    path('obtener-horas/', views.get_horas, name='obtener_horas'),
    path('contacto/',views.contacto, name = 'contacto'),
    path('resetcorreo/',views.resetCorreo, name = 'resetCorreo'),
    path('resetcontrasena/',views.resetContrasena, name = 'resetContrasena'),
    path('login/',views.login, name = 'login'),
    path('logout/', views.logout, name='logout'),
    path('comentarios/', views.comentarios, name='comentarios'),
    path('citas/', views.citas, name='citas'),
    path('api/hours/', get_horas, name='get_horas'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('empresas/', views.empresas, name='empresas'),

    # crud
    path('logincrud/',views.login_crud, name='logincrud'),
    path('logout/', views.logout_view, name='logout_view'),
    path('homecrud/',views.home_crud, name='homecrud'),
    path("comentarioscrud/",views.comentarios_crud, name="comentarioscrud"),
    path("quejascrud/",views.quejas_crud, name="quejascrud"),
    path("usuarioscrud/",views.usuarios_crud, name="usuarioscrud"),
    path("citascrud/",views.citas_crud, name="citascrud"),
    path("citascomcrud/",views.citascom_crud, name="citascomcrud"),
    path('citascrud/cambiar_estado/<int:reserva_id>/', cambiar_estado_reserva, name='cambiar_estado_reserva'),
    path("servicioscrud/",views.servicios_crud, name="servicioscrud"),
    path("empresascrud/",views.empresas_crud, name="empresascrud"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

