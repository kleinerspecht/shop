# Generated by Django 3.1.3 on 2020-12-07 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_auto_20201207_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
