from rest_framework             import serializers
from rest_framework.serializers import ModelSerializer

from django.db.models           import Avg

from lectures.models            import Lecture, LectureImage
from reviews.serializers        import ReviewSerializer


class LectureListSerializer(ModelSerializer):
    
    creator_nickname = serializers.CharField(source='user.name')
    like_count       = serializers.SerializerMethodField()
   
    def get_like_count(self, obj):
        return obj.likes
        
    class Meta:
        model  = Lecture
        fields = ['id', 'name', 'price', 'discount_rate', 'thumbnail_image_url', 'creator_nickname', 'like_count']
        extra_kwargs = {
            'id': {'read_only': True}
        }


class LectureImageSerializer(ModelSerializer):
    
    class Meta:
        model  = LectureImage
        fields = ['id', 'title', 'sequence', 'image_url']

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