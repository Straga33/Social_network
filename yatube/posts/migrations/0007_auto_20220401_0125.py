# Generated by Django 2.2.16 on 2022-03-31 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20220331_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузите картинку', null=True, upload_to='media/posts/', verbose_name='Картинка'),
        ),
    ]
