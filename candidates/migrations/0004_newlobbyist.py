# Generated by Django 2.2.6 on 2019-10-16 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0003_auto_20191015_2004'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewLobbyist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lobbyist_full_name', models.CharField(max_length=255)),
                ('lobbyist_id', models.CharField(max_length=10)),
                ('association_full_name', models.CharField(max_length=255)),
                ('association_entity_id', models.CharField(max_length=10)),
                ('registration_date', models.DateField()),
                ('termination_date', models.DateField(null=True)),
                ('bool_alert_sent', models.BooleanField(default=False)),
                ('ingestion_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
