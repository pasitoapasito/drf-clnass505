from django.db   import models
from core.models import TimeStamp

class Review(TimeStamp):
    title   = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    rating  = models.PositiveIntegerField()
    user    = models.ForeignKey('users.User', on_delete=models.CASCADE)
    lecture = models.ForeignKey('lectures.Lecture', on_delete=models.CASCADE)

    class Meta:
        db_table = 'reviews'

class ReviewImage(TimeStamp):
    image_url = models.CharField(max_length=2000)
    review    = models.ForeignKey('Review', on_delete=models.CASCADE)

    class Meta:
        db_table = 'review_images'