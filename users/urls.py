from django.urls import path
from users.views import KakaoSignInView

urlpatterns = [
    path('/kakao-auth', KakaoSignInView.as_view())
]
