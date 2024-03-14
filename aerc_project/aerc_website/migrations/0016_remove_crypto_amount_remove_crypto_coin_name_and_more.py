# Generated by Django 5.0.1 on 2024-03-13 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aerc_website', '0015_propertytype_alter_house_property_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crypto',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='crypto',
            name='coin_name',
        ),
        migrations.AddField(
            model_name='crypto',
            name='share',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='crypto',
            name='ticker_symbol',
            field=models.CharField(db_index=True, default='', max_length=20),
        ),
    ]