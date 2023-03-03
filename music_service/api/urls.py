from django.urls import include, path
from rest_framework import routers, permissions
from rest_framework.documentation import include_docs_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import AlbumViewSet, PerformerViewSet, TrackViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register('performers', PerformerViewSet, basename='performers')
router.register('albums', AlbumViewSet, basename='albums')
router.register('tracks', TrackViewSet, basename='tracks')


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
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
