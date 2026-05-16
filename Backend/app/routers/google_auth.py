from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.auth import Token, GoogleLoginRequest
from app.services.google_auth_service import verify_google_id_token, GoogleAuthError
from app.services.auth_session import issue_login_token_response
from app.models.user import User
from app.services.security_service import record_login_history

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
        raise HTTPException(
            status_code=404,
            detail="Account not found. Please register through your administrator first."
        )

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
