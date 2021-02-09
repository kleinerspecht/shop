# Generated by Django 3.1.3 on 2021-02-09 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0022_auto_20210202_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_status',
            field=models.CharField(blank=True, choices=[('Order processed', 'Order processed!'), ('Order processed', 'Order shipped!'), ('Order en route', 'Order en route'), ('Order arrived', 'Order arrived!')], max_length=70, null=True),
        ),
    ]
