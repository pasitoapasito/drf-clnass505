from rest_framework.response import Response
from rest_framework.views    import APIView

from core.decorator          import public_decorator, signin_decorator, query_debugger
from core.utils              import get_user_status

from users.models            import Like
from lectures.models         import Lecture
from lectures.serializers    import LectureDetailSerializer

class LectureDetailView(APIView):
    @query_debugger
    @public_decorator
    def get(self, request, lecture_id):
        try:
            user = request.user
            
            lecture = Lecture.objects\
                            .select_related('user', 'subcategory')\
                            .prefetch_related('lectureimage_set', 'review_set', 'like_set')\
                            .get(id=lecture_id)
            
            user_status = get_user_status(lecture, user)
            
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
        
        except Lecture.DoesNotExist as e:
            return Response({'detail' : str(e)}, status=400)


class LectureLikeView(APIView):
    @signin_decorator
    def post(self, request, lecture_id):
        try:
            user = request.user
            lecture = Lecture.objects.get(id=lecture_id)
            like, is_created = Like.objects.get_or_create(user=user, lecture=lecture)
            
            if not is_created:
                like.delete()
                return Response({'message' : 'cancel like'}, status=200)
            
            return Response({'message' : 'success like'}, status=201)
        
        except Lecture.DoesNotExist as e:
            return Response({'detail' : str(e)}, status=400)


