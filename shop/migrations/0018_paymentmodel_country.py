# Generated by Django 3.1.3 on 2021-01-24 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0017_remove_paymentmodel_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmodel',
            name='country',
            field=models.CharField(default='Bulgaria', max_length=200),
            preserve_default=False,
        ),
    ]
