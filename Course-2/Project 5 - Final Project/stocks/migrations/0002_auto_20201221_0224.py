# Generated by Django 3.1.4 on 2020-12-20 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acquisition',
            name='qty',
            field=models.IntegerField(),
        ),
    ]