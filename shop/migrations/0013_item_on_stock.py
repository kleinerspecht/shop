# Generated by Django 3.1.3 on 2020-12-28 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_auto_20201218_2050'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='on_stock',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
