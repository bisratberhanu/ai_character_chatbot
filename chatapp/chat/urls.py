from django.urls import path
from .views import (
    upload_and_chat_view,
    from_other_users_characters_view,
    upload_book_api,
    list_characters_api,
    chat_with_character_api,
    home_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path("upload_and_chat/", upload_and_chat_view, name="upload_and_chat"),
    path("from_other_users_characters/", from_other_users_characters_view, name="from_other_users_characters"),
    path("api/upload_book/", upload_book_api, name="upload_book_api"),
    path("api/characters/", list_characters_api, name="list_characters_api"),
    path("api/chat/", chat_with_character_api, name="chat_with_character_api"),
]