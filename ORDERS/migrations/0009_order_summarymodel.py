# Generated by Django 5.1.7 on 2025-04-08 09:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ORDERS', '0008_delete_order_summarymodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order_Summarymodel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=100)),
                ('payment_status', models.BooleanField(default=False)),
                ('payment_id', models.CharField(blank=True, max_length=100, null=True)),
                ('total_amount', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('order_item_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ORDERS.orderitemmodel')),
            ],
        ),
    ]
