# Generated by Django 4.1.7 on 2023-03-08 10:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_remove_album_in_favorites'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='music.performer'),
            preserve_default=False,
        ),
    ]