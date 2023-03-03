from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Album, AlbumTrack, Performer, Track
from .serializers import (AlbumTrackListSerializer, CreateAlbumSerializer,
                          CreatePerformerSerializer, CreateTrackSerializer,
                          GetAlbumSerializer, GetPerformerSerializer,
                          GetTrackSerializer)


class PerformerViewSet(viewsets.ModelViewSet):
    queryset = Performer.objects.all()
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        print(self.request.method)
        if self.request.method in ['GET']:
            return GetPerformerSerializer
        return CreatePerformerSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetAlbumSerializer
        return CreateAlbumSerializer

    @action(
        detail=True, methods=['post', 'delete'],
        serializer_class=AlbumTrackListSerializer,
        url_name='add_tracks'
    )
    def add_tracks(self, request, pk=None):
        album = get_object_or_404(Album, pk=pk)
        tracks_data = request.data.get('tracks', [])
        serializer = AlbumTrackListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.method == 'POST':
            existing_tracks = album.tracks.all().values_list('id', flat=True)
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
                album_track = AlbumTrack(
                    album=album,
                    track=track
                )
                album_track.save()

            serializer = GetAlbumSerializer(album)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            for track in tracks_data:
                if AlbumTrack.objects.filter(album=album, track=track).exists():
                    AlbumTrack.objects.get(album=album, track=track).delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(
                    {'error': f'Трек {track} не добавлен в альбом'},
                    status=status.HTTP_400_BAD_REQUEST
                )


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetTrackSerializer
        return CreateTrackSerializer
