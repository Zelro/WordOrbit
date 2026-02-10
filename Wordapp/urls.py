# ==================== Wordapp/urls.py ====================

from django.urls import path
from . import views

urlpatterns = [
    # Home and main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Game pages
    path('play/', views.game_play, name='game_play'),
    path('check-word/', views.check_word, name='check_word'),
    path('end-game/', views.end_game, name='end_game'),
    path('results/', views.game_results, name='game_results'),

    # User pages
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),

    # Contact and feedback
    path('contact/', views.contact, name='contact'),
    path('feedback/', views.feedback, name='feedback'),
]
