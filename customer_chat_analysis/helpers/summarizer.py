import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use GOOGLE_API_KEY as required by Gemini SDK
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in your environment variables (.env file)")

# Configure the Gemini client with your API key
genai.configure(api_key=API_KEY)

def summarize_conversation(conversation, max_tokens=256):
    """
    Summarize a customer support conversation using the Gemini API.

    Args:
        conversation (str): The entire conversation as text.
        max_tokens (int): Maximum tokens output by Gemini for summary.

    Returns:
        str: Summary text or error message.
    """
    if not conversation or not conversation.strip():
        return "No conversation provided for summarization."

    prompt = (
        "Summarize the following customer support chat conversation concisely:\n"
        f"{conversation}"
    )

    model = genai.GenerativeModel('gemini-2.5-pro')  # Correct and up-to-date model name

    try:
        # Generate the summary using Gemini API
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": max_tokens
            }
        )

        # Debug: print the full raw response to console
        print("Gemini API raw response:", response)

        # Extract the summary text safely from the API response structure
        summary = response.candidates[0].content.parts[0].text.strip()

        if not summary:
            print("Summary was empty after retrieval.")
            return "Summary could not be generated."

        return summary

    except Exception as e:
        # Log error to console for debugging
        print("Exception during Gemini summary generation:", str(e))
        return f"Error generating summary: {str(e)}"
