from typing          import Any

from users.models    import UserLecture


def get_user_status(lecture, user) -> Any:
    
    if UserLecture.objects.filter(user=user, lecture=lecture).exists():
        user_status = 'student'
    if not UserLecture.objects.filter(user=user, lecture=lecture).exists():
        user_status = 'potential_student'
    if lecture.user == user:
        user_status = 'creator'
    if user is None:
        user_status = None
    
    return user_status