# Generated by Django 4.1.1 on 2023-04-26 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_contract_instrument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demo',
            name='title',
            field=models.CharField(db_column='name', max_length=100),
        ),
    ]