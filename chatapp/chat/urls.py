from django.urls import path
from .views import (
    upload_and_chat_view,
    from_other_users_characters_view,
    upload_book_api,
    list_characters_api,
    chat_with_character_api,
    home_view
)
from . import views

urlpatterns = [
    path('', home_view, name='home'),
    path('auth/', views.auth_view, name='auth'),  # New signup/login page
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("upload_and_chat/", upload_and_chat_view, name="upload_and_chat"),
    path("from_other_users_characters/", from_other_users_characters_view, name="from_other_users_characters"),
    path("api/upload_book/", upload_book_api, name="upload_book_api"),
    path("api/characters/", list_characters_api, name="list_characters_api"),
    path("api/chat/", chat_with_character_api, name="chat_with_character_api"),
    path('api/clear_session/', views.clear_session_api, name='clear_session_api'),
]