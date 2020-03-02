from django.urls import path

from user import views


app_name = 'user'


urlpatterns = [
    path('create/', views.CreateUserAPI.as_view(), name='create'),
    path('token/', views.CreateTokenAPI.as_view(), name='token'),
    path('me/', views.ManageUserAPI.as_view(), name='me'),
]
