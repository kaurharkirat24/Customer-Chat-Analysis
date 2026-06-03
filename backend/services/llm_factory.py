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

    def extract_intent_and_sentiment(self, text: str, attachments: list = None) -> dict:
        if not self.client:
            raise ValueError("GEMINI_API_KEY not set")
            
        uploaded_files = []
        if attachments:
            import tempfile
            from services.security_service import get_s3_client
            
            s3_client = get_s3_client()
            bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
            
            for att in attachments:
                s3_key = att.get("s3_key")
                if s3_key and bucket_name:
                    tmp_path = None
                    try:
                        # Download to a temporary file
                        suffix = os.path.splitext(att.get("filename", ""))[1]
                        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                            tmp_path = tmp_file.name
                            
                        s3_client.download_file(bucket_name, s3_key, tmp_path)
                        
                        # Upload to Gemini
                        gemini_file = self.client.files.upload(file=tmp_path, mime_type=att.get("file_type"))
                        uploaded_files.append(gemini_file)
                    except Exception as e:
                        print(f"Failed to process attachment for Gemini: {e}")
                    finally:
                        if tmp_path and os.path.exists(tmp_path):
                            try:
                                os.remove(tmp_path)
                            except Exception as e:
                                print(f"Warning: Failed to clean up temp file {tmp_path}: {e}")
        
        prompt = f"""
        Analyze the following customer service interaction with an Enterprise-grade lens.
        Extract the following data points into EXACTLY a valid JSON string:
        
        1. 'intent': One of [Cancel, Downgrade, Refund, Escalation, Feedback, Billing, Security, Compliance, General Support]
        2. 'sentiment': One of [Positive, Neutral, Negative, Highly Frustrated]
        3. 'confidence': A float between 0.0 and 1.0 representing your confidence in the intent mapping.
        4. 'priority': Map to one of [P0, P1, P2, P3]. 
           - P0 = Security/Compliance/Data Breach
           - P1 = Escalation/High Churn/Highly Frustrated
           - P2 = Standard Billing/Refunds/Cancel
           - P3 = Normal Support/Feedback
        5. 'feature': A short 1-3 word tag describing the product feature mentioned (e.g., 'CSV Import', 'Login Flow'). If none, return null.

        Text: {text}
        """
        
        contents = [prompt]
        if uploaded_files:
            contents.extend(uploaded_files)
            
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
        )
        cleaned = response.text.strip().strip('```json').strip('```')
        return json.loads(cleaned)

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
        # Strict enforcement: Fail loudly if no API keys are present
        if os.getenv("GEMINI_API_KEY"):
            return GeminiProvider()
        elif os.getenv("OPENAI_API_KEY"):
            return OpenAIProvider()
        else:
            raise EnvironmentError("CRITICAL: No valid LLM API keys found. Enterprise pipeline requires valid AI credentials.")

def get_llm():
    return LLMFactory.get_provider()
