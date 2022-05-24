from django.db   import models
from core.models import TimeStamp

class Lecture(TimeStamp):
    name                = models.CharField(max_length=200)
    price               = models.DecimalField(max_digits=10, decimal_places=2)
    discount_rate       = models.PositiveIntegerField()
    thumbnail_image_url = models.CharField(max_length=2000)
    description         = models.CharField(max_length=500)
    user                = models.ForeignKey('users.User', on_delete=models.CASCADE)
    difficulty          = models.ForeignKey('Difficulty', on_delete=models.CASCADE)
    subcategory         = models.ForeignKey('Subcategory', on_delete=models.CASCADE)

    class Meta:
        db_table = 'lectures'

class Difficulty(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'difficulties'

class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'categories'

class Subcategory(models.Model):
    name     = models.CharField(max_length=50)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    class Meta:
        db_table = 'subcategories'

class LectureImage(TimeStamp):
    title     = models.CharField(max_length=100)
    image_url = models.CharField(max_length=2000)
    sequence  = models.PositiveIntegerField()
    lecture   = models.ForeignKey('Lecture', on_delete=models.CASCADE)

    class Meta:
        db_table = 'lecture_images'