# Generated by Django 3.1.3 on 2020-11-28 21:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0005_auto_20201129_0359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='follow',
            field=models.ManyToManyField(blank=True, related_name='_user_follow_+', to=settings.AUTH_USER_MODEL),
        ),
    ]