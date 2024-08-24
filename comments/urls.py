from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('index/<int:user_id>', views.index, name='index'),
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
