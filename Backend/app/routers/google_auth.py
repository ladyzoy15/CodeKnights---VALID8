from fastapi import APIRouter, Depends, HTTPException, Request
import logging

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.auth import Token, GoogleLoginRequest
from app.services.google_auth_service import verify_google_id_token, GoogleAuthError
from app.services.auth_session import issue_login_token_response
from app.models.user import User, UserRole
from app.models.role import Role
from app.models.school import School
from app.services.security_service import record_login_history
import secrets

router = APIRouter(tags=["authentication"])

@router.post("/auth/google", response_model=Token)
async def login_with_google(
    request: Request,
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    try:
        google_payload = verify_google_id_token(payload.id_token)
    except GoogleAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    email = google_payload["email"]
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # If user is new and hasn't provided a school_id yet, return onboarding flag
        if not payload.school_id:
            return Token(
                email=email,
                first_name=google_payload.get("given_name"),
                last_name=google_payload.get("family_name"),
                needs_onboarding=True
            )
        
        # User is new and has provided a school_id, proceed with registration
        user = User(
            email=email,
            first_name=google_payload.get("given_name"),
            last_name=google_payload.get("family_name"),
            is_active=True,
            must_change_password=False,
            school_id=payload.school_id
        )
        user.set_password(secrets.token_urlsafe(16))
        db.add(user)
        db.flush()

        # Assign 'student' role
        student_role = db.query(Role).filter(Role.code.ilike("student")).first()
        if student_role:
            db.add(UserRole(user_id=user.id, role_id=student_role.id))
        
        logger.info(f"Registered new Google user {email} for school {payload.school_id}")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled.")

    response_payload = issue_login_token_response(
        db=db,
        user=user,
        request=request,
        remember_me=True,
    )

    record_login_history(
        db,
        email_attempted=user.email,
        user=user,
        success=True,
        auth_method="google",
        request=request,
    )
    db.commit()

    return response_payload
