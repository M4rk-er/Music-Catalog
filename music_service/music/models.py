from django.db import models


class Performer(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Playlist(models.Model):
    title = models.CharField(max_length=128)
    date_of_create = models.DateField(
        auto_now_add=True
    )
    description = models.CharField(
        max_length=512,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title


class Album(models.Model):
    title = models.CharField(
        max_length=128
    )
    release_date = models.DateField()
    in_favorites = models.BooleanField(
        default=False,
        blank=True
    )

    def __str__(self):
        return self.title


class Track(models.Model):
    title = models.CharField(max_length=128)
    author = models.ForeignKey(
        Performer,
        on_delete=models.CASCADE,
        related_name='tracks'
    )
    playlist = models.ManyToManyField(
        Playlist,
        through='PlaylistTrack',
        related_name='tracks',
    )
    album = models.ManyToManyField(
        Album,
        through='AlbumTrack',
        related_name='tracks'
    )

    def __str__(self):
        return self.title


class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE
    )
    track_number = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['playlist', 'track'],
                name='unique_playlist_title',
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.pk:
            last_playlist_track = PlaylistTrack.objects.filter(
                playlist=self.playlist
            ).last()
            track_number = (
                last_playlist_track.track_number + 1 if last_playlist_track else 1
            )
            self.track_number = track_number
        super().save(*args, **kwargs)


class AlbumTrack(models.Model):
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['album', 'track'],
                name='unique_album_title',
            ),
        ]
