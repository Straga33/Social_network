# Generated by Django 2.2.16 on 2022-04-05 05:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20220404_1108'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('create',)},
        ),
    ]