# Generated by Django 4.1.7 on 2023-02-27 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_rename_album_title_album_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='album',
            field=models.ManyToManyField(related_name='tracks', through='api.AlbumTrack', to='api.album'),
        ),
    ]
