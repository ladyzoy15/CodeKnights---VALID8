"""Use: Handles login and authentication API endpoints.
Where to use: Use this through the FastAPI app when the frontend or an API client needs login and authentication features.
Role: Router layer. It receives HTTP requests, checks access rules, and returns API responses.
"""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.core.timezones import utc_now
from app.core.rate_limit import (
    build_forgot_password_rule,
    build_login_rule,
    client_ip_identity,
    enforce_rate_limit,
)
from app.core.security import (
    PASSWORD_CHANGE_PROMPT_DISMISS_ENDPOINT,
    authenticate_user,
    get_current_admin_or_campus_admin,
    get_current_application_user,
    has_any_role,
    verify_password,
)
from app.core.dependencies import get_db
from app.schemas.auth import ChangePasswordRequest, Token, LoginRequest
from app.schemas.google_auth import GoogleLoginRequest
from app.services.google_auth_service import (
    GoogleAuthDisabledError,
    GoogleAuthInvalidTokenError,
    GoogleEmailNotVerifiedError,
    verify_google_id_token,
)
from app.schemas.common import MessageResponse
from app.schemas.password_reset import (
    ForgotPasswordRequestCreate,
    ForgotPasswordRequestResponse,
    PasswordResetApprovalResponse,
    PasswordResetRequestItem,
    ResetPasswordConfirm,
)
from app.models.password_reset_request import PasswordResetRequest
from app.models.school import School
from app.models.user import User, UserRole
from app.services.email_service import EmailDeliveryError, send_password_reset_email
from app.services.auth_session import (
    issue_login_token_response,
    validate_login_account_state,
)
from app.services.notification_center_service import send_account_security_notification
from app.services.password_change_policy import must_change_password_for_temporary_reset
from app.services.security_service import (
    record_login_history,
)
from app.utils.passwords import generate_secure_password
from app.utils.security_utils import generate_reset_token, hash_token, get_token_expiry

router = APIRouter(tags=["authentication"])
FORGOT_PASSWORD_GENERIC_MESSAGE = (
    "If the account exists, a password reset request has been submitted for administrator approval."
)


def _is_platform_admin_account(user: User | None) -> bool:
    return bool(user) and has_any_role(user, ["admin"]) and getattr(user, "school_id", None) is None


def _requires_platform_admin_password_reset_approval(user: User | None) -> bool:
    return bool(user) and has_any_role(user, ["admin", "campus_admin"])


def _can_submit_public_password_reset_request(user: User | None) -> bool:
    if user is None or not getattr(user, "is_active", True):
        return False
    if getattr(user, "school_id", None) is None:
        return False
    return not _is_platform_admin_account(user)


def _login_rate_limit_identity(request: Request, email: str) -> str:
    return f"{client_ip_identity(request)}:email:{email.strip().lower()}"


def _try_commit(db: Session) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()


def _try_record_login_history(db: Session, **kwargs) -> None:
    try:
        record_login_history(db, **kwargs)
    except Exception:
        db.rollback()


@router.post("/token", response_model=Token)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember_me: bool = Form(default=False),
    db: Session = Depends(get_db)
):
    """OAuth2-compatible token endpoint (for Swagger UI)"""
    enforce_rate_limit(
        build_login_rule(),
        _login_rate_limit_identity(request, form_data.username),
        request=request,
    )
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        _try_record_login_history(
            db,
            email_attempted=form_data.username,
            user=None,
            success=False,
            auth_method="password",
            failure_reason="invalid_credentials",
            request=request,
        )
        _try_commit(db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    validate_login_account_state(db, user)

    response_payload = issue_login_token_response(
        db=db,
        user=user,
        request=request,
        remember_me=remember_me,
    )
    _try_record_login_history(
        db,
        email_attempted=user.email,
        user=user,
        success=True,
        auth_method="password",
        request=request,
    )
    _try_commit(db)
    return response_payload

@router.post("/login", response_model=Token)
def login_with_email(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Alternative login endpoint that returns extended user info"""
    enforce_rate_limit(
        build_login_rule(),
        _login_rate_limit_identity(request, login_data.email),
        request=request,
    )
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        _try_record_login_history(
            db,
            email_attempted=login_data.email,
            user=None,
            success=False,
            auth_method="password",
            failure_reason="invalid_credentials",
            request=request,
        )
        _try_commit(db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    validate_login_account_state(db, user)

    response_payload = issue_login_token_response(
        db=db,
        user=user,
        request=request,
        remember_me=login_data.remember_me,
        platform=login_data.platform,
    )
    _try_record_login_history(
        db,
        email_attempted=user.email,
        user=user,
        success=True,
        auth_method="password",
        request=request,
    )

    _try_commit(db)
    return response_payload


@router.post("/auth/google", response_model=Token)
def login_with_google(
    request: Request,
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db),
):
    """Verify a Google ID token and issue an access token for a registered user."""
    enforce_rate_limit(
        build_login_rule(),
        f"{client_ip_identity(request)}:google",
        request=request,
    )

    try:
        google_payload = verify_google_id_token(payload.id_token)
    except GoogleAuthDisabledError:
        record_login_history(
            db,
            email_attempted="",
            user=None,
            success=False,
            auth_method="google",
            failure_reason="google_login_disabled",
            request=request,
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Google login is disabled.")
    except GoogleEmailNotVerifiedError:
        record_login_history(
            db,
            email_attempted="",
            user=None,
            success=False,
            auth_method="google",
            failure_reason="email_not_verified",
            request=request,
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google email is not verified.")
    except GoogleAuthInvalidTokenError:
        record_login_history(
            db,
            email_attempted="",
            user=None,
            success=False,
            auth_method="google",
            failure_reason="invalid_token",
            request=request,
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token.")

    email = google_payload["email"]

    user = (
        db.query(User)
        .options(joinedload(User.roles).joinedload(UserRole.role))
        .filter(User.email == email)
        .first()
    )
    if user is None:
        record_login_history(
            db,
            email_attempted=email,
            user=None,
            success=False,
            auth_method="google",
            failure_reason="not_registered",
            request=request,
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Google account is not registered.")

    validate_login_account_state(db, user)

    response_payload = issue_login_token_response(
        db=db,
        user=user,
        request=request,
        remember_me=False,
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


@router.post("/auth/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_application_user),
    db: Session = Depends(get_db),
):
    # Use the same verifier as login so temporary passwords work consistently
    # regardless of which hashing helper originally created the stored hash.
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.set_password(payload.new_password)
    current_user.must_change_password = False
    current_user.should_prompt_password_change = False
    try:
        send_account_security_notification(
            db,
            user=current_user,
            subject="Password Changed",
            message="Your password was changed successfully.",
            metadata_json={"event": "password_change"},
        )
    except Exception:
        pass
    db.commit()

    return {"message": "Password updated successfully"}


@router.post(PASSWORD_CHANGE_PROMPT_DISMISS_ENDPOINT, response_model=MessageResponse)
def dismiss_password_change_prompt(
    current_user: User = Depends(get_current_application_user),
    db: Session = Depends(get_db),
):
    current_user.should_prompt_password_change = False
    db.commit()
    return {"message": "Password change prompt dismissed."}


@router.post("/auth/forgot-password", response_model=ForgotPasswordRequestResponse)
def request_forgot_password(
    request: Request,
    payload: ForgotPasswordRequestCreate,
    db: Session = Depends(get_db),
):
    normalized_email = payload.email.strip().lower()
    enforce_rate_limit(
        build_forgot_password_rule(),
        _login_rate_limit_identity(request, normalized_email),
        request=request,
    )
    target_user = (
        db.query(User)
        .options(joinedload(User.roles).joinedload(UserRole.role))
        .filter(User.email == normalized_email)
        .first()
    )

    if not target_user:
        return ForgotPasswordRequestResponse(message=FORGOT_PASSWORD_GENERIC_MESSAGE)

    if not _can_submit_public_password_reset_request(target_user):
        return ForgotPasswordRequestResponse(message=FORGOT_PASSWORD_GENERIC_MESSAGE)

    # 1. Determine if this user requires manual administrative approval.
    requires_approval = _requires_platform_admin_password_reset_approval(target_user)

    if not requires_approval:
        # AUTOMATIC RESET FLOW for Students
        reset_token = generate_reset_token()
        token_hash = hash_token(reset_token)
        expires_at = get_token_expiry(hours=2)

        # Record as an auto-approved request
        db.add(
            PasswordResetRequest(
                user_id=target_user.id,
                school_id=target_user.school_id,
                requested_email=target_user.email.lower(),
                status="approved",
                token_hash=token_hash,
                expires_at=expires_at,
                resolved_at=utc_now(),
                reviewed_by_user_id=None,  # System auto-approved
            )
        )

        school = db.query(School).filter(School.id == target_user.school_id).first()
        system_name = (school.school_name or school.name) if school else None

        try:
            send_password_reset_email(
                recipient_email=target_user.email,
                reset_token=reset_token,
                first_name=target_user.first_name,
                system_name=system_name,
            )
        except EmailDeliveryError as exc:
            db.rollback()
            raise HTTPException(status_code=502, detail=f"Failed to send password reset email: {exc}") from exc

        db.commit()
        return ForgotPasswordRequestResponse(
            message="Your password reset has been processed. Please check your email for instructions to reset your password."
        )

    # MANUAL APPROVAL FLOW for Admins/Campus Admins
    existing_pending = (
        db.query(PasswordResetRequest)
        .filter(
            PasswordResetRequest.user_id == target_user.id,
            PasswordResetRequest.status == "pending",
        )
        .first()
    )
    if existing_pending:
        return ForgotPasswordRequestResponse(message=FORGOT_PASSWORD_GENERIC_MESSAGE)

    db.add(
        PasswordResetRequest(
            user_id=target_user.id,
            school_id=target_user.school_id,
            requested_email=target_user.email.lower(),
            status="pending",
        )
    )
    db.commit()

    return ForgotPasswordRequestResponse(message=FORGOT_PASSWORD_GENERIC_MESSAGE)


@router.post("/auth/reset-password", status_code=204)
def confirm_password_reset(
    payload: ResetPasswordConfirm,
    db: Session = Depends(get_db),
):
    token_hash = hash_token(payload.token)
    
    request_item = (
        db.query(PasswordResetRequest)
        .filter(
            PasswordResetRequest.token_hash == token_hash,
            PasswordResetRequest.status == "approved",
            PasswordResetRequest.expires_at > utc_now(),
        )
        .first()
    )
    
    if not request_item:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    target_user = db.query(User).filter(User.id == request_item.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    target_user.set_password(payload.new_password)
    target_user.must_change_password = False
    target_user.should_prompt_password_change = False
    
    request_item.status = "completed"
    request_item.token_hash = None
    request_item.resolved_at = utc_now()
    
    db.commit()
    return None


@router.get("/auth/password-reset-requests", response_model=list[PasswordResetRequestItem])
def list_password_reset_requests(
    current_user: User = Depends(get_current_admin_or_campus_admin),
    db: Session = Depends(get_db),
):
    is_platform_admin = _is_platform_admin_account(current_user)

    query = (
        db.query(PasswordResetRequest)
        .options(joinedload(PasswordResetRequest.user).joinedload(User.roles).joinedload(UserRole.role))
        .filter(PasswordResetRequest.status == "pending")
        .order_by(PasswordResetRequest.requested_at.asc())
    )

    if not is_platform_admin:
        actor_school_id = getattr(current_user, "school_id", None)
        if actor_school_id is None:
            raise HTTPException(status_code=403, detail="User is not assigned to a school")
        query = query.filter(PasswordResetRequest.school_id == actor_school_id)

    requests = query.all()
    if not is_platform_admin:
        requests = [
            item
            for item in requests
            if item.user is not None
            and not _requires_platform_admin_password_reset_approval(item.user)
        ]

    return [
        PasswordResetRequestItem(
            id=item.id,
            user_id=item.user.id,
            email=item.user.email,
            first_name=item.user.first_name,
            last_name=item.user.last_name,
            roles=[role.role.name for role in item.user.roles if getattr(role, "role", None)],
            status=item.status,
            requested_at=item.requested_at,
        )
        for item in requests
        if item.user is not None
    ]


@router.post("/auth/password-reset-requests/{request_id}/approve", response_model=PasswordResetApprovalResponse)
def approve_password_reset_request(
    request_id: int,
    current_user: User = Depends(get_current_admin_or_campus_admin),
    db: Session = Depends(get_db),
):
    request_item = (
        db.query(PasswordResetRequest)
        .options(joinedload(PasswordResetRequest.user).joinedload(User.roles).joinedload(UserRole.role))
        .filter(
            PasswordResetRequest.id == request_id,
            PasswordResetRequest.status == "pending",
        )
        .first()
    )

    if not request_item or not request_item.user:
        raise HTTPException(status_code=404, detail="Pending password reset request not found")

    is_platform_admin = _is_platform_admin_account(current_user)
    if not is_platform_admin:
        actor_school_id = getattr(current_user, "school_id", None)
        if actor_school_id is None or actor_school_id != request_item.school_id:
            raise HTTPException(status_code=404, detail="Password reset request not found")

    target_user = request_item.user
    if not getattr(target_user, "is_active", True):
        raise HTTPException(status_code=400, detail="Target user is inactive")

    if has_any_role(current_user, ["campus_admin"]) and not has_any_role(current_user, ["admin"]):
        if _requires_platform_admin_password_reset_approval(target_user):
            raise HTTPException(
                status_code=403,
                detail="Campus Admin cannot reset admin or Campus Admin accounts.",
            )
        if current_user.id == target_user.id:
            raise HTTPException(status_code=403, detail="Campus Admin cannot approve their own reset request.")

    reset_token = generate_reset_token()
    token_hash = hash_token(reset_token)
    expires_at = get_token_expiry(hours=2)

    request_item.status = "approved"
    request_item.token_hash = token_hash
    request_item.expires_at = expires_at
    request_item.resolved_at = utc_now()
    request_item.reviewed_by_user_id = current_user.id

    school = db.query(School).filter(School.id == request_item.school_id).first()
    system_name = (school.school_name or school.name) if school else None

    try:
        send_password_reset_email(
            recipient_email=target_user.email,
            reset_token=reset_token,
            first_name=target_user.first_name,
            system_name=system_name,
        )
        try:
            send_account_security_notification(
                db,
                user=target_user,
                subject="Password Reset Approved",
                message="Your password reset request was approved. Please check your email for the reset link.",
                metadata_json={"event": "password_reset_approved", "request_id": request_item.id},
            )
        except Exception:
            pass
    except EmailDeliveryError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Failed to send password reset email: {exc}") from exc

    db.commit()

    return PasswordResetApprovalResponse(
        id=request_item.id,
        user_id=target_user.id,
        status=request_item.status,
        resolved_at=request_item.resolved_at or utc_now(),
        message="Password reset approved and reset link emailed.",
    )

