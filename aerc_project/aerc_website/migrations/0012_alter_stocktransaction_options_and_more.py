# Generated by Django 5.0.1 on 2024-03-07 19:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aerc_website', '0011_rename_ticker_symbol_stocktransaction_stock'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stocktransaction',
            options={'ordering': ['purchase_date'], 'verbose_name': 'Stock Transaction', 'verbose_name_plural': 'Stock Transactions'},
        ),
        migrations.RemoveField(
            model_name='stocktransaction',
            name='transaction_date',
        ),
    ]
