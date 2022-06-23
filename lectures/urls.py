from django.urls    import path
from lectures.views import LectureDetailView, LectureLikeView

urlpatterns = [
    path('/<int:lecture_id>', LectureDetailView.as_view()),
    path('/<int:lecture_id>/like', LectureLikeView.as_view()),
]

