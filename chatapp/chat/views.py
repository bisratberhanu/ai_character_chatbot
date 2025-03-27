# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Book, Character, Conversation
from .utils import extract_characters, store_book_in_vector_db, get_relevant_context
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Replace with your actual API key


def auth_view(request):
    """Render the signup/login page."""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'chat/auth.html')


@csrf_exempt
def signup_view(request):
    """Handle user signup."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            if not username or not password:
                return JsonResponse({"success": False, "error": "Username and password are required."})
            if User.objects.filter(username=username).exists():
                return JsonResponse({"success": False, "error": "Username already exists."})
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method."})

@csrf_exempt
def login_view(request):
    """Handle user login."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "Invalid username or password."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method."})

def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('auth')


@login_required
def home_view(request):
    return render(request, 'chat/home.html')


@login_required
def upload_and_chat_view(request):
    """Render the upload and chat page."""
    return render(request, "chat/upload_and_chat.html")


@login_required
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

        if Book.objects.filter(title=uploaded_file.name).exists():
            return JsonResponse({
                "success": False,
                "error": "This book is already registered. You can chat with its characters from the 'List Characters' page."
            })

        file_extension = uploaded_file.name.lower().split('.')[-1]
        if file_extension not in ['txt', 'pdf']:
            return JsonResponse({"success": False, "error": "File must be a .txt or .pdf file."})

        try:
            if file_extension == 'txt':
                book_text = uploaded_file.read().decode("utf-8")
            elif file_extension == 'pdf':
                from PyPDF2 import PdfReader
                pdf_reader = PdfReader(uploaded_file)
                book_text = ""
                for page in pdf_reader.pages:
                    book_text += page.extract_text() or ""
                if not book_text.strip():
                    return JsonResponse({"success": False, "error": "No readable text found in the PDF."})
        except UnicodeDecodeError:
            return JsonResponse({"success": False, "error": "Text file must be a valid UTF-8 encoded file."})
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Error processing file: {str(e)}"})

        characters = extract_characters(book_text)
        if not characters:
            return JsonResponse({"success": False, "error": "No characters found in the book."})

        # Save the book and store in vector DB
        book = Book.objects.create(title=uploaded_file.name, file=uploaded_file)
        collection_name = store_book_in_vector_db(book.id, book_text)
        book.vector_collection_name = collection_name  # Optional: Save the collection name
        book.save()

        character_objects = []
        for name in characters:
            character_obj = Character.objects.create(
                name=name,
                book=book,
                context=""  # No static context; we'll fetch dynamically
            )
            character_objects.append({"id": character_obj.id, "name": character_obj.name})

        return JsonResponse({
            "success": True,
            "book_id": book.id,
            "characters": character_objects
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})






@login_required
def list_characters_api(request):
    """Return a list of all characters in the database."""
    if request.method == "GET":
        characters = Character.objects.all().values("id", "name", "book__title")
        return JsonResponse({"success": True, "characters": list(characters)})
    return JsonResponse({"success": False, "error": "Invalid request method."})

@csrf_exempt
@login_required
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

        # Verify API key is loaded
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return JsonResponse({"success": False, "error": "Google API key not configured."})
        # print("API Key Loaded:", bool(api_key))  # Debugging: Confirm API key presence

        # Load conversation history from session
        history_key = f'conversation_history_{character_id}'
        conversation_history = request.session.get(history_key, [])
        conversation_history.append({'role': 'user', 'content': user_message})

        # Format history as a string for the prompt
        history_str = ""
        for entry in conversation_history:
            if entry['role'] == 'user':
                history_str += f"User: {entry['content']}\n"
            elif entry['role'] == 'model':
                history_str += f"Character: {entry['content']}\n"
        # print("Conversation History:", history_str)  # Debugging: Inspect history

        # Get relevant context from vector DB
        context = get_relevant_context(character.book.id, user_message)
        print("Context Retrieved:", context)  # Debugging: Check context

        # Define the prompt template using LangChain
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "You are {character_name} from {book_title}.\n"
                "Based on the provided context:\n{context}\n\n"
                "Here is the conversation so far:\n{history}\n"
                "Now, respond to the latest user message: {user_message}\n\n"
                "After your response, on a new line, provide the emotion levels for the following five emotions on a scale of 1 to 5 "
                "(where 1 is the lowest and 5 is the highest, no values below 1 or above 5). "
                "Format the emotion levels as a JSON object enclosed in ```json and ``` markers, e.g.,\n"
                "```\nYour response here.\n```\n```json\n{{\"Anger\": 3, \"Sadness\": 2, \"Pride\": 4, \"Joy\": 5, \"Bliss\": 1}}\n```"
            )),
            ("human", "{user_message}")
        ])

        # Format the prompt with the actual values
        try:
            formatted_prompt = prompt_template.format_messages(
                character_name=character.name,
                book_title=character.book.title,
                context=context,
                history=history_str,
                user_message=user_message
            )
            # print("Formatted Prompt:", formatted_prompt)  # Debugging: Inspect prompt
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Prompt formatting error: {str(e)}"})

        try:
            # Use LangChain to generate the response
            llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Specify the model you’re using
            google_api_key=os.getenv("GOOGLE_API_KEY"),  # Your API key from environment variables
    temperature=0.7  # Controls randomness; adjust as needed
)
            response = llm.invoke(formatted_prompt)
            full_response = response.content.strip()
            # print("Full Response:", full_response)  # Debugging: Inspect raw response

            # Parse the response to extract text and emotion levels
            if "```json" in full_response:
                response_text, json_part = full_response.split("```json", 1)
                emotion_json = json_part.split("```")[0].strip()
                emotion_levels = json.loads(emotion_json)
            else:
                # Fallback parsing if JSON markers are missing
                try:
                    json_start = full_response.rfind("{")
                    json_end = full_response.rfind("}") + 1
                    if json_start != -1 and json_end != -1:
                        response_text = full_response[:json_start].strip()
                        emotion_json = full_response[json_start:json_end]
                        emotion_levels = json.loads(emotion_json)
                    else:
                        response_text = full_response
                        emotion_levels = {"Anger": 1, "Sadness": 1, "Pride": 1, "Joy": 1, "Bliss": 1}
                except json.JSONDecodeError:
                    response_text = full_response
                    emotion_levels = {"Anger": 1, "Sadness": 1, "Pride": 1, "Joy": 1, "Bliss": 1}

            # Ensure emotion levels are within the valid range (1-5)
            for emotion in emotion_levels:
                emotion_levels[emotion] = max(1, min(5, int(emotion_levels[emotion])))
        except Exception as e:
            print("AI Invocation Error:", str(e))  # Debugging: Log specific error
            return JsonResponse({"success": False, "error": f"AI error: {str(e)}"})

        # Update conversation history in session
        conversation_history.append({'role': 'model', 'content': response_text})
        request.session[history_key] = conversation_history

        # Save the conversation to the database
        Conversation.objects.create(
            character=character,
            user_id=user_id,
            message=user_message,
            response=response_text
        )

        return JsonResponse({
            "success": True,
            "response": response_text,
            "emotions": emotion_levels
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})



@csrf_exempt
def clear_session_api(request):
    if request.method == "POST":
        try:
            keys_to_clear = [key for key in request.session.keys() if key.startswith('conversation_history_')]
            for key in keys_to_clear:
                del request.session[key]
            request.session.modified = True
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method."})