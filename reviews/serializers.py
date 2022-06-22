from rest_framework             import serializers
from rest_framework.serializers import ModelSerializer

from reviews.models import Review, ReviewImage


class ReviewImageSerializer(ModelSerializer):
    
    class Meta:
        model  = ReviewImage
        fields = ['id', 'image_url']


class ReviewSerializer(ModelSerializer):
    user      = serializers.CharField(source='user.name')
    image_url = ReviewImageSerializer(source='reviewimage_set', many=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'title', 'content', 'rating', 'image_url']

