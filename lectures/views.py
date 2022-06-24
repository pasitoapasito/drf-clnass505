from rest_framework.response import Response
from rest_framework.views    import APIView

from django.db.models        import Q, Avg, Count

from core.decorator          import public_decorator, signin_decorator, query_debugger
from core.utils              import get_user_status

from users.models            import Like
from lectures.models         import Lecture
from lectures.serializers    import LectureSerializer, LectureDetailSerializer


class LectureListView(APIView):
    @query_debugger
    @public_decorator
    def get(self, request):
        try:
            user = request.user
            
            sort           = request.GET.get('sort', 'new')
            category_id    = request.GET.get('category_id', None)
            subcategory_id = request.GET.get('subcategory_id', None)
            difficulty_id  = request.GET.get('difficulty_id', None)
            search         = request.GET.get('search', None)
            offset         = int(request.GET.get('offset', 0))
            limit          = int(request.GET.get('limit', 16))
        
            sort_set = {
                'liked'       : '-likes',
                'unlike'      : 'likes',
                'best_grade'  : '-star',
                'worst_grade' : 'star',
                'new'         : '-created_at',
                'old'         : 'created_at',
                'high_price'  : '-price',
                'low_price'   : 'price'
            }

            q = Q()

            if category_id:
                q &= Q(subcategory__category_id = category_id)

            if subcategory_id:
                q &= Q(subcategory_id = subcategory_id)

            if difficulty_id:
                q &= Q(difficulty_id__in = difficulty_id)

            if search:
                q &= Q(name__icontains = search)

            lectures = Lecture.objects\
                              .annotate(likes=Count('like'), star=Avg('review__rating'))\
                              .select_related('user', 'subcategory')\
                              .prefetch_related('like_set')\
                              .filter(q)\
                              .order_by(sort_set[sort])[offset : offset+limit]
            
            # TODO user like status
            serializer = LectureSerializer(lectures, many=True)
            return Response(serializer.data, status=200)

        except KeyError:
            return Response({'detail' : 'key error'}, status=400)


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
            user             = request.user
            lecture          = Lecture.objects.get(id=lecture_id)
            like, is_created = Like.objects.get_or_create(user=user, lecture=lecture)
            
            if not is_created:
                like.delete()
                return Response({'message' : 'cancel like'}, status=200)
            
            return Response({'message' : 'success like'}, status=201)
        
        except Lecture.DoesNotExist as e:
            return Response({'detail' : str(e)}, status=400)
        
        
class LectureCreatorView(APIView):
    @query_debugger
    @signin_decorator
    def get(self, request):
        user     = request.user
        lectures = Lecture.objects\
                          .annotate(likes=Count('like'))\
                          .select_related('user', 'subcategory')\
                          .filter(user=user)
        
        serializer = LectureSerializer(lectures, many=True)
        return Response(serializer.data, status=200)