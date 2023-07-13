# Generated by Django 4.2.2 on 2023-07-07 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicproapp', '0002_producto_descripcion_alter_tipoproducto_nombre'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entrega',
            fields=[
                ('codigo_entrega', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Nombre del Producto')),
                ('confirmacion', models.BooleanField()),
            ],
        ),
    ]
