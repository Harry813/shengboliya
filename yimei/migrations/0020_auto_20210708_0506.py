# Generated by Django 3.2 on 2021-07-08 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yimei', '0019_auto_20210708_0504'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_profile',
            name='id_card',
            field=models.CharField(blank=True, max_length=18, verbose_name='身份证号码'),
        ),
        migrations.AddField(
            model_name='user_profile',
            name='real_name',
            field=models.CharField(blank=True, max_length=15, verbose_name='真实姓名'),
        ),
    ]