# Generated by Django 3.2.5 on 2021-09-06 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0002_alter_station_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='photo',
            field=models.ImageField(null=True, upload_to='../main/static/img/'),
        ),
    ]
