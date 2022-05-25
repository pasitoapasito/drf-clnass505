import jwt

from django.conf  import settings
from django.http  import JsonResponse

from users.models import User

def signin_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            payload      = jwt.decode(access_token, settings.SECRET_KEY, settings.ALGORITHM)
            user         = User.objects.get(id=payload['user_id'])
            request.user = user

        except jwt.exceptions.DecodeError:
            return JsonResponse({'message' : 'INVALID_TOKEN'}, status=401)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_USER'}, status=401)

        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({'message' : 'EXPIRED_TOKEN'}, status=400)

        return func(self, request, *args, **kwargs)

    return wrapper

def public_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            request.user = None

            if access_token:
                payload      = jwt.decode(access_token, settings.SECRET_KEY, settings.ALGORITHM)
                user         = User.objects.get(id=payload['user_id'])
                request.user = user

        except jwt.exceptions.DecodeError:
            return JsonResponse({'message' : 'INVALID_TOKEN'}, status=401)

        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({'message' : 'EXPIRED_TOKEN'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_USER'}, status=401)

        return func(self, request, *args, **kwargs)

    return wrapper