from rest_framework.response import Response
from rest_framework.views    import APIView

from django.db.models        import Q, Avg, Count
from django.db               import transaction

from core.decorator          import public_decorator, signin_decorator, query_debugger
from core.utils              import get_user_status

from users.models            import Like
from lectures.models         import Lecture, LectureImage, Difficulty, Subcategory
from lectures.serializers    import LectureSerializer, LectureDetailSerializer, LectureLikeSerializer
                                    # LectureCreateSerializer

from core.storage            import FileUpload, s3_client

from clnass505_drf.settings  import (
    BUCKET_DIR_THUMBNAIL,
    BUCKET_DIR_IMAGE,
    BUCKET_DIR_PROFILE 
)


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
    
    @signin_decorator
    def post(self, request):
        try:
            user = request.user

            profile        = request.FILES['profile_image_url']
            thumbnail      = request.FILES['thumbnail_image_url']
            lecture_images = request.FILES.getlist('lecture_images_url')
            
            name           = request.POST['name']
            price          = request.POST['price']
            title          = request.POST['title']
            discount_rate  = request.POST['discount_rate']
            description    = request.POST['description']
            difficulty_id  = request.POST['difficulty_id']
            subcategory_id = request.POST['subcategory_id']
            
            difficulty  = Difficulty.objects.get(id=difficulty_id)
            subcategory = Subcategory.objects.get(id=subcategory_id)
        
            file_handler = FileUpload(s3_client)
            
            with transaction.atomic():
                
                uploaded_profile_image_url = file_handler.upload(profile, BUCKET_DIR_PROFILE)
                user.profile_image_url     = uploaded_profile_image_url
                user.save()
                
                uploaded_thumbnail_url = file_handler.upload(thumbnail, BUCKET_DIR_THUMBNAIL)
                lecture = Lecture.objects.create(
                        name                = name,
                        price               = price,
                        discount_rate       = discount_rate,
                        thumbnail_image_url = uploaded_thumbnail_url,
                        description         = description,
                        user_id             = user.id,
                        difficulty          = difficulty,
                        subcategory         = subcategory
                )
                
                bulk_lecture_images = []
                for idx, lecture_image in enumerate(lecture_images):
                
                    uploaded_lecture_image_url = file_handler.upload(lecture_image, BUCKET_DIR_IMAGE)
                
                    bulk_lecture_images.append(LectureImage(
                        title      = title,
                        image_url  = uploaded_lecture_image_url,
                        sequence   = idx + 1,
                        lecture_id = lecture.id
                    ))
                LectureImage.objects.bulk_create(bulk_lecture_images) 
                
            return Response({'message' : 'new lecture creation success'}, status=201)  
        
        except KeyError:
            return Response({'detail' : 'key error'}, status=400)
        except Difficulty.DoesNotExist as d:
            return Response({'detail' : str(d)}, status=400)
        except Subcategory.DoesNotExist as s:
            return Response({'detail' : str(s)}, status=400)
        except transaction.TransactionManagementError as t:
            return Response({'detail' : str(t)}, status=400)
        
    '''
    def post(self, request):
        serializer = LectureCreateSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.error, status=400)
    '''
    

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
            user    = request.user
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
    @query_debugger
    @signin_decorator
    def get(self, request):
        user  = request.user
        likes = Like.objects\
                    .select_related('lecture__user', 'lecture__subcategory')\
                    .filter(user=user)
        
        serializer = LectureLikeSerializer(likes, many=True)
        return Response(serializer.data, status=200)
    
    @signin_decorator
    def post(self, request, lecture_id):
        try:
            user             = request.user
            lecture          = Lecture.objects.get(id=lecture_id)
            like, is_created = Like.objects.get_or_create(user=user, lecture=lecture)
            
            if not is_created:
                like.delete()
                return Response({'message' : 'like cancel success'}, status=200)
            
            return Response({'message' : 'like success'}, status=201)
        
        except Lecture.DoesNotExist as e:
            return Response({'detail' : str(e)}, status=400)
    

class LectureStudentView(APIView):
    @query_debugger
    @signin_decorator
    def get(self, request):
        user     = request.user
        lectures = user.lectures\
                       .select_related('subcategory', 'user')\
                       .prefetch_related('like_set')\
                       .all()
                       
        serializer = LectureSerializer(lectures, many=True)
        return Response(serializer.data, status=200)      