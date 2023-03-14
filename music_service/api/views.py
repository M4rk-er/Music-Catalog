from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from music.models import (Album, AlbumTrack, FavoriteAlbum, FavoritePlaylist,
                          FavoriteTrack, Performer, Playlist, PlaylistTrack,
                          Track)
from users.models import User

from .pagination import CustomPagination
from .permissions import CustomUserPermissions
from .serializers import (AddTrackListSerializer, AlbumFavoriteSerializer,
                          AlbumSerializer, PasswordSerializer,
                          PerformerSerializer, PlaylistFavoriteSerializer,
                          PlaylistSerializer, TrackFavoriteSerializer,
                          TrackSerializer, UserSerializer)


class PerformerViewSet(viewsets.ModelViewSet):
    queryset = Performer.objects.all()
    http_method_names = ['get', 'post']
    serializer_class = PerformerSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    http_method_names = ['get', 'post', 'delete']
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(
        detail=True, methods=['post', 'delete'],
        serializer_class=AddTrackListSerializer,
        url_name='add_tracks',
    )
    def add_tracks(self, request, pk=None):
        playlist = get_object_or_404(Playlist, pk=pk)
        playlist_author = playlist.created_by
        if request.user != playlist_author:
            return Response(
                {'error': 'Нельзя добавлять трек в не в свой плейлист'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tracks_data = request.data.get('tracks', [])
        serializer = AddTrackListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.method == 'POST':
            existing_tracks = playlist.tracks.all().values_list('id', flat=True)
            tracks_obj = []

            for track_id in tracks_data:
                if track_id in existing_tracks:
                    return Response(
                        {'error': f'Трек {track_id} уже есть в плейлисте.'},
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

    @action(
        detail=True, methods=['post', 'delete'],
        url_name='favorite', permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        user = request.user
        playlist = get_object_or_404(Playlist, pk=kwargs['pk'])

        if request.method == 'POST':
            if FavoritePlaylist.objects.filter(user=user,
                                               playlist=playlist).exists():
                return Response(
                    {'errors': 'Плейлист уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = PlaylistFavoriteSerializer(playlist)
            FavoritePlaylist.objects.create(user=user, playlist=playlist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if FavoritePlaylist.objects.filter(user=user,
                                               playlist=playlist).exists():
                FavoritePlaylist.objects.get(user=user,
                                             playlist=playlist).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Плейлист не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False, methods=['get'],
        url_name='favourites',
        permission_classes=(IsAuthenticated,)
    )
    def favourites(self, request, *args, **kwargs):
        user = request.user
        favorites_playlists = FavoritePlaylist.objects.filter(
            user=user
        ).values_list('playlist', flat=True)
        playlists = Playlist.objects.filter(id__in=favorites_playlists)
        serializer = AlbumSerializer(playlists,
                                     many=True,
                                     context={'request': request})
        return Response(serializer.data)


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    http_method_names = ['get', 'post', 'delete']
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    @action(
        detail=True, methods=['post', 'delete'],
        url_name='favorite', permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        user = request.user
        track = get_object_or_404(Track, pk=kwargs['pk'])

        if request.method == 'POST':
            if FavoriteTrack.objects.filter(user=user, track=track).exists():
                return Response(
                    {'errors': 'Трек уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = TrackFavoriteSerializer(track)
            FavoriteTrack.objects.create(user=user, track=track)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if FavoriteTrack.objects.filter(user=user, track=track).exists():
                FavoriteTrack.objects.get(user=user, track=track).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Трек не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False, methods=['get'],
        url_name='favourites',
        permission_classes=(IsAuthenticated,)
    )
    def favourites(self, request, *args, **kwargs):
        user = request.user
        favorites_tracks = FavoriteTrack.objects.filter(
            user=user
        ).values_list('track', flat=True)
        tracks = Track.objects.filter(id__in=favorites_tracks)
        serializer = TrackSerializer(tracks,
                                     many=True,
                                     context={'request': request})
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (CustomUserPermissions,)
    http_method_names = ['get', 'post', 'delete']
    pagination_class = CustomPagination

    @action(
        detail=False, methods=['post'],
        url_name='set_password', url_path='set_password',
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        user = get_object_or_404(User, username=request.user)
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.data['current_password']):
            return Response({'status': 'Текцщий пароль указан неверно'})
        user.set_password(serializer.data['new_password'])
        user.save()
        return Response(
            {'status': 'Пароль изменен'},
            status=status.HTTP_204_NO_CONTENT
        )


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    http_method_names = ['get', 'post', 'delete']
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(
        detail=True, methods=['post', 'delete'],
        serializer_class=AddTrackListSerializer,
        url_name='add_tracks'
    )
    def add_tracks(self, request, pk=None):
        album = get_object_or_404(Album, pk=pk)
        album_created_by = album.created_by
        err_msg = 'Нельзя добавлять трек альбом созданный другим пользователем'
        if request.user != album_created_by:
            return Response(
                {'error': err_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        tracks_data = request.data.get('tracks', [])
        serializer = AddTrackListSerializer(data=request.data)
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

            serializer = PlaylistSerializer(album)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            for track in tracks_data:
                if AlbumTrack.objects.filter(
                    album=album, track=track
                ).exists():
                    PlaylistTrack.objects.get(album=album,
                                              track=track).delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(
                    {'error': f'Трек {track} не добавлен в альбом'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=True, methods=['post', 'delete'],
        url_name='favorite', permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        user = request.user
        album = get_object_or_404(Album, pk=kwargs['pk'])

        if request.method == 'POST':
            if FavoriteAlbum.objects.filter(user=user, album=album).exists():
                return Response(
                    {'errors': 'Альбом уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = AlbumFavoriteSerializer(album)
            FavoriteAlbum.objects.create(user=user, album=album)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if FavoriteAlbum.objects.filter(user=user, album=album).exists():
                FavoriteAlbum.objects.get(user=user, album=album).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Альбом не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False, methods=['get'],
        url_name='favourites',
        permission_classes=(IsAuthenticated,)
    )
    def favourites(self, request, *args, **kwargs):
        user = request.user
        favorites_albums = FavoriteAlbum.objects.filter(
            user=user
        ).values_list('album', flat=True)
        albums = Album.objects.filter(id__in=favorites_albums)
        serializer = AlbumSerializer(albums,
                                     many=True,
                                     context={'request': request})
        return Response(serializer.data)
