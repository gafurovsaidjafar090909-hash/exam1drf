
from django.contrib import admin
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version="v1",
        description="API Documentation",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],

)

from django.urls import path
from .views import *

urlpatterns = [
    path('users/', user_list, name='user_list'),
    path('users/most-active/', most_active_users, name='most_active_users'),
    path('users/statistics/', user_statistics, name='user_statistics'),
    path('users/<int:user_id>/posts/', user_posts, name='user_posts'),
    path('users/<int:pk>/', user_detail, name='user_detail'),
    path('users/most-active/', most_active_users),
    path('profiles/', profile_list, name='profile_list'),
    path('profiles/city-statistics/', city_statistics, name='city_statistics'),
    path('profiles/<int:pk>/', profile_detail, name='profile_detail'),
    path('posts/', post_list, name='post_list'),
    path('posts/popular/', popular_posts, name='popular_posts'),
    path('posts/search/', search_posts, name='search_posts'),
    path('posts/filter/', filter_posts, name='filter_posts'),
    path('posts/statistics/', post_statistics, name='post_statistics'),
    path('posts/author-statistics/', author_statistics, name='author_statistics'),
    path('posts/<int:pk>/', post_detail, name='post_detail'),
    path('likes/', like_list, name='like_list'),
    path('likes/top-posts/', top_posts, name='top_posts'),
    path('likes/<int:pk>/', like_delete, name='like_delete'),
    path('posts/<int:post_id>/likes/', post_likes, name='post_likes'),
    path('favorites/', favorite_list, name='favorite_list'),
    path('favorites/<int:pk>/', favorite_delete, name='favorite_delete'),
    path('users/<int:user_id>/favorites/', user_favorites, name='user_favorites'),
    path('users/<int:user_id>/analytics/',user_analytics,name='user_analytics'),
    path('dashboard/',dashboard,name='dashboard'),

      path('admin/', admin.site.urls),
    
        re_path(
            r'^swagger/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui',
        ),
    
        re_path(
            r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc',
        ),
]


