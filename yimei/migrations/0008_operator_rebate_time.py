# Generated by Django 3.2 on 2021-06-30 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yimei', '0007_operator_pin'),
    ]

    operations = [
        migrations.AddField(
            model_name='operator',
            name='rebate_time',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='返佣时间'),
        ),
    ]
