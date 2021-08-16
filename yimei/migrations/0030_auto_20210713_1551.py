# Generated by Django 3.2 on 2021-07-13 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yimei', '0029_auto_20210713_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_profile',
            name='available',
        ),
        migrations.AddField(
            model_name='user_profile',
            name='frozen',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='冻结'),
        ),
    ]
