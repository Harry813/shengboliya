# Generated by Django 3.2 on 2021-07-03 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yimei', '0012_auto_20210702_2309'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='show',
            field=models.BooleanField(default=True, verbose_name='显示'),
        ),
    ]