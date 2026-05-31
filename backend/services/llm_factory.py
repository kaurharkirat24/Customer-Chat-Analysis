import os
import json
from abc import ABC, abstractmethod
from google import genai

class LLMProvider(ABC):
    @abstractmethod
    def extract_intent_and_sentiment(self, text: str) -> dict:
        pass

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def extract_intent_and_sentiment(self, text: str) -> dict:
        if not self.client:
            raise ValueError("GEMINI_API_KEY not set")
        
        prompt = f"""
        Analyze the following customer service interaction. 
        Extract the sentiment (Positive, Neutral, Negative, Highly Frustrated) 
        and the primary intent (Cancel, Escalation, Feedback, Billing, General Support).
        Return EXACTLY a valid JSON string with keys 'sentiment' and 'intent'.
        
        Text: {text}
        """
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        try:
            cleaned = response.text.strip().strip('```json').strip('```')
            return json.loads(cleaned)
        except Exception:
            return {"sentiment": "Neutral", "intent": "General Support"}


class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        
    def extract_intent_and_sentiment(self, text: str) -> dict:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        # Mock fallback for now, as real integration requires openai client
        return {"sentiment": "Negative", "intent": "Cancel (Mock Fallback)"}


class LLMFactory:
    @staticmethod
    def get_provider() -> LLMProvider:
        # Try Gemini First
        if os.getenv("GEMINI_API_KEY"):
            return GeminiProvider()
        # Fallback to OpenAI
        elif os.getenv("OPENAI_API_KEY"):
            return OpenAIProvider()
        else:
            print("WARNING: No valid LLM API keys found. Using Mock Provider for testing.")
            class MockProvider(LLMProvider):
                def extract_intent_and_sentiment(self, text: str):
                    return {"sentiment": "Negative", "intent": "Escalation"}
            return MockProvider()

def get_llm():
    return LLMFactory.get_provider()
