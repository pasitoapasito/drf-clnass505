from rest_framework             import serializers
from rest_framework.serializers import ModelSerializer

from django.db.models           import Avg
from django.db                  import transaction

from lectures.models            import Lecture, LectureImage, Difficulty, Subcategory
from reviews.serializers        import ReviewSerializer
from users.models               import User, Like

'''
from core.storage               import FileUpload, s3_client

from clnass505_drf.settings     import (
    BUCKET_DIR_THUMBNAIL,
    BUCKET_DIR_IMAGE,
    BUCKET_DIR_PROFILE 
)
'''

'''
class LectureCreateSerializer(ModelSerializer):
    
    @transaction.atomic()
    def create(self, validated_data):
        file_handler = FileUpload(s3_client)
        
        user    = validated_data.pop('user')
        profile = validated_data.pop('profile_image_url')
        
        uploaded_profile_image_url = file_handler.upload(profile, BUCKET_DIR_PROFILE)
        user.profile_image_url     = uploaded_profile_image_url
        user.save
        
        name           = validated_data.pop('name')
        price          = validated_data.pop('price')
        thumbnail      = validated_data.pop('thumbnail_image_url')
        discount_rate  = validated_data.pop('discount_rate')
        difficulty_id  = validated_data.pop('difficulty')
        subcategory_id = validated_data.pop('subcategory')
        description    = validated_data.pop('description')
        
        try:
            difficulty = Difficulty.objects.get(id=difficulty_id)
        except Difficulty.DoesNotExist:
            raise serializers.ValidationError(f'difficulty id {difficulty_id} does not exists')
        try:
            subcategory = Subcategory.objects.get(id=subcategory_id)
        except Subcategory.DoesNotExist:
            raise serializers.ValidationError(f'subcategory id {subcategory_id} does not exists')

        uploaded_thumbnail_url = file_handler.upload(thumbnail, BUCKET_DIR_THUMBNAIL)
        lecture = Lecture.obejcts.create(
            name                = name,
            price               = price,
            user_id             = user.id,
            discount_rate       = discount_rate,
            thumbnail_image_url = uploaded_thumbnail_url,
            description         = description,
            difficulty          = difficulty,
            subcategory         = subcategory
        )
        
        bulk_lecture_images = []
        
        lecture_images = validated_data.pop('lecture_images_url')
        title          = validated_data.pop('title')
        
        for idx, lecture_image in enumerate(lecture_images):
            uploaded_lecture_image_url = file_handler.upload(lecture_image, BUCKET_DIR_IMAGE)
            
            bulk_lecture_images.append(
                LectureImage(
                    title      = title,
                    image_url  = uploaded_lecture_image_url,
                    sequence   = idx + 1,
                    lecture_id = lecture.id
                    )
                )
        
        return lecture
    
    class Meta:
        model  = Lecture
        fields = [
            'id', 'user', 'name', 'price', 'discount_rate', 'difficulty',\
            'subcategory', 'description', 'thumbnail_image_url'
        ]
        extra_kwargs = {
            'id': {'read_only': True}
        }
'''


class LectureLikeSerializer(ModelSerializer):
    subcategory               = serializers.CharField(source='lecture.subcategory.name')
    creator_nickname          = serializers.CharField(source='lecture.user.name')
    creator_profile_image_url = serializers.CharField(source='lecture.user.profile_image_url')
    name                      = serializers.CharField(source='lecture.name')
    price                     = serializers.IntegerField(source='lecture.price')
    thumbnail_image_url       = serializers.CharField(source='lecture.thumbnail_image_url')
    discount_rate             = serializers.SerializerMethodField()
    discount_price            = serializers.SerializerMethodField()
    like_count                = serializers.SerializerMethodField()
    
    def get_discount_rate(self, obj):
        return obj.lecture.discount_rate if obj.lecture.discount_rate else None
    
    def get_discount_price(self, obj):
        calculated_price = float(obj.lecture.price) * (1-(obj.lecture.discount_rate/100))\
                           if obj.lecture.discount_rate else None
        return calculated_price    
    
    def get_like_count(self, obj):
        return obj.lecture.like_set.count()
    
    class Meta:
        model  = Like
        fields = [
            'id', 'subcategory', 'creator_nickname', 'creator_profile_image_url',\
            'name', 'price', 'thumbnail_image_url', 'discount_rate', 'discount_price',\
            'like_count'
        ]
        extra_kwargs = {
            'id': {'read_only': True}
        }
    
    
class LectureSerializer(ModelSerializer):
    
    subcategory               = serializers.CharField(source='subcategory.name')
    creator_profile_image_url = serializers.CharField(source='user.profile_image_url')
    creator_nickname          = serializers.CharField(source='user.nickname')
    like_count                = serializers.SerializerMethodField()
    discount_rate             = serializers.SerializerMethodField()
    discount_price            = serializers.SerializerMethodField()
    user_like_status          = serializers.SerializerMethodField()
   
    def get_like_count(self, obj):
        return obj.likes
    
    def get_discount_rate(self, obj):
        return obj.discount_rate if obj.discount_rate else None
    
    def get_discount_price(self, obj):
        calculated_price = float(obj.price) * (1-(obj.discount_rate)/100)\
                           if obj.discount_rate else None
        return calculated_price
    
    def get_user_like_status(self, obj):
        user    = self.context.get('user', None)
        lecture = obj
        if user:
            return Like.objects.filter(user=user, lecture=lecture).exists()
        return False
    
    class Meta:
        model  = Lecture
        fields = [
            'id', 'name', 'price', 'discount_rate', 'thumbnail_image_url', 'creator_nickname',\
            'like_count', 'creator_profile_image_url', 'subcategory', 'discount_price', 'user_like_status'
        ]
        extra_kwargs = {
            'id': {'read_only': True}
        }


class LectureImageSerializer(ModelSerializer):
    
    class Meta:
        model  = LectureImage
        fields = ['id', 'title', 'sequence', 'image_url']
        extra_kwargs = {
            'id': {'read_only': True}
        }


class LectureDetailSerializer(ModelSerializer):
    subcategory               = serializers.CharField(source='subcategory.name')
    creator_nickname          = serializers.CharField(source='user.name')
    creator_profile_image_url = serializers.CharField(source='user.profile_image_url')
    difficulty                = serializers.CharField(source='difficulty.name')
    lecture_images            = LectureImageSerializer(source='lectureimage_set', many=True, required=False)
    reviews                   = ReviewSerializer(source='review_set', many=True, required=False)
    discount_rate             = serializers.SerializerMethodField()
    discount_price            = serializers.SerializerMethodField()
    review_avg_rating         = serializers.SerializerMethodField()
    
    def get_discount_rate(self, obj):
        return obj.discount_rate if obj.discount_rate else None
    
    def get_discount_price(self, obj):
        calculated_price = float(obj.price) * (1-(obj.discount_rate)/100)\
                           if obj.discount_rate else None
        return calculated_price

    def get_review_avg_rating(self, obj):
        avg_rating = round(obj.review_set.all().aggregate(Avg('rating'))['rating__avg'], 1)\
                     if obj.review_set.all() else None
        return avg_rating

    class Meta:
        model  = Lecture
        fields = [
            'id', 'subcategory', 'creator_nickname', 'creator_profile_image_url',\
            'name', 'price', 'discount_rate', 'discount_price', 'description',\
            'difficulty', 'review_avg_rating', 'thumbnail_image_url', 'lecture_images',\
            'reviews'
        ]
        extra_kwargs = {
            'id': {'read_only': True}
        }