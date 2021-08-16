# Generated by Django 3.2 on 2021-06-30 01:45

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yimei', '0004_operator_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='Operator_Rebate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vip_lv', models.PositiveSmallIntegerField(choices=[(0, '普通用户'), (1, 'VIP I'), (2, 'VIP II')], default=0, verbose_name='VIP等级')),
                ('rebate_int', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], verbose_name='返佣比例')),
                ('op', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yimei.operator', verbose_name='OP')),
            ],
        ),
    ]
