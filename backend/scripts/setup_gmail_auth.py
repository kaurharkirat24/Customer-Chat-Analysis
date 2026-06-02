import os.path
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# We need modify scopes to read unread emails and send replies
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def main():
    # Adjust paths so the script can be run from either the root or backend folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credentials_path = os.path.join(base_dir, 'credentials.json')
    token_path = os.path.join(base_dir, 'token.json')
    
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"ERROR: credentials.json not found at {credentials_path}")
                print("Please download it from Google Cloud Console and place it in the backend/ folder.")
                sys.exit(1)
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    print("\n✅ Success! Your token.json has been generated.")
    print("The backend is now fully authenticated with Gmail.")

if __name__ == '__main__':
    main()
