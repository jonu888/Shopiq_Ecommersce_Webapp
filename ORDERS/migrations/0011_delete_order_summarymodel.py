# Generated by Django 5.1.7 on 2025-04-09 09:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ORDERS', '0010_alter_order_summarymodel_order_item_id'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Order_Summarymodel',
        ),
    ]
