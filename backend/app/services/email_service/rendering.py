"""Template rendering helpers for the email service package."""

from __future__ import annotations

import html


def _send_email(
    *,
    subject: str,
    recipient_email: str,
    body: str,
    html_body: str | None = None,
    reply_to: str | None = None,
) -> None:
    from . import send_transactional_email

    send_transactional_email(
        recipient_email=recipient_email,
        subject=subject,
        text_body=body,
        html_body=html_body,
        reply_to=reply_to,
    )


def build_welcome_email_content(
    *,
    recipient_email: str,
    temporary_password: str,
    first_name: str,
    system_name: str,
    login_url: str,
    password_label: str,
    credential_subject: str,
    password_notice: str,
) -> tuple[str, str, str]:
    safe_system_name = html.escape(system_name)
    safe_first_name = html.escape(first_name)
    safe_email = html.escape(recipient_email)
    safe_password = html.escape(temporary_password)
    safe_login_url = html.escape(login_url)
    safe_password_label = html.escape(password_label)
    safe_notice = html.escape(password_notice).replace(chr(10), '<br>')

    html_body = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 20px auto; border: 1px solid #e1e1e1; border-radius: 12px; overflow: hidden; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 30px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 24px; font-weight: 600;">Welcome to {safe_system_name}</h1>
        </div>
        <div style="padding: 40px; color: #333333; line-height: 1.6;">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>{safe_first_name}</strong>,</p>
            <p>Your account has been successfully created. You can now access your campus services through our unified portal.</p>
            
            <div style="background-color: #f8fafc; border-radius: 8px; padding: 25px; margin: 30px 0; border: 1px solid #cbd5e1;">
                <h2 style="font-size: 16px; margin-top: 0; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">Login Credentials</h2>
                <p style="margin: 10px 0;"><strong>Email:</strong> {safe_email}</p>
                <p style="margin: 10px 0;"><strong>{safe_password_label}:</strong> <code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{safe_password}</code></p>
            </div>

            <div style="text-align: center; margin: 40px 0;">
                <a href="{safe_login_url}" style="background-color: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; display: inline-block;">Log In to Portal</a>
            </div>

            <p style="color: #64748b; font-size: 14px;">{safe_notice}</p>
            <p style="color: #ef4444; font-size: 13px; font-style: italic;"><strong>Notice:</strong> Please do not share your login credentials with anyone for security purposes.</p>
        </div>
        <div style="padding: 20px 40px; background-color: #f1f5f9; text-align: center; color: #64748b; font-size: 12px; border-top: 1px solid #e2e8f0;">
            <p>If you experience issues, please contact your Campus Administrator.</p>
            <p style="margin: 5px 0;">&copy; 2026 {safe_system_name} Team</p>
        </div>
    </div>
    """

    text_body = (
        f"Dear {first_name},\n\n"
        f"Welcome to {system_name}!\n\n"
        "Your account has been successfully created.\n\n"
        "Login Credentials:\n"
        "-----------------------------------\n"
        f"Email: {recipient_email}\n"
        f"{password_label}: {temporary_password}\n"
        f"Login URL: {login_url}\n"
        "-----------------------------------\n\n"
        f"{password_notice}\n"
        "Do not share your login credentials with anyone.\n\n"
        "If you experience issues, contact your Campus Admin.\n\n"
        "Best regards,\n"
        f"{system_name} Team\n"
    )

    return (f"Welcome to {system_name} - {credential_subject}", text_body, html_body)


def build_import_onboarding_email_content(
    *,
    first_name: str,
    system_name: str,
    login_url: str,
) -> tuple[str, str, str]:
    safe_system_name = html.escape(system_name)
    safe_first_name = html.escape(first_name)
    safe_login_url = html.escape(login_url)

    html_body = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 20px auto; border: 1px solid #e1e1e1; border-radius: 12px; overflow: hidden; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 30px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 24px; font-weight: 600;">Account Ready - {safe_system_name}</h1>
        </div>
        <div style="padding: 40px; color: #333333; line-height: 1.6;">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>{safe_first_name}</strong>,</p>
            <p>Your account has been successfully initialized in the <strong>{safe_system_name}</strong> system.</p>
            
            <p>To finalize your setup and create your password, please use the <strong>Forgot Password</strong> option on the login page.</p>
            <p style="background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px; color: #92400e; font-size: 14px;">
                <strong>Note:</strong> A Campus Administrator must approve your request before you can gain full access to the portal.
            </p>

            <div style="text-align: center; margin: 40px 0;">
                <a href="{safe_login_url}" style="background-color: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; display: inline-block;">Go to Login Page</a>
            </div>
        </div>
        <div style="padding: 20px 40px; background-color: #f1f5f9; text-align: center; color: #64748b; font-size: 12px; border-top: 1px solid #e2e8f0;">
            <p>If you experience issues, please contact your Campus Administrator.</p>
            <p style="margin: 5px 0;">&copy; 2026 {safe_system_name} Team</p>
        </div>
    </div>
    """

    text_body = (
        f"Dear {first_name},\n\n"
        f"Your account has been created in {system_name}.\n\n"
        "To set your first password, open the login page and use the Forgot Password option.\n"
        "A Campus Admin must approve the request before you can sign in.\n\n"
        f"Login URL: {login_url}\n\n"
        "If you experience issues, contact your Campus Admin.\n\n"
        "Best regards,\n"
        f"{system_name} Team\n"
    )

    return (f"Welcome to {system_name} - Account Ready", text_body, html_body)


def build_password_reset_email_content(
    *,
    recipient_email: str,
    temporary_password: str,
    first_name: str,
    system_name: str,
    login_url: str,
) -> tuple[str, str, str]:
    safe_system_name = html.escape(system_name)
    safe_first_name = html.escape(first_name)
    safe_email = html.escape(recipient_email)
    safe_password = html.escape(temporary_password)
    safe_login_url = html.escape(login_url)

    html_body = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 20px auto; border: 1px solid #e1e1e1; border-radius: 12px; overflow: hidden; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="background: linear-gradient(135deg, #1e293b 0%, #475569 100%); padding: 30px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 24px; font-weight: 600;">Password Reset Approved</h1>
        </div>
        <div style="padding: 40px; color: #333333; line-height: 1.6;">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>{safe_first_name}</strong>,</p>
            <p>Your password reset request for <strong>{safe_system_name}</strong> has been approved by your administrator.</p>
            
            <div style="background-color: #f8fafc; border-radius: 8px; padding: 25px; margin: 30px 0; border: 1px solid #cbd5e1;">
                <h2 style="font-size: 16px; margin-top: 0; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">Temporary Credentials</h2>
                <p style="margin: 10px 0;"><strong>Email:</strong> {safe_email}</p>
                <p style="margin: 10px 0;"><strong>Temporary Password:</strong> <code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{safe_password}</code></p>
            </div>

            <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; color: #991b1b; font-size: 15px;">
                <strong>IMPORTANT:</strong> You are required to change this temporary password immediately after your next login.
            </div>

            <div style="text-align: center; margin: 40px 0;">
                <a href="{safe_login_url}" style="background-color: #1e293b; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; display: inline-block;">Access Your Account</a>
            </div>
        </div>
        <div style="padding: 20px 40px; background-color: #f1f5f9; text-align: center; color: #64748b; font-size: 12px; border-top: 1px solid #e2e8f0;">
            <p>If you did not request this, please contact security immediately.</p>
            <p style="margin: 5px 0;">&copy; 2026 {safe_system_name} Team</p>
        </div>
    </div>
    """

    text_body = (
        f"Dear {first_name},\n\n"
        "Your password reset request has been approved.\n\n"
        "Temporary Login Credentials:\n"
        "-----------------------------------\n"
        f"Email: {recipient_email}\n"
        f"Temporary Password: {temporary_password}\n"
        f"Login URL: {login_url}\n"
        "-----------------------------------\n\n"
        "IMPORTANT:\n"
        "You are required to change this temporary password immediately after login.\n\n"
        "Best regards,\n"
        f"{system_name} Team\n"
    )

    return (f"{system_name} - Password Reset Approved", text_body, html_body)


