from rest_framework import serializers

from music.models import Playlist, PlaylistTrack, Performer, Track
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


class TracksListInSerializer(serializers.ModelSerializer):
    playlists = serializers.SerializerMethodField(method_name='get_playlists')

    class Meta:
        model = Track
        fields = ('id', 'title', 'playlists',)

    def get_playlists(self, track):
        return PlaylistInSerializer(track.playlist.all(),
                                    context={'track': track},
                                    many=True).data


class PlaylistSerializer(serializers.ModelSerializer):
    tracks = CreatePlaylistTrackSerializer(many=True,
                                           required=True,
                                           source='playlisttrack_set')

    class Meta:
        model = Playlist
        fields = ('id', 'title', 'date_of_create', 'tracks',)

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

    def get_tracks(self, playlist):
        return TrackInSerializer(playlist.tracks.all(),
                                 context={'playlist': playlist},
                                 many=True).data


class PerformerSerializer(serializers.ModelSerializer):
    tracks = serializers.SerializerMethodField(method_name='get_tracks',
                                               read_only=True,
                                               required=False)

    class Meta:
        model = Performer
        fields = ('id', 'name', 'tracks',)

    def get_tracks(self, author):
        return TracksListInSerializer(author.tracks.all(), many=True).data


class TrackSerializer(serializers.ModelSerializer):
    author = PerformerInSerializer(required=True)
    playlists = serializers.SerializerMethodField(method_name='get_playlists',
                                                  read_only=True)

    class Meta:
        model = Track
        fields = ('id', 'title', 'author', 'playlists')
        extra_kwargs = {'title': {'required': True}}

    def create(self, validated_data):
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

    def get_playlists(self, obj):
        playlists = Playlist.objects.filter(playlisttrack__track=obj)
        serializer = PlaylistInSerializer(playlists,
                                          context={'track': obj},
                                          many=True)
        return serializer.data


class PlaylistTrackListSerializer(serializers.ModelSerializer):
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
