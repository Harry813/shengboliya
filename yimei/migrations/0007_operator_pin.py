# Generated by Django 3.2 on 2021-06-30 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yimei', '0006_auto_20210630_0412'),
    ]

    operations = [
        migrations.AddField(
            model_name='operator',
            name='pin',
            field=models.BooleanField(default=False, verbose_name='推荐'),
        ),
    ]