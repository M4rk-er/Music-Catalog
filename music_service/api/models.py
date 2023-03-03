from django.db import models


class Performer(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=128)
    year_of_release = models.DateField()

    def __str__(self):
        return self.title


class Track(models.Model):
    title = models.CharField(max_length=128)
    author = models.ForeignKey(
        Performer,
        on_delete=models.CASCADE,
        related_name='tracks'
    )
    album = models.ManyToManyField(
        Album,
        through='AlbumTrack',
        related_name='tracks',
    )

    def __str__(self):
        return self.title


class AlbumTrack(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    track_number = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['album', 'track'],
                name='unique_album_title',
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.pk:
            last_album_track = AlbumTrack.objects.filter(
                album=self.album
            ).last()
            track_number = (
                last_album_track.track_number + 1 if last_album_track else 1
            )
            self.track_number = track_number
        super().save(*args, **kwargs)
