# Generated by Django 4.2.16 on 2024-12-13 10:31

from django.db import migrations, models
import shortuuid.main


class Migration(migrations.Migration):

    dependencies = [
        ('a_game', '0035_alter_gamemodel_room_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamemodel',
            name='room_name',
            field=models.CharField(blank=True, default=shortuuid.main.ShortUUID.uuid, max_length=180, unique=True),
        ),
    ]
