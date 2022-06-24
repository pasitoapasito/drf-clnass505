from django.urls    import path
from lectures.views import LectureListView, LectureDetailView, LectureLikeView

urlpatterns = [
    path('', LectureListView.as_view()),
    path('/<int:lecture_id>', LectureDetailView.as_view()),
    path('/<int:lecture_id>/like', LectureLikeView.as_view()),
]

