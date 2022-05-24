import requests, jwt

from datetime                   import datetime, timedelta

from django.views               import View
from django.http                import JsonResponse
from django.conf                import settings

from users.models               import User

class KakaoSignInView(View):
    def get(self, request):
        try:
            kakao_token = request.headers.get('Authorization')
            headers     = {'Authorization' : f'Bearer {kakao_token}'}
            response    = requests.get('https://kapi.kakao.com/v2/user/me', headers=headers, timeout=3)
            kakao_user  = response.json()
            
            if kakao_user.get('code') == -401:
                return JsonResponse({'message' : 'INVALID_TOKEN'}, status=401)
            
            kakao_id = kakao_user['id']
            email    = kakao_user['kakao_account']['email']
            name     = kakao_user['kakao_account']['profile']['nickname']
            
            user, is_created = User.objects.get_or_create(
                kakao_id = kakao_id,
                defaults = {'email' : email, 'name' : name}
            )
            
            access_token = jwt.encode({'user_id' : user.id, 'exp': datetime.utcnow() + timedelta(hours=24)}, settings.SECRET_KEY, settings.ALGORITHM)
            status       = 201 if is_created else 200
            
            return JsonResponse({'message' : 'SUCCESS', 'access_token' : access_token}, status=status)
        
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)
        
        except requests.exceptions.Timeout:
            return JsonResponse({'message' : 'TIME_OUT_ERROR'}, status=408)