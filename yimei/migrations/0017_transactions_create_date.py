# Generated by Django 3.2 on 2021-07-05 14:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('yimei', '0016_auto_20210704_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='创建时间'),
            preserve_default=False,
        ),
    ]