from rest_framework.response import Response
from rest_framework.views    import APIView

from core.decorator          import public_decorator, query_debugger
from core.utils              import get_lecture_n_check_error

from lectures.serializers    import LectureDetailSerializer

class LectureDetailView(APIView):
    @query_debugger
    @public_decorator
    def get(self, request, lecture_id):
        user = request.user
        
        lecture, user_status, err = get_lecture_n_check_error(lecture_id, user)
        if err:
            return Response({'detail' : err}, status=400)
        
        user_data = {
            'user_name'   : user.name if user else None,
            'user_email'  : user.email if user else None,
            'user_status' : user_status
        }
        like_data = {
            'likes'    : lecture.like_set.count(),
            'is_liked' : lecture.like_set.filter(user=user).exists()
        }
        data = {
            'lecture_detail' : LectureDetailSerializer(lecture).data
        }
        data['lecture_detail'].update(user_data)
        data['lecture_detail'].update(like_data)
        
        return Response(data, status=200)
          


