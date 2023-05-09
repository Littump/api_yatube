from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

v1_router = SimpleRouter()
v1_router.register('posts', views.PostViewSet)
v1_router.register(r'posts/(?P<pk_post>\d+)/comments',
                   views.CommentViewSet, basename='comment')
v1_router.register('groups', views.GroupViewSet)
v1_router.register(r'follow', views.FollowViewSet)


urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]
