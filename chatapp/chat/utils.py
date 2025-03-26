import google.generativeai as genai
import json
import re

# Configure the API key (do this once, typically outside the function)
genai.configure(api_key="AIzaSyAwuj2Rh3GjdjZAzrsWMdDrzcTZmFzGyuw")  # Your API key

def extract_characters(book_text):
    """
    Extract characters from a given book text using Google Generative AI.
    Returns a list of character names.
    """
    prompt = (
        "Identify all character names in the following text and return them as a JSON array of strings. "
        "For example, if the text is 'Harry met Sally', return ['Harry', 'Sally']. "
        "Text:\n\n" + book_text
    )
    try:
        print("Extracting characters...")
        # Create a GenerativeModel instance with a valid model name
        model = genai.GenerativeModel('gemini-1.5-flash')  # Use a supported model
        # Generate content using the correct method
        response = model.generate_content(prompt)
        # Access the generated text
        raw_text = response.text
        print("AI Response:", raw_text)
        
        # Strip Markdown code block markers if present
        cleaned_text = re.sub(r'```json\s*|\s*```', '', raw_text, flags=re.DOTALL).strip()
        print("Cleaned Response:", cleaned_text)
        
        # Parse the cleaned JSON
        characters = json.loads(cleaned_text)
        # Clean up the character list
        return [name.strip() for name in characters if isinstance(name, str) and name.strip()]
    except json.JSONDecodeError:
        print("Response is not valid JSON even after cleaning.")
        print("Cleaned Response for debugging:", cleaned_text)
        return []
    except Exception as e:
        print(f"Error extracting characters: {e}")
        return []

# # Test the function
# if __name__ == "__main__":
#     book_text = "there are two characters in this thing, the first one is Bisrat and the second iis melake, melake is an angry person"
#     characters = extract_characters(book_text)
#     print("Extracted Characters:", characters)