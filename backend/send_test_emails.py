import os
import sys

# Add the backend directory to sys.path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gmail_service import send_email

import tempfile

TARGET_EMAIL = "hkcodes04@gmail.com"

# Create dummy files for attachments
tmp_dir = tempfile.mkdtemp()
receipt_path = os.path.join(tmp_dir, "receipt.pdf")
with open(receipt_path, "w") as f: f.write("Dummy PDF receipt content")

screenshot_path = os.path.join(tmp_dir, "error_screenshot.png")
with open(screenshot_path, "wb") as f: f.write(b"\x89PNG\x0d\x0a\x1a\x0a\x00\x00\x00\x0dIHDR")

csv_path = os.path.join(tmp_dir, "export_data.csv")
with open(csv_path, "w") as f: f.write("id,name,email\n1,John,john@example.com")

TEST_EMAILS = [
    {
        "subject": "Help! I was charged twice for my subscription",
        "content": "Hello,\n\nI just checked my credit card statement and saw that I was billed $49.99 twice this month for my pro subscription. Can you please refund the duplicate charge immediately?\n\nI have attached my receipt.\n\nThanks,\nJohn",
        "attachments": [receipt_path]
    },
    {
        "subject": "URGENT: Suspicious login alert on my account",
        "content": "Hi support,\n\nI just received an alert that someone logged into my account from Russia. I am based in New York and have never been to Russia! Please lock down my account immediately and tell me what to do.\n\nJane",
        "attachments": []
    },
    {
        "subject": "How do I export my data to CSV?",
        "content": "Hi team,\n\nI'm trying to figure out how to export all my customer data into a CSV format. I looked through the docs but couldn't find the exact button. Is this feature available on the basic plan?\n\nI attached an example of what I want.\n\nThanks,\nMark",
        "attachments": [csv_path]
    },
    {
        "subject": "WIN A FREE IPHONE 15 PRO MAX!!!",
        "content": "CONGRATULATIONS!!!\n\nYou have been randomly selected to win a brand new iPhone 15 Pro Max! Click the link below immediately to claim your prize before it expires in 24 hours!\n\nhttp://totally-not-a-scam-link.com/claim\n\nDon't miss out!",
        "attachments": []
    },
    {
        "subject": "I want to cancel my account right now",
        "content": "Your software is incredibly buggy and it just deleted 5 hours of my work. I am so frustrated. Cancel my account immediately and I want a full refund for this month. See the attached screenshot of the crash.\n\nDo not try to convince me otherwise.",
        "attachments": [screenshot_path]
    }
]

def main():
    print(f"Sending {len(TEST_EMAILS)} test emails to {TARGET_EMAIL}...")
    
    success_count = 0
    for idx, email_data in enumerate(TEST_EMAILS, 1):
        try:
            print(f"[{idx}/{len(TEST_EMAILS)}] Sending: '{email_data['subject']}'")
            res = send_email(
                to_address=TARGET_EMAIL,
                subject=email_data['subject'],
                content=email_data['content'],
                attachments=email_data.get('attachments', [])
            )
            if res:
                success_count += 1
                print("   -> Success!")
            else:
                print("   -> Failed.")
        except Exception as e:
            print(f"   -> Error: {e}")
            
    print(f"\nDone! Successfully sent {success_count} out of {len(TEST_EMAILS)} test emails.")

if __name__ == "__main__":
    main()
