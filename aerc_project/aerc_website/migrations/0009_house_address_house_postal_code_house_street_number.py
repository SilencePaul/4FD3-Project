# Generated by Django 5.0.1 on 2024-03-06 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aerc_website', '0008_alter_asset_current_value_alter_stock_purchase_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='address',
            field=models.CharField(default='', max_length=80),
        ),
        migrations.AddField(
            model_name='house',
            name='postal_code',
            field=models.CharField(default='XXX XXX', max_length=10),
        ),
        migrations.AddField(
            model_name='house',
            name='street_number',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]
