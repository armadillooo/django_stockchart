# Generated by Django 2.2.6 on 2019-12-01 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0004_auto_20191201_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='code',
            field=models.IntegerField(),
        ),
    ]