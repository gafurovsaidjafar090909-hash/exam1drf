from datetime import timedelta
from django.db.models import Count, Sum, Avg, Min, Max, Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import *

# GET /api/users/
# POST /api/users/
@api_view(['GET', 'POST'])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.annotate(posts_count=Count('posts', distinct=True),likes_count=Count('likes', distinct=True),favorites_count=Count('favorites', distinct=True), ).order_by('id')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# GET /api/users/1/
# PUT /api/users/1/
# PATCH /api/users/1/
# DELETE /api/users/1/
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found'},status=404)
    if request.method == 'GET':
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    if request.method == 'DELETE':
        user.delete()
        return Response(status=204)
    partial = request.method == 'PATCH'
    serializer = UserSerializer(user,data=request.data,partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ==========================================
# USERS — MOST ACTIVE
# ==========================================

# GET /api/users/most-active/
@api_view(['GET'])
def most_active_users(request):
    users = User.objects.annotate(posts_count=Count('posts', distinct=True)).order_by('-posts_count', 'id')[:10]
    data = users.values('id','username','posts_count')
    return Response(data)


# ==========================================
# USERS — STATISTICS
# ==========================================

# GET /api/users/statistics/
@api_view(['GET'])
def user_statistics(request):
    data = User.objects.aggregate(
        total_users=Count('id'),
        average_age=Avg('age'),
        min_age=Min('age'),
        max_age=Max('age'),)

    return Response(data)


# ==========================================
# PROFILES — CRUD
# ==========================================

# GET /api/profiles/
# POST /api/profiles/
@api_view(['GET', 'POST'])
def profile_list(request):
    if request.method == 'GET':
        profiles = Profile.objects.annotate(posts_count=Count('user__posts',distinct=True)).select_related('user')
        serializer = ProfileSerializer(profiles,many=True)
        return Response(serializer.data)
    serializer = ProfileCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# GET /api/profiles/1/
# PUT /api/profiles/1/
# PATCH /api/profiles/1/
# DELETE /api/profiles/1/
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def profile_detail(request, pk):
    try:
        profile = Profile.objects.select_related('user').get(pk=pk)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'},status=404)
    if request.method == 'GET':
        profile = Profile.objects.annotate(posts_count=Count('user__posts',distinct=True)).select_related('user').get(pk=pk)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    if request.method == 'DELETE':
        profile.delete()
        return Response(status=204)
    partial = request.method == 'PATCH'
    serializer = ProfileCreateSerializer(profile,data=request.data,partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# GET /api/profiles/city-statistics/
@api_view(['GET'])
def city_statistics(request):
    cities = Profile.objects.values('city').annotate(users_count=Count('user', distinct=True)).order_by('-users_count')
    return Response(cities)



# GET /api/posts/
# POST /api/posts/
@api_view(['GET', 'POST'])
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.annotate(likes_count=Count('likes',distinct=True),favorites_count=Count('favorites',distinct=True),).select_related('user').order_by('-id')
        serializer = PostListSerializer(posts,many=True)
        return Response(serializer.data)
    serializer = PostWriteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)



# GET /api/posts/1/
# PUT /api/posts/1/
# PATCH /api/posts/1/
# DELETE /api/posts/1/
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'},status=404)
    if request.method == 'GET':
        post = Post.objects.annotate(likes_count=Count('likes',distinct=True),favorites_count=Count('favorites',distinct=True),).select_related('user').get(pk=pk)
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)
    if request.method == 'DELETE':
        post.delete()
        return Response(status=204)
    partial = request.method == 'PATCH'
    serializer = PostWriteSerializer(post,data=request.data,partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ==========================================
# USER POSTS
# ==========================================

# GET /api/users/1/posts/
@api_view(['GET'])
def user_posts(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'},status=404)
    posts = Post.objects.filter(user=user).annotate(likes_count=Count('likes', distinct=True)).order_by('-id')
    data = []
    for post in posts:
        data.append({
            'id': post.id,
            'title': post.title,
            'likes_count': post.likes_count,
            'views': post.views,
        })
    return Response({
        'user': {'id': user.id,'username': user.username, },'posts_count': posts.count(),'results': data,})


# GET /api/posts/popular/
@api_view(['GET'])
def popular_posts(request):
    posts = Post.objects.annotate(likes_count=Count('likes', distinct=True),favorites_count=Count('favorites',distinct=True ),).filter(likes_count__gte=10).order_by('-likes_count')
    data = []
    for post in posts:
        data.append({
            'id': post.id,
            'title': post.title,
            'likes_count': post.likes_count,
            'favorites_count': post.favorites_count,
            'is_popular': True,
        })
    return Response(data)



# GET /api/posts/search/?q=django
@api_view(['GET'])
def search_posts(request):
    q = request.query_params.get('q', '').strip()
    if not q:
        return Response([])
    posts = Post.objects.filter(Q(title__icontains=q)| Q(content__icontains=q) ).annotate(likes_count=Count('likes', distinct=True),favorites_count=Count('favorites',distinct=True ),).order_by('-id')
    serializer = PostListSerializer(posts, many=True)
    return Response(serializer.data)


# GET /api/posts/filter/?min_views=100&max_views=2000&user_id=1
@api_view(['GET'])
def filter_posts(request):
    posts = Post.objects.all()
    min_views = request.query_params.get('min_views')
    max_views = request.query_params.get('max_views')
    user_id = request.query_params.get('user_id')
    if min_views is not None:
        posts = posts.filter(views__gte=min_views)
    if max_views is not None:
        posts = posts.filter(views__lte=max_views)
    if user_id is not None:
        posts = posts.filter(user_id=user_id)
    posts = posts.annotate(likes_count=Count('likes', distinct=True),favorites_count=Count('favorites',distinct=True),).order_by('-id')
    serializer = PostListSerializer(posts,many=True)
    return Response(serializer.data)



# GET /api/posts/statistics/
@api_view(['GET'])
def post_statistics(request):
    data = Post.objects.aggregate(
        total_posts=Count('id'),
        total_views=Sum('views'),
        average_views=Avg('views'),
        max_views=Max('views'),
        min_views=Min('views'),
    )
    data['total_likes'] = Like.objects.count()
    data['total_favorites'] = Favorite.objects.count()
    return Response(data)


# GET /api/posts/author-statistics/
@api_view(['GET'])
def author_statistics(request):
    users = User.objects.annotate(
        posts_count=Count('posts',distinct=True),
        total_views=Sum('posts__views'),
        average_views=Avg('posts__views'),
        likes_received=Count('posts__likes',distinct=True),).order_by('id')
    data = []
    for user in users:
        data.append({
            'user_id': user.id,
            'username': user.username,
            'posts_count': user.posts_count,
            'total_views': user.total_views or 0,
            'average_views': user.average_views or 0,
            'likes_received': user.likes_received,
        })
    return Response(data)




# GET /api/likes/
# POST /api/likes/
@api_view(['GET', 'POST'])
def like_list(request):
    if request.method == 'GET':
        likes = Like.objects.select_related('user','post').order_by('-created_at')
        serializer = LikeSerializer(likes,many=True)
        return Response(serializer.data)
    serializer = LikeCreateSerializer(data=request.data)
    if serializer.is_valid():
        like = serializer.save()
        return Response(LikeSerializer(like).data,status=201)
    return Response(serializer.errors, status=400)


# DELETE /api/likes/1/
@api_view(['DELETE'])
def like_delete(request, pk):
    try:
        like = Like.objects.get(pk=pk)
    except Like.DoesNotExist:
        return Response(
            {'error': 'Like not found'},
            status=404
        )

    like.delete()
    return Response(status=204)



# GET /api/posts/1/likes/
@api_view(['GET'])
def post_likes(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'},status=404)
    likes = Like.objects.filter(post=post).select_related('user')
    users = [{'id': like.user.id,'username': like.user.username,}for like in likes]
    return Response({'post_id': post.id,'likes_count': likes.count(),'users': users,})



# GET /api/likes/top-posts/
@api_view(['GET'])
def top_posts(request):
    posts = Post.objects.annotate(likes_count=Count('likes', distinct=True)).order_by('-likes_count', 'id')[:10]
    data = []
    for post in posts:
        data.append({'post_id': post.id,'title': post.title,'likes_count': post.likes_count,})
    return Response(data)



# GET /api/favorites/
# POST /api/favorites/
@api_view(['GET', 'POST'])
def favorite_list(request):
    if request.method == 'GET':
        favorites = Favorite.objects.select_related('user','post','post__user').annotate(likes_count=Count('post__likes',distinct=True )).order_by('-created_at')
        serializer = FavoriteSerializer(favorites,many=True)
        return Response(serializer.data)
    serializer = FavoriteCreateSerializer(data=request.data)
    if serializer.is_valid():
        favorite = serializer.save()
        return Response(FavoriteSerializer(favorite).data,status=201)
    return Response(serializer.errors, status=400)


# DELETE /api/favorites/1/
@api_view(['DELETE'])
def favorite_delete(request, pk):
    try:
        favorite = Favorite.objects.get(pk=pk)
    except Favorite.DoesNotExist:
        return Response({'error': 'Favorite not found'},status=404)
    favorite.delete()
    return Response(status=204)



# GET /api/users/2/favorites/
@api_view(['GET'])
def user_favorites(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'},status=404)
    favorites = Favorite.objects.filter(user=user).select_related('post').annotate(likes_count=Count('post__likes',distinct=True)).order_by('-id')
    data = []
    for favorite in favorites:
        data.append({
            'post_id': favorite.post.id,
            'title': favorite.post.title,
            'likes_count': favorite.likes_count,
            'views': favorite.post.views,
        })
    return Response({'user': user.username,'favorites_count': favorites.count(),'results': data,})



# GET /api/users/1/analytics/
@api_view(['GET'])
def user_analytics(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'},status=404)
    posts = Post.objects.filter(user=user)
    posts_data = posts.aggregate(posts_count=Count('id'),total_views=Sum('views'),average_views=Avg('views'),)
    likes_received = Like.objects.filter(post__user=user).count()
    favorites_received = Favorite.objects.filter(post__user=user).count()
    likes_given = Like.objects.filter(user=user).count()
    favorites_given = Favorite.objects.filter(user=user).count()
    seven_days_ago = timezone.now() - timedelta(days=7)
    posts_last_7_days = posts.filter(created_at__gte=seven_days_ago).count()
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': f'{user.first_name} {user.last_name}',
        },
        'posts': {
            'posts_count': posts_data['posts_count'],
            'total_views': posts_data['total_views'] or 0,
            'average_views': posts_data['average_views'] or 0,
        },
        'engagement': {
            'likes_received': likes_received,
            'favorites_received': favorites_received,
            'likes_given': likes_given,
            'favorites_given': favorites_given,
        },
        'activity': {
            'posts_last_7_days': posts_last_7_days,
            'is_active_user': posts_last_7_days > 0,
        },
    })



# GET /api/dashboard/
@api_view(['GET'])
def dashboard(request):
    posts_data = Post.objects.aggregate(
        total_views=Sum('views'),
        average_views=Avg('views'),
    )

    statistics = {
        'users_count': User.objects.count(),
        'profiles_count': Profile.objects.count(),
        'posts_count': Post.objects.count(),
        'likes_count': Like.objects.count(),
        'favorites_count': Favorite.objects.count(),
        'total_views': posts_data['total_views'] or 0,
        'average_views': posts_data['average_views'] or 0,
    }

    active_user = User.objects.annotate(
        posts_count=Count('posts', distinct=True)
    ).order_by('-posts_count', 'id').first()

    most_active_user = None

    if active_user:
        most_active_user = {
            'id': active_user.id,
            'username': active_user.username,
            'posts_count': active_user.posts_count,
        }

    popular_post = Post.objects.annotate(
        likes_count=Count('likes', distinct=True)
    ).order_by('-likes_count', 'id').first()

    most_popular_post = None

    if popular_post:
        most_popular_post = {
            'id': popular_post.id,
            'title': popular_post.title,
            'likes_count': popular_post.likes_count,
        }

    latest = Post.objects.annotate(
        likes_count=Count('likes', distinct=True)
    ).select_related('user').order_by('-created_at')[:5]

    latest_posts = []

    for post in latest:
        latest_posts.append({
            'id': post.id,
            'title': post.title,
            'author': post.user.username,
            'likes_count': post.likes_count,
        })

    return Response({
        'statistics': statistics,
        'most_active_user': most_active_user,
        'most_popular_post': most_popular_post,
        'latest_posts': latest_posts,
    })
