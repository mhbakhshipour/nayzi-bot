# Generated by Django 3.0.7 on 2020-07-05 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20200705_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userserviceimage',
            name='image',
            field=models.ImageField(upload_to='user_service_image', verbose_name='image'),
        ),
    ]
