from rest_framework import serializers
from .models import User, Profile, Post, Like, Favorite


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'city']


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','username','full_name','age',]
        
    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id','username','full_name','age','profile','statistics']
    def get_full_name(self, data):
        return f'{data.first_name} {data.last_name}'.strip()
    def get_profile(self, data):
        try:
            return ProfileSerializer(data.profile).data
        except Profile.DoesNotExist:
            return None
    def get_statistics(self, data):
        posts = Post.objects.filter(user=data)
        return {
            'posts_count': posts.count(),
            'total_views': sum(post.views for post in posts),
            'likes_received': Like.objects.filter(post__user=data).count(),
            'favorites_received': Favorite.objects.filter(post__user=data).count()
        }



class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']



class ProfileSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profile
        fields = ['id','user','bio','city','birth_date','avatar','posts_count',]


class ProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'city', 'birth_date', 'avatar']




class AuthorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']
    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip()


class PostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source='user', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    is_popular = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'views','likes_count', 'favorites_count', 'is_popular','created_at']
    def get_is_popular(self, obj):
        return obj.likes_count >= 10


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(source='user', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    liked_by = UserShortSerializer(source='likers', many=True, read_only=True)
    favorited_by = UserShortSerializer(source='favoriters', many=True, read_only=True)
    is_popular = serializers.SerializerMethodField()
    is_viral = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'views','likes_count', 'favorites_count', 'liked_by','favorited_by', 'is_popular', 'is_viral','status', 'created_at']
    def get_is_popular(self, obj):
        return obj.likes_count >= 10

    def get_is_viral(self, obj):
        return obj.views >= 1000 and obj.likes_count >= 10

    def get_status(self, obj):
        if obj.likes_count > 0:
            return 'has_likes'
        return 'no_likes'


class PostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['user', 'title', 'content', 'views']


class LikeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title']


class LikeSerializer(serializers.ModelSerializer):
    user = LikeUserSerializer(read_only=True)
    post = LikePostSerializer(read_only=True)
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']


class LikeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['user', 'post']

    def validate(self, attrs):
        user = attrs['user']
        post = attrs['post']
        if Like.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError('error')
        return attrs



class FavoriteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class FavoritePostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='user.username', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'author', 'likes_count']


class FavoriteSerializer(serializers.ModelSerializer):
    user = FavoriteUserSerializer(read_only=True)
    post = FavoritePostSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'post', 'created_at']



class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'post']
    def validate(self, attrs):
        user = attrs['user']
        post = attrs['post']
        if Favorite.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError('error')
        return attrs


class FavoritePostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='user.username',read_only=True)
    likes_count = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id', 'title', 'author', 'likes_count']
    def get_likes_count(self, obj):
        return obj.likes.count()




