# Generated by Django 3.0.7 on 2020-10-01 16:27

from django.db import migrations


def count_total_price(apps, schema_editor):
    OrderProduct = apps.get_model("foodcartapp", "OrderProduct")
    for item in OrderProduct.objects.all():
        if not item.total_price:
            item.total_price = item.product.price * item.quantity
            item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0035_orderproduct_total_price'),
    ]

    operations = [
        migrations.RunPython(count_total_price),
    ]
