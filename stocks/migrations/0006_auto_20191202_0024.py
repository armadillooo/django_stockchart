# Generated by Django 2.2.6 on 2019-12-01 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0005_auto_20191201_2227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.Company'),
        ),
    ]
