from django.urls import path
from . import views

urlpatterns = [
    path("", views.cover, name="cover"),
    path("home/", views.home, name="home"),        
    path("learn/", views.learn, name="learn"),
    path("quiz_select/", views.quiz_select, name="quiz_select"),
    path("quiz/", views.quiz, name="quiz"),
    path("stats/", views.stats, name="stats"),
    path("stats/clear/", views.stats_clear, name="stats_clear"),
]
