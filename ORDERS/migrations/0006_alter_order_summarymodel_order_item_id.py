# Generated by Django 5.1.7 on 2025-04-08 09:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ORDERS', '0005_order_summarymodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_summarymodel',
            name='order_item_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ORDERS.orderitemmodel'),
        ),
    ]
