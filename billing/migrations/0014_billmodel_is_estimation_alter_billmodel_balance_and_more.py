# Generated by Django 5.2 on 2025-04-19 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0013_alter_billproductmodel_product_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='billmodel',
            name='is_estimation',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='billmodel',
            name='balance',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='billmodel',
            name='bill_discount_amount',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='billmodel',
            name='bill_discount_percentage',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='billmodel',
            name='total_discount_amount',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='billmodel',
            name='total_paid',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='billmodel',
            name='total_tax_amount',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
