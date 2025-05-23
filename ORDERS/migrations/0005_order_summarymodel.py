# Generated by Django 5.1.7 on 2025-04-08 09:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ORDERS', '0004_alter_orderitemmodel_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order_Summarymodel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=100)),
                ('payment_status', models.BooleanField(default=False)),
                ('order_item_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ORDERS.orderitemmodel')),
            ],
        ),
    ]
