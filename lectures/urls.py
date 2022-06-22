from django.urls    import path
from lectures.views import LectureDetailView

urlpatterns = [
    path('/<int:lecture_id>', LectureDetailView.as_view()),
]

