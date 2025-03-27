# AI Character Chatbot

## Overview

The AI Character Chatbot is a project designed to simulate engaging and contextually relevant conversations with various characters. The project is organized into a modular structure to ensure maintainability and scalability. Each folder and file serves a specific purpose, such as handling AI logic, managing user interactions, or storing data. Below is a detailed breakdown of the file structure to help you navigate and understand the project.


## Features
- The app has the features of login and signup
- a user can upload a book or a pdf.
- The user can then interact with all characters in the book or pdf.
- The AI character can then change its emotional level based.
- Other user can also access other users uploaded books and interact with the characters in the book.  

## File Structure


## How to Run

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd ai_character_chatbot
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:

   ```bash
    python manage.py runserver
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:8000`.

## How the Application Works

The AI Character Chatbot is designed to simulate conversations with various characters. Here's how it works:

1. **Input Processing**: The user inputs a message through the interface.
2. **AI Model**: The input is processed by an AI model (Google Gemini) to generate a response.
3. **Response Generation**: The AI generates a contextually relevant response based on the character's personality and the conversation history.
4. **Output Display**: The response is displayed in the chat interface for the user.
