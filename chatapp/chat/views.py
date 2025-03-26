from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Book, Character, Conversation
from .utils import extract_characters
import google.generativeai as genai
import json

genai.configure(api_key="AIzaSyAwuj2Rh3GjdjZAzrsWMdDrzcTZmFzGyuw")  # Replace with your actual API key

def home_view(request):
    return render(request, 'chat/home.html')

def upload_and_chat_view(request):
    """Render the upload and chat page."""
    return render(request, "chat/upload_and_chat.html")

def from_other_users_characters_view(request):
    """Render the page to chat with existing characters."""
    return render(request, "chat/from_other_users_characters.html")

@csrf_exempt
def upload_book_api(request):
    """Handle book upload, extract characters, and save them to the database."""
    if request.method == "POST":
        uploaded_file = request.FILES.get("book")
        if not uploaded_file:
            return JsonResponse({"success": False, "error": "No file provided."})

        try:
            book_text = uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError:
            return JsonResponse({"success": False, "error": "File must be a valid text file."})

        characters = extract_characters(book_text)
        if not characters:
            return JsonResponse({"success": False, "error": "No characters found in the book."})

        # Save the book and characters
        book = Book.objects.create(title=uploaded_file.name, file=uploaded_file)
        character_objects = []
        for name in characters:
            character_obj = Character.objects.create(
                name=name,
                book=book,
                context=book_text[:500]  # Store first 500 characters as context
            )
            character_objects.append({"id": character_obj.id, "name": character_obj.name})

        return JsonResponse({
            "success": True,
            "book_id": book.id,
            "characters": character_objects
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})

def list_characters_api(request):
    """Return a list of all characters in the database."""
    if request.method == "GET":
        characters = Character.objects.all().values("id", "name", "book__title")
        return JsonResponse({"success": True, "characters": list(characters)})
    return JsonResponse({"success": False, "error": "Invalid request method."})

@csrf_exempt
def chat_with_character_api(request):
    """Handle chat interactions with a selected character."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            character_id = data.get("character_id")
            user_message = data.get("message")
            user_id = data.get("user_id", "anonymous")
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid request data."})

        if not character_id or not user_message:
            return JsonResponse({"success": False, "error": "Character ID and message are required."})

        character = get_object_or_404(Character, id=character_id)

        prompt = (
            f"You are {character.name} from {character.book.title}. "
            f"Based on the provided context:\n{character.context}\n"
            f"Respond to: {user_message}"
        )

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')

            response = model.generate_content(prompt)
            response_text = response.text if hasattr(response, "text") else "No response generated."
        except Exception as e:
            return JsonResponse({"success": False, "error": f"AI error: {str(e)}"})

        # Save the conversation
        conversation = Conversation.objects.create(
            character=character,
            user_id=user_id,
            message=user_message,
            response=response_text
        )

        return JsonResponse({"success": True, "response": response_text})
    return JsonResponse({"success": False, "error": "Invalid request method."})