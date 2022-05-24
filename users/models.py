from django.db   import models
from core.models import TimeStamp

class User(TimeStamp):
    name              = models.CharField(max_length=50, null=True)
    nickname          = models.CharField(max_length=50, null=True)
    kakao_id          = models.BigIntegerField()
    email             = models.CharField(max_length=100, null=True)
    description       = models.CharField(max_length=500, null=True)
    profile_image_url = models.CharField(max_length=2000, default='https://cdn.pixabay.com/photo/2016/03/31/19/58/avatar-1295429_960_720.png')
    point             = models.IntegerField(default=1000000)
    lectures          = models.ManyToManyField('lectures.Lecture', through='UserLecture', related_name='users')

    class Meta:
        db_table = 'users'

class UserLecture(TimeStamp):
    user    = models.ForeignKey('User', on_delete=models.CASCADE)
    lecture = models.ForeignKey('lectures.Lecture', on_delete=models.CASCADE)

    class Meta:
        db_table = 'users_lectures'

class Like(TimeStamp):
    user    = models.ForeignKey('User', on_delete=models.CASCADE)
    lecture = models.ForeignKey('lectures.Lecture', on_delete=models.CASCADE)

    class Meta:
        db_table = 'likes'