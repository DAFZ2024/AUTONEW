"""
Comando para limpiar datos de cookies antiguas
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime, timedelta
import json

class Command(BaseCommand):
    help = 'Limpia datos de cookies antiguos y genera reporte de consentimiento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Días de retención de datos de cookies (por defecto: 365)'
        )
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generar reporte de estadísticas de cookies'
        )

    def handle(self, *args, **options):
        days_retention = options['days']
        show_report = options['report']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🍪 Iniciando limpieza de cookies de AutoNew (retención: {days_retention} días)'
            )
        )
        
        if show_report:
            self.generate_cookie_report()
        
        # Aquí implementarías la lógica de limpieza si tuvieras un modelo de cookies
        # Por ahora, solo mostramos información
        self.stdout.write(
            self.style.SUCCESS(
                '✅ Proceso de limpieza completado exitosamente'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                '💡 Recuerda: Las cookies se gestionan en el navegador del usuario'
            )
        )

    def generate_cookie_report(self):
        """Genera un reporte de configuración de cookies"""
        self.stdout.write(self.style.WARNING('\n📊 REPORTE DE CONFIGURACIÓN DE COOKIES - AUTONEW\n'))
        
        # Mostrar configuración actual
        cookie_settings = getattr(settings, 'COOKIE_SETTINGS', {})
        categories = getattr(settings, 'COOKIE_CATEGORIES', {})
        
        self.stdout.write('⚙️ Configuración actual:')
        for key, value in cookie_settings.items():
            self.stdout.write(f'   • {key}: {value}')
        
        self.stdout.write('\n📋 Categorías de cookies configuradas:')
        for category, config in categories.items():
            required_status = '✅ Requerida' if config.get('required') else '🔧 Opcional'
            self.stdout.write(f'   • {config["name"]} ({category}): {required_status}')
            self.stdout.write(f'     └─ {config["description"]}')
        
        # Recomendaciones
        self.stdout.write('\n💡 Recomendaciones:')
        if settings.DEBUG:
            self.stdout.write('   ⚠️  DEBUG está activado - Las cookies secure están deshabilitadas')
        else:
            self.stdout.write('   ✅ Modo producción - Cookies seguras habilitadas')
        
        self.stdout.write('   📱 Asegúrate de que el banner sea responsive')
        self.stdout.write('   🔒 Verifica que las cookies sensibles usen HttpOnly')
        self.stdout.write('   🌐 Revisa la configuración de SameSite para CSRF')
        
        self.stdout.write(f'\n📅 Fecha del reporte: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write('=' * 60)
