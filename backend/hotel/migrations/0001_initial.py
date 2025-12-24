from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=30)),
            ],
            options={'ordering': ['full_name']},
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10, unique=True)),
                ('room_type', models.CharField(max_length=50)),
                ('capacity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    'status',
                    models.CharField(
                        choices=[('available', 'Available'), ('occupied', 'Occupied'), ('maintenance', 'Maintenance')],
                        default='available',
                        max_length=20,
                    ),
                ),
                ('description', models.TextField(blank=True)),
            ],
            options={'ordering': ['number']},
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'status',
                    models.CharField(
                        choices=[('reserved', 'Reserved'), ('checked_in', 'Checked In'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
                        default='reserved',
                        max_length=20,
                    ),
                ),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'guest',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='hotel.guest'
                    ),
                ),
                (
                    'room',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='hotel.room'
                    ),
                ),
            ],
            options={'ordering': ['-check_in', '-created_at']},
        ),
    ]
