# Generated by Django 4.2.16 on 2024-12-15 23:46

from django.db import migrations, models
import shortuuid.main


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0006_alter_tournamentmodels_tournament_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentmodels',
            name='tournament_name',
            field=models.CharField(blank=True, default=shortuuid.main.ShortUUID.uuid, max_length=128, unique=True),
        ),
    ]
