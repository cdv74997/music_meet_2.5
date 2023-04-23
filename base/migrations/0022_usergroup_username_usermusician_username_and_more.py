# Generated by Django 4.1.1 on 2023-04-23 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_usergroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='username',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='usermusician',
            name='username',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
