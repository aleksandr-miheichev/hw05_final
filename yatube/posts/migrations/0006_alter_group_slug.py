# Generated by Django 4.0.6 on 2022-07-12 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_alter_group_options_alter_post_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Короткая метка сообщества'),
        ),
    ]
