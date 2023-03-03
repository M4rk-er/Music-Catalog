from rest_framework import serializers

from .models import Album, AlbumTrack, Performer, Track


class AlbumInSerializer(serializers.ModelSerializer):
    """
    Вложеный сериализатор для получение Album с полями id и name
    в сериализаторе получения трека.
    """
    track_number = serializers.SerializerMethodField(method_name='get_track_number')
    id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = Album
        fields = ('id', 'title', 'track_number',)

    def get_track_number(self, album):
        track = self.context.get('track')
        album_track = AlbumTrack.objects.get(album=album, track=track)
        return album_track.track_number


class AlbumInSerialzer(serializers.ModelSerializer):
    """
    Сериализатор для получния Album с полями
    id и title в сериализаторе создания трека.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all(),
                                            required=True)
    title = serializers.ReadOnlyField()

    class Meta:
        model = Album
        fields = ('id', 'title',)


class AlbumTrackListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления треков в альбом с полями
    id, title, tracks.
    """
    id = serializers.ReadOnlyField(source='album.id')
    title = serializers.ReadOnlyField(source='album.title')
    tracks = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all(),
                                                many=True,
                                                required=True)

    class Meta:
        model = Album
        fields = ('id', 'title', 'tracks',)


class CreateAlbumTrackSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания связи AlbumTrack
    в сериализаторе для создания Альбома.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all(),
                                            required=True,
                                            source='track')
    title = serializers.ReadOnlyField(source='track.title')

    class Meta:
        model = AlbumTrack
        fields = ('id', 'title',)


class PerformerForGetSerializer(serializers.ModelSerializer):
    """
    Вложенный сериализатор для получения Performer с полями
    id и name в сериализаторе получения Трека.
    """

    class Meta:
        model = Performer
        fields = ('id', 'name',)


class PerformerForCreateSerializer(serializers.ModelSerializer):
    """
    Вложенный сериализатор для получения Performer с полями
    id и name в сериализаторе создания Трека.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Performer.objects.all(),
                                            required=True)
    name = serializers.ReadOnlyField()

    class Meta:
        model = Performer
        fields = ('id', 'name',)


class TrackInSerializer(serializers.ModelSerializer):
    """
    Вложенный сериализатор для получения Track
    с полями id, title, track_number
    в сериализаторе получения альбома.
    """
    track_number = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = ('id', 'title', 'track_number',)

    def get_track_number(self, obj):
        album = self.context.get('album')
        album_track = AlbumTrack.objects.get(track=obj, album=album)
        return album_track.track_number


class TracksListInSerializer(serializers.ModelSerializer):
    """
    Вложенный сериализатор для получения Track с полями id, title, albums
    в сериализаторе получения исполнителя.
    """
    albums = serializers.SerializerMethodField(method_name='get_albums')

    class Meta:
        model = Track
        fields = ('id', 'title', 'albums',)

    def get_albums(self, track):
        return AlbumInSerializer(track.album.all(),
                                 context={'track': track},
                                 many=True).data


class CreateAlbumSerializer(serializers.ModelSerializer):
    """Создание Album."""
    tracks = CreateAlbumTrackSerializer(many=True,
                                        required=True,
                                        source='albumtrack_set')

    class Meta:
        model = Album
        fields = ('id', 'title', 'year_of_release', 'tracks',)

    def create(self, validated_data):
        tracks_data = validated_data.pop('albumtrack_set')

        album = Album.objects.create(**validated_data)

        for track in tracks_data:
            album_track = AlbumTrack(
                album=album,
                track=track.get('track')
            )
            album_track.save()

        return album


class GetAlbumSerializer(serializers.ModelSerializer):
    """Получение Album."""
    tracks = serializers.SerializerMethodField(method_name='get_tracks')

    class Meta:
        model = Album
        fields = ('id', 'title',  'year_of_release', 'tracks',)

    def get_tracks(self, album):
        return TrackInSerializer(album.tracks.all(),
                                 context={'album': album},
                                 many=True).data


class CreatePerformerSerializer(serializers.ModelSerializer):
    """Создание Track"""
    class Meta:
        model = Performer
        fields = ('id', 'name',)


class GetPerformerSerializer(serializers.ModelSerializer):
    """Получение Performer."""
    tracks = serializers.SerializerMethodField(method_name='get_tracks')

    class Meta:
        model = Performer
        fields = ('id', 'name', 'tracks',)

    def get_tracks(self, author):
        return TracksListInSerializer(author.tracks.all(),
                                      many=True).data


class CreateTrackSerializer(serializers.ModelSerializer):
    """Создание Track"""
    author = PerformerForCreateSerializer(required=True)
    album = AlbumInSerialzer(many=True, required=False)

    class Meta:
        model = Track
        fields = ('id', 'title', 'author', 'album',)

    def create(self, validated_data):
        is_album = validated_data.get('album')
        album_data = validated_data.pop('album') if is_album else []
        track = Track.objects.create(
            title=validated_data.get('title'),
            author=validated_data.get('author').get('id')
        )
        if is_album:
            for album in album_data:
                album_obj = Album.objects.get(id=album['id'].id)
                AlbumTrack.objects.create(
                    album=album_obj,
                    track=track
                )
        return track

    def validate(self, data):
        is_track = Track.objects.filter(
            title=data['title'],
            author=data.get('author').get('id')
        ).exists()
        if is_track:
            raise serializers.ValidationError(
                'Трек с таким названием уже есть у этого исполнителя'
            )
        return data


class GetTrackSerializer(serializers.ModelSerializer):
    """Получение Track."""
    author = PerformerForGetSerializer(read_only=True)
    albums = serializers.SerializerMethodField(method_name='get_albums')

    class Meta:
        model = Track
        fields = ('id', 'title', 'author', 'albums',)

    def get_albums(self, track):
        albums = Album.objects.filter(albumtrack__track=track)
        serializer = AlbumInSerializer(albums,
                                       context={'track': track},
                                       many=True)
        return serializer.data
