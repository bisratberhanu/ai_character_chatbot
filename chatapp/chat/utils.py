import google.generativeai as genai
import json
import re
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
import os 

load_dotenv()
# Configure the API key (do this once, typically outside the function)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Your API key


# Initialize SentenceTransformer model for embeddings
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # A lightweight, fast model

# Initialize Chroma client (persistent storage)
chroma_client = chromadb.PersistentClient(path="./chroma_db")  # Store in a local directory



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



def store_book_in_vector_db(book_id, book_text):
    """Store book text in Chroma vector database as 500-line chunks."""
    # Split text into lines
    lines = book_text.splitlines()
    chunk_size = 500
    chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
    
    # Create a unique collection name for this book
    collection_name = f"book_{book_id}_vectors"
    collection = chroma_client.get_or_create_collection(name=collection_name)
    
    # Generate embeddings for each chunk
    chunk_texts = ["\n".join(chunk) for chunk in chunks]
    embeddings = embedder.encode(chunk_texts, convert_to_tensor=False).tolist()
    
    # Store in Chroma
    collection.add(
        documents=chunk_texts,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunk_texts))]
    )
    return collection_name

def get_relevant_context(book_id, query_text, top_k=1):
    """Retrieve the most relevant 500-line chunk from Chroma based on query."""
    collection_name = f"book_{book_id}_vectors"
    try:
        

        collection = chroma_client.get_collection(name=collection_name)
    except Exception:
        print("check message")
        return "No context available for this book."
    
    # Generate embedding for the query
    query_embedding = embedder.encode([query_text], convert_to_tensor=False).tolist()[0]
    
    # Perform similarity search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    # Return the most relevant chunk
    if results["documents"] and results["documents"][0]:
        print("Relevant Context:", results["documents"][0][0])
        return results["documents"][0][0]  # First document from first result
    return "No relevant context found."