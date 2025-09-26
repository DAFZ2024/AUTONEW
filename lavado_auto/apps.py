from django.apps import AppConfig




class LavadoAutoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lavado_auto'

    def ready(self):
        from django.db.models.signals import post_migrate
        from django.contrib.auth import get_user_model
        def create_admin_user(sender, **kwargs):
            User = get_user_model()
            if not User.objects.filter(nombre_usuario='admin').exists():
                User.objects.create_superuser(
                    nombre_usuario='admin',
                    correo='admin@admin.com',
                    password='admin123',
                    rol='admin'  # Valor correcto para el campo rol
                )
        post_migrate.connect(create_admin_user, sender=self)

