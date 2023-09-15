# Generated by Django 4.2.4 on 2023-09-04 23:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('myuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(max_length=255)),
                ('second_name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('user.myuser',),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]