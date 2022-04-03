
from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('sign_up', views.register, name='register'),

    path('login', views.login, name='login'),
    # ex: /polls/5/
    path('<int:user_id>/', views.profile, name='profile'),
]