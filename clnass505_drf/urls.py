from django.urls import path, include

urlpatterns = [
    path('users', include('users.urls')),
    path('lectures', include('lectures.urls')),
]
