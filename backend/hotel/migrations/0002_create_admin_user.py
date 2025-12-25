from django.contrib.auth import get_user_model
from django.db import migrations


def create_default_admin(apps, schema_editor):
    User = get_user_model()
    username = 'admin'
    password = 'admin123'
    email = 'admin@example.com'
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)


def remove_default_admin(apps, schema_editor):
    User = get_user_model()
    User.objects.filter(username='admin').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('hotel', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_admin, remove_default_admin),
    ]
