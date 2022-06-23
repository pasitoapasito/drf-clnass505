import jwt, time, functools

from django.db    import connection, reset_queries
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
            return JsonResponse({'message' : 'invalid token'}, status=401)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'invalid user'}, status=401)

        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({'message' : 'expired user'}, status=400)

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
            return JsonResponse({'message' : 'invalid token'}, status=401)

        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({'message' : 'expired token'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'invalid user'}, status=401)

        return func(self, request, *args, **kwargs)

    return wrapper

def query_debugger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()
        number_of_start_queries = len(connection.queries)
        start  = time.perf_counter()
        result = func(*args, **kwargs)
        end    = time.perf_counter()
        number_of_end_queries = len(connection.queries) - 2 if len(connection.queries) else 0
        print(f"-------------------------------------------------------------------")
        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {number_of_end_queries-number_of_start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        print(f"-------------------------------------------------------------------")
        return result
    
    return wrapper