import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """Initializes and returns the Gmail API service object."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    token_path = os.path.join(base_dir, 'token.json')
    
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Gmail token is invalid or missing. Run python scripts/setup_gmail_auth.py first.")
            
    return build('gmail', 'v1', credentials=creds)

def fetch_unread_emails():
    """Fetches unread emails from the inbox and marks them as read."""
    service = get_gmail_service()
    try:
        # Get unread messages in INBOX
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
        messages = results.get('messages', [])
        
        parsed_emails = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            
            # Extract headers (From, Subject)
            headers = msg_data['payload'].get('headers', [])
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            
            # Extract body
            body = ""
            if 'parts' in msg_data['payload']:
                for part in msg_data['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
            else:
                data = msg_data['payload']['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    
            parsed_emails.append({
                "id": msg['id'],
                "sender": sender,
                "subject": subject,
                "body": body
            })
            
            # Mark as read (remove UNREAD label)
            service.users().messages().modify(
                userId='me', id=msg['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
        return parsed_emails
    except HttpError as error:
        print(f"An error occurred fetching emails: {error}")
        return []

def send_email(to_address: str, subject: str, content: str):
    """Sends an email using the Gmail API."""
    service = get_gmail_service()
    try:
        message = EmailMessage()
        message.set_content(content)
        message['To'] = to_address
        message['From'] = 'me'  # Gmail API automatically uses the authenticated user's address
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return send_message
    except HttpError as error:
        print(f"An error occurred sending email: {error}")
        return None
