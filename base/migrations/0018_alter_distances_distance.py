# Generated by Django 4.1.1 on 2023-04-04 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_distances_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distances',
            name='distance',
            field=models.IntegerField(default=1.0),
        ),
    ]