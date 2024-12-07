
from django.apps import AppConfig

class StudentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'students'
    verbose_name = "จัดการข้อมูล"

    def ready(self):
        import students.signals  # Import the signals to connect them
