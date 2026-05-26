
import os
import sys

# Add the current directory to sys.path to find the app module
sys.path.append(os.getcwd())

from app.services.email_service import send_welcome_email
from app.core.config import get_settings

def run():
    recipient = "joyborjacom6@gmail.com"
    temp_pass = "Welcome@Nexus2026"
    
    print(f"Sending Welcome Email to {recipient}...")
    
    try:
        send_welcome_email(
            recipient_email=recipient,
            temporary_password=temp_pass,
            first_name="Joy",
            system_name="Nexus Web"
        )
        print("\nSUCCESS! Welcome email sent successfully.")
    except Exception as e:
        print(f"\nFAILED to send email: {e}")

if __name__ == "__main__":
    run()
