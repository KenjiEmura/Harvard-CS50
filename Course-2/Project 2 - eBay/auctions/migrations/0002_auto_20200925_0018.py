# Generated by Django 3.1 on 2020-09-24 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auction',
            old_name='initial_price',
            new_name='price',
        ),
    ]