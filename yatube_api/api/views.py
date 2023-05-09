from django.shortcuts import get_object_or_404
from posts.models import Comment, Follow, Group, Post, User
from rest_framework import filters, status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .permissions import IsOwnerOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    def get_queryset(self):
        pk_post = self.kwargs.get("pk_post")
        new_queryset = Comment.objects.filter(post=pk_post)
        return new_queryset

    def perform_create(self, serializer):
        pk_post = self.kwargs.get("pk_post")
        post = Post.objects.get(pk=pk_post)
        serializer.save(post=post, author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        return queryset

    def create(self, request):
        user = request.user
        following_username = request.data.get('following')
        if following_username:
            following = get_object_or_404(User, username=following_username)
            if following == user:
                return Response({'error': 'You cannot follow yourself.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=user, following=following).exists():
                return Response({'error':
                                 'You are already following this user.'},
                                status=status.HTTP_400_BAD_REQUEST)
            follow = Follow.objects.create(user=user, following=following)
            serializer = self.get_serializer(follow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Missing following username.'},
                            status=status.HTTP_400_BAD_REQUEST)
