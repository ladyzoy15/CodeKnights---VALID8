
import os
import sys

# Add the current directory to sys.path to find the app module
sys.path.append(os.getcwd())

from app.services.email_service import send_test_email
from app.core.config import get_settings

def run_test():
    settings = get_settings()
    print(f"Testing email configuration...")
    print(f"Transport: {settings.email_transport}")
    print(f"SMTP Host: {settings.smtp_host}")
    print(f"Sender: {settings.email_sender_email}")
    
    recipient = "nexuscodeknights@gmail.com"  # Sending to self as a test
    print(f"Sending test email to {recipient}...")
    
    try:
        send_test_email(recipient_email=recipient)
        print("\nSUCCESS! Test email sent successfully.")
        print("Please check the inbox of nexuscodeknights@gmail.com.")
    except Exception as e:
        print(f"\nFAILED to send email: {e}")

if __name__ == "__main__":
    run_test()
