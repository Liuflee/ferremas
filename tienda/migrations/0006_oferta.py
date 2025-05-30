# Generated by Django 5.0.6 on 2025-05-21 17:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0005_remove_producto_precio_pedido_itempedido_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Oferta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('precio_oferta', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_inicio', models.DateTimeField()),
                ('fecha_fin', models.DateTimeField()),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ofertas', to='tienda.producto')),
            ],
        ),
    ]
