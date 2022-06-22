from typing          import Tuple, Any

from lectures.models import Lecture
from users.models    import UserLecture


def get_lecture_n_check_error(lecture_id, user) -> Tuple[Any, Any, str]:
    if not lecture_id:
        return None, None, 'no lecture id'
    try:
        lecture = Lecture.objects\
                         .select_related('user', 'subcategory')\
                         .prefetch_related('lectureimage_set', 'review_set', 'like_set')\
                         .get(id=lecture_id)
    except Lecture.DoesNotExist:
        return None, None, f'invalid lecture id {lecture_id}'
    
    if UserLecture.objects.filter(user=user, lecture=lecture).exists():
        user_status = 'student'
    if not UserLecture.objects.filter(user=user, lecture=lecture).exists():
        user_status = 'potential_student'
    if lecture.user == user:
        user_status = 'creator'
    if user is None:
        user_status = None
    
    return lecture, user_status, None
    