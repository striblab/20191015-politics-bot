# Generated by Django 2.2.6 on 2019-10-15 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0002_auto_20191015_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newcandidate',
            name='district',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
