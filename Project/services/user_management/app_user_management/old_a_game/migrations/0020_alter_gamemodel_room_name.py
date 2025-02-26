# Generated by Django 4.2.16 on 2024-12-11 18:20

from django.db import migrations, models
import shortuuid.main


class Migration(migrations.Migration):

    dependencies = [
        ('a_game', '0019_alter_gamemodel_room_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamemodel',
            name='room_name',
            field=models.CharField(blank=True, default=shortuuid.main.ShortUUID.uuid, max_length=180, unique=True),
        ),
    ]
