from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="books/")

    def __str__(self):
        return self.title

class Character(models.Model):
    name = models.CharField(max_length=255)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="characters")
    context = models.TextField()  # The extracted context
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Conversation(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="conversations")
    user_id = models.CharField(max_length=100)  # No authentication, so store user identifier
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.character.name}"