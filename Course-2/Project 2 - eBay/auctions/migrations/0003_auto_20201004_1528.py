# Generated by Django 3.1 on 2020-10-04 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auction_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcategory',
            name='parent_category',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_categories', to='auctions.productcategory'),
        ),
    ]