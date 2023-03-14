from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers
from rest_framework.authtoken import views

from .views import (AlbumViewSet, PerformerViewSet, PlaylistViewSet,
                    TrackViewSet, UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()

router.register('performers', PerformerViewSet, basename='performers')
router.register('playlists', PlaylistViewSet, basename='playlists')
router.register('tracks', TrackViewSet, basename='tracks')
router.register('users', UserViewSet, basename='users')
router.register('albums', AlbumViewSet, basename='album')


schema_view = get_schema_view(
    openapi.Info(
        title='Music Service',
        default_version='v1',
        description='Музыкальные каталоги',
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('', include(router.urls)),
    path('token/', views.obtain_auth_token),
    path('swagger/',
         schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]
