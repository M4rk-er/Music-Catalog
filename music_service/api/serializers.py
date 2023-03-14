from rest_framework import serializers

from music.models import (Album, AlbumTrack, FavoriteAlbum, FavoritePlaylist,
                          FavoriteTrack, Performer, Playlist, PlaylistTrack,
                          Track)
from users.models import User


class PlaylistInSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Playlist.objects.all(),
                                            required=True)
    title = serializers.ReadOnlyField()
    track_number = serializers.SerializerMethodField(
        method_name='get_track_number'
    )

    class Meta:
        model = Playlist
        fields = ('id', 'title', 'track_number',)

    def get_track_number(self, playlist):
        track = self.context['track']
        playlist_track = PlaylistTrack.objects.get(playlist=playlist,
                                                   track=track)
        return playlist_track.track_number


class PerformerInSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Performer.objects.all(),
                                            required=True)
    name = serializers.ReadOnlyField()

    class Meta:
        model = Performer
        fields = ('id', 'name',)


class CreatePlaylistTrackSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all(),
                                            required=True,
                                            source='track')
    title = serializers.ReadOnlyField(source='track.title')
    author = PerformerInSerializer(source='track.author', read_only=True)
    track_number = serializers.ReadOnlyField()

    class Meta:
        model = PlaylistTrack
        fields = ('id', 'title', 'author', 'track_number',)


class TrackInSerializer(serializers.ModelSerializer):
    track_number = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = ('id', 'title', 'track_number',)

    def get_track_number(self, track):
        playlist = self.context.get('playlist')
        playlist_track = PlaylistTrack.objects.get(track=track,
                                                   playlist=playlist)
        return playlist_track.track_number


class AlbumInSerializer(serializers.ModelSerializer):
    title = serializers.CharField()

    class Meta:
        model = Album
        fields = ('id', 'title',)


class TracksListInSerializer(serializers.ModelSerializer):
    album = serializers.SerializerMethodField(method_name='get_album')

    class Meta:
        model = Track
        fields = ('id', 'title', 'album',)

    def get_album(self, track):
        if track.album.first():
            return AlbumInSerializer(track.album.first()).data
        return 'Single'


class PlaylistSerializer(serializers.ModelSerializer):
    tracks = CreatePlaylistTrackSerializer(many=True,
                                           required=True,
                                           source='playlisttrack_set')
    description = serializers.CharField(max_length=512, required=False)
    is_favorite = serializers.SerializerMethodField(
        method_name='get_is_favorite',
        read_only=True
    )

    class Meta:
        model = Playlist
        fields = ('id',
                  'title',
                  'date_of_create',
                  'description',
                  'tracks',
                  'is_favorite')

    def create(self, validated_data):
        tracks_data = validated_data.pop('playlisttrack_set')
        playlist = Playlist.objects.create(**validated_data)

        for track in tracks_data:
            playlist_track = PlaylistTrack(
                playlist=playlist,
                track=track.get('track')
            )
            playlist_track.save()

        return playlist

    def get_is_favorite(self, playlist):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            FavoritePlaylist.objects.filter(user=user,
                                            playlist=playlist).exists()
        )


class TrackInAlbumSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all(),
                                            required=True,
                                            source='track')
    title = serializers.ReadOnlyField(source='track.title')

    class Meta:
        model = Track
        fields = ('id', 'title',)


class AlbumSerializer(serializers.ModelSerializer):
    author = PerformerInSerializer(required=True)
    tracks = TrackInAlbumSerializer(many=True,
                                    required=True,
                                    source='albumtrack_set')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )

    class Meta:
        model = Album
        fields = ('id',
                  'title',
                  'release_date',
                  'author',
                  'tracks',
                  'is_favorited',)

    def create(self, validated_data):
        user = self.context['request'].user
        author_created_by = validated_data.get('author').get('id').created_by
        if user != author_created_by:
            raise serializers.ValidationError(
                {'error': 'Нельзя создавать альбом не своего исполнителя'}
            )

        title = validated_data.get('title')
        err_msg = 'У этого исполнителя уже существует альбом с таким названием'
        if Album.objects.filter(title=title).exists():
            raise serializers.ValidationError(
                {'error': err_msg}
            )

        tracks_data = validated_data.pop('albumtrack_set')
        author = validated_data.pop('author')
        album = Album.objects.create(
            **validated_data,
            author=author.get('id')
        )

        for track in tracks_data:
            track_author = track.get('track').author
            if track_author != album.author:
                raise serializers.ValidationError(
                    {'error': 'Нельзя добавлять в альбом треки другого автора'}
                )
            AlbumTrack.objects.create(
                album=album,
                track=track.get('track')
            )

        return album

    def get_is_favorited(self, album):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            FavoriteAlbum.objects.filter(user=user, album=album).exists()
        )


class PerformerSerializer(serializers.ModelSerializer):
    tracks = serializers.SerializerMethodField(method_name='get_tracks',
                                               read_only=True,
                                               required=False)
    albums = serializers.SerializerMethodField(method_name='get_albums',
                                               read_only=True,
                                               required=False)

    class Meta:
        model = Performer
        fields = ('id', 'name', 'tracks', 'albums')

    def get_tracks(self, author):
        return TracksListInSerializer(author.tracks.all(), many=True).data

    def get_albums(self, author):
        return AlbumInSerializer(author.album_set.all(), many=True).data


class TrackSerializer(serializers.ModelSerializer):
    author = PerformerInSerializer(required=True)
    playlists = serializers.SerializerMethodField(method_name='get_playlists',
                                                  read_only=True)
    albums = serializers.SerializerMethodField(method_name='get_albums',
                                               read_only=True)
    is_favorite = serializers.SerializerMethodField(
        method_name='get_is_favorite'
    )

    class Meta:
        model = Track
        fields = ('id',
                  'title',
                  'author',
                  'playlists',
                  'albums',
                  'is_favorite',)
        extra_kwargs = {'title': {'required': True}}

    def create(self, validated_data):
        user = self.context['request'].user
        if user != validated_data.get('author').get('id').created_by:
            raise serializers.ValidationError(
                {'error': 'Нельзя создавать треки не своего исполнителя.'}
            )

        is_playlist = validated_data.get('playlists')
        playlist_data = validated_data.pop('playlists') if is_playlist else []
        track = Track.objects.create(
            title=validated_data.get('title'),
            author=validated_data.get('author').get('id')
        )
        if is_playlist:
            for playlist in playlist_data:
                playlist_obj = Playlist.objects.get(id=playlist['id'].id)
                PlaylistTrack.objects.create(
                    playlist=playlist_obj,
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

    def get_playlists(self, track):
        playlists = Playlist.objects.filter(playlisttrack__track=track)
        return PlaylistInSerializer(playlists,
                                    context={'track': track},
                                    many=True).data

    def get_albums(self, track):
        album = Album.objects.filter(albumtrack__track=track)
        return AlbumInSerializer(album,
                                 context={'track': track},
                                 many=True).data

    def get_is_favorite(self, track):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            FavoriteTrack.objects.filter(user=user, track=track).exists()
        )


class AddTrackListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='playlist.id')
    title = serializers.ReadOnlyField(source='playlist.title')
    tracks = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all(),
                                                many=True,
                                                required=True)

    class Meta:
        model = Playlist
        fields = ('id', 'title', 'tracks',)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)

    def validate(self, value):
        if value['new_password'] == value['current_password']:
            raise serializers.ValidationError(
                {'status': 'Поля не должны совпадать'})
        return value


class PlaylistFavoriteSerializer(serializers.ModelSerializer):
    amount_tracks = serializers.SerializerMethodField(
        method_name='get_amount_tracks'
    )

    class Meta:
        model = Playlist
        fields = ('id', 'title', 'date_of_create', 'amount_tracks',)

    def get_amount_tracks(self, playlist):
        return playlist.tracks.all().count()


class TrackFavoriteSerializer(serializers.ModelSerializer):
    album = serializers.SerializerMethodField(method_name='get_album')
    author = PerformerInSerializer()

    class Meta:
        model = Track
        fields = ('id', 'title', 'author', 'album',)

    def get_album(self, track):
        if track.album.first():
            return AlbumInSerializer(track.album.first()).data
        return 'Single'


class AlbumFavoriteSerializer(serializers.ModelSerializer):
    author = PerformerInSerializer()
    amount_tracks = serializers.SerializerMethodField(
        method_name='get_amount_tracks'
    )

    class Meta:
        model = Album
        fields = ('id', 'title', 'author', 'release_date', 'amount_tracks',)

    def get_amount_tracks(self, album):
        return album.tracks.all().count()
