from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot_questions, name='hot_questions'),
    path('question/<int:question_id>', views.question, name='question'),
    path('tag/<str:tag_name>', views.tag, name='tag'),
    path('ask/', views.ask, name='ask'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/edit/', views.settings, name='settings'),
    path('question/<int:question_id>/feedback', views.question_feedback, name='question_feedback'),
    path('answer/<int:answer_id>/feedback', views.answer_feedback, name='answer_feedback'),
    path('answer/<int:answer_id>/correct', views.correct_feedback, name='correct_feedback'),
]
