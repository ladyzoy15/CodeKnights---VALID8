"""Use: Contains the main backend rules for password change policy checks.
Where to use: Use this from routers, workers, or other services when password change policy checks logic is needed.
Role: Service layer. It keeps business logic out of the route files.
"""

from __future__ import annotations


NEW_ACCOUNT_MUST_CHANGE_PASSWORD = False
RESET_ACCOUNT_MUST_CHANGE_PASSWORD = True
NEW_ACCOUNT_SHOULD_PROMPT_PASSWORD_CHANGE = True
RESET_ACCOUNT_SHOULD_PROMPT_PASSWORD_CHANGE = False


def must_change_password_for_new_account() -> bool:
    return NEW_ACCOUNT_MUST_CHANGE_PASSWORD


def must_change_password_for_temporary_reset() -> bool:
    return RESET_ACCOUNT_MUST_CHANGE_PASSWORD


def should_prompt_password_change_for_new_account() -> bool:
    return NEW_ACCOUNT_SHOULD_PROMPT_PASSWORD_CHANGE


def should_prompt_password_change_for_temporary_reset() -> bool:
    return RESET_ACCOUNT_SHOULD_PROMPT_PASSWORD_CHANGE


def get_welcome_email_password_notice(*, password_is_temporary: bool = True) -> str:
    if password_is_temporary and must_change_password_for_new_account():
        return (
            "SECURITY NOTICE:\n"
            "This account has been issued a temporary password for initial access.\n"
            "For security purposes, you are required to change your password immediately upon your first login.\n\n"
        )

    if password_is_temporary:
        return (
            "SECURITY NOTICE:\n"
            "This account has been issued a temporary password.\n"
            "While you may continue to use this password, we strongly recommend updating it via your account settings to ensure the continued security of your profile.\n\n"
        )

    return (
        "SECURITY NOTICE:\n"
        "Please maintain the confidentiality of your login credentials.\n"
        "You may update your password at any time through your account security settings.\n\n"
    )
