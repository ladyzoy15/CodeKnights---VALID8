
import os
import sys

# Add the current directory to sys.path to find the app module
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.password_reset_request import PasswordResetRequest
from app.models.user import User

def check():
    db = SessionLocal()
    try:
        requests = db.query(PasswordResetRequest).all()
        print(f"Total Password Reset Requests: {len(requests)}")
        for r in requests:
            user = db.query(User).filter(User.id == r.user_id).first()
            user_email = user.email if user else "Unknown"
            print(f"ID: {r.id}, User: {user_email}, Requested Email: {r.requested_email}, Status: {r.status}, School ID: {r.school_id}")
            
        pending = db.query(PasswordResetRequest).filter(PasswordResetRequest.status == "pending").all()
        print(f"\nPending Requests: {len(pending)}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
