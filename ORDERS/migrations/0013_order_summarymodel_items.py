# Generated by Django 5.1.7 on 2025-04-09 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ORDERS', '0012_order_summarymodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_summarymodel',
            name='items',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
