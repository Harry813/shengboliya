# Generated by Django 3.2 on 2021-06-30 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yimei', '0008_operator_rebate_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='operator',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='医院简介'),
        ),
    ]
