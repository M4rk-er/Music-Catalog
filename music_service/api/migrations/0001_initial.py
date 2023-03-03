# Generated by Django 4.1.7 on 2023-02-25 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album_title', models.CharField(max_length=128)),
                ('year_of_release', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='AlbumTrack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.album')),
            ],
        ),
        migrations.CreateModel(
            name='Performer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_title', models.CharField(max_length=128)),
                ('album', models.ManyToManyField(through='api.AlbumTrack', to='api.album')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='api.performer')),
            ],
        ),
        migrations.AddField(
            model_name='albumtrack',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.track'),
        ),
        migrations.AddField(
            model_name='album',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='albums', to='api.performer'),
        ),
        migrations.AddConstraint(
            model_name='albumtrack',
            constraint=models.UniqueConstraint(fields=('album', 'track'), name='unique_album_title'),
        ),
    ]