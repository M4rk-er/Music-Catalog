from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User
from music.models import Playlist, PlaylistTrack, Performer, Track
from .serializers import (PlaylistTrackListSerializer, PerformerSerializer,
                          PlaylistSerializer, TrackSerializer, UserSerializer)


class PerformerViewSet(viewsets.ModelViewSet):
    queryset = Performer.objects.all()
    http_method_names = ['get', 'post']
    serializer_class = PerformerSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    http_method_names = ['get', 'post', 'delete']

    @action(
        detail=True, methods=['post', 'delete'],
        serializer_class=PlaylistTrackListSerializer,
        url_name='add_tracks'
    )
    def add_tracks(self, request, pk=None):
        playlist = get_object_or_404(Playlist, pk=pk)
        tracks_data = request.data.get('tracks', [])
        serializer = PlaylistTrackListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.method == 'POST':
            existing_tracks = playlist.tracks.all().values_list('id', flat=True)
            tracks_obj = []

            for track_id in tracks_data:
                if track_id in existing_tracks:
                    return Response(
                        {'error': f'Трек {track_id} уже есть в альбоме.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                track = get_object_or_404(Track, pk=track_id)
                tracks_obj.append(track)

            for track in tracks_obj:
                playlist_track = PlaylistTrack(
                    playlist=playlist,
                    track=track
                )
                playlist_track.save()

            serializer = PlaylistSerializer(playlist)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            for track in tracks_data:
                if PlaylistTrack.objects.filter(
                    playlist=playlist, track=track
                ).exists():
                    PlaylistTrack.objects.get(playlist=playlist,
                                              track=track).delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(
                    {'error': f'Трек {track} не добавлен в альбом'},
                    status=status.HTTP_400_BAD_REQUEST
                )


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    http_method_names = ['get', 'post', 'delete']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'delete']
