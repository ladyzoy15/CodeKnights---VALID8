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
            <h1 style="margin: 0; font-size: 24px; font-weight: 600;">Account Activation - {safe_system_name}</h1>
        </div>
        <div style="padding: 40px; color: #333333; line-height: 1.6;">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>{safe_first_name}</strong>,</p>
            <p>We are pleased to inform you that your official account has been successfully created. You may now access your campus services through our unified digital portal.</p>
            
            <div style="background-color: #f8fafc; border-radius: 8px; padding: 25px; margin: 30px 0; border: 1px solid #cbd5e1;">
                <h2 style="font-size: 16px; margin-top: 0; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">Authentication Details</h2>
                <p style="margin: 10px 0;"><strong>Registered Email:</strong> {safe_email}</p>
                <p style="margin: 10px 0;"><strong>{safe_password_label}:</strong> <code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{safe_password}</code></p>
            </div>

            <div style="text-align: center; margin: 40px 0;">
                <a href="{safe_login_url}" style="background-color: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; display: inline-block;">Proceed to Portal</a>
            </div>

            <div style="color: #64748b; font-size: 14px; border-top: 1px solid #f1f5f9; padding-top: 20px;">
                {safe_notice}
            </div>
            <p style="color: #ef4444; font-size: 13px; font-style: italic; margin-top: 20px;"><strong>Confidentiality Notice:</strong> To maintain the integrity of your account, please do not disclose these credentials to unauthorized personnel.</p>
        </div>
        <div style="padding: 20px 40px; background-color: #f1f5f9; text-align: center; color: #64748b; font-size: 12px; border-top: 1px solid #e2e8f0;">
            <p>For technical assistance, please contact the Campus Information Technology Department.</p>
            <p style="margin: 5px 0;">&copy; 2026 {safe_system_name} Infrastructure Team</p>
        </div>
    </div>
    """

    text_body = (
        f"Dear {first_name},\n\n"
        f"Greetings from {system_name}.\n\n"
        "This is to formally notify you that your account has been successfully provisioned. You may now access the campus portal using the credentials provided below.\n\n"
        "Authentication Details:\n"
        "-----------------------------------\n"
        f"Registered Email: {recipient_email}\n"
        f"{password_label}: {temporary_password}\n"
        f"Portal Access URL: {login_url}\n"
        "-----------------------------------\n\n"
        f"{password_notice}\n"
        "Please maintain the confidentiality of these credentials. If you did not expect this communication or encounter any technical difficulties, please reach out to your Campus IT Administrator.\n\n"
        "Sincerely,\n"
        f"The {system_name} Team\n"
    )

    return (f"{system_name} - Official Account Activation", text_body, html_body)


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
            <h1 style="margin: 0; font-size: 24px; font-weight: 600;">Account Initialization - {safe_system_name}</h1>
        </div>
        <div style="padding: 40px; color: #333333; line-height: 1.6;">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>{safe_first_name}</strong>,</p>
            <p>Your institutional account has been successfully initialized within the <strong>{safe_system_name}</strong> management system.</p>
            
            <p>To complete your registration and establish your permanent password, please utilize the <strong>"Forgot Password"</strong> recovery feature on the portal login page.</p>
            <div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px; color: #92400e; font-size: 14px; margin: 25px 0;">
                <strong>Administrative Note:</strong> Please be advised that full portal access is subject to final approval by a Campus Administrator.
            </div>

            <div style="text-align: center; margin: 40px 0;">
                <a href="{safe_login_url}" style="background-color: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; display: inline-block;">Access Login Portal</a>
            </div>
        </div>
        <div style="padding: 20px 40px; background-color: #f1f5f9; text-align: center; color: #64748b; font-size: 12px; border-top: 1px solid #e2e8f0;">
            <p>Should you require assistance, please coordinate with the Campus IT Department.</p>
            <p style="margin: 5px 0;">&copy; 2026 {safe_system_name} Infrastructure Team</p>
        </div>
    </div>
    """

    text_body = (
        f"Dear {first_name},\n\n"
        f"This is an official notification regarding the initialization of your account in the {system_name} system.\n\n"
        "To finalize your setup and establish your security credentials, please visit the portal and use the 'Forgot Password' option.\n"
        "Note that administrative approval is required before full access is granted.\n\n"
        f"Portal Access URL: {login_url}\n\n"
        "For technical inquiries, please contact your Campus Administrator.\n\n"
        "Sincerely,\n"
        f"The {system_name} Team\n"
    )

    return (f"{system_name} - Official Account Initialization", text_body, html_body)


def build_password_reset_email_content(
    *,
    recipient_email: str,
    reset_url: str,
    first_name: str,
    system_name: str,
) -> tuple[str, str, str]:
    safe_system_name = html.escape(system_name)
    safe_first_name = html.escape(first_name)
    safe_email = html.escape(recipient_email)
    safe_reset_url = html.escape(reset_url)

    html_body = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 20px auto; border: 1px solid #e1e1e1; border-radius: 12px; overflow: hidden; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="background: linear-gradient(135deg, #1e293b 0%, #475569 100%); padding: 30px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 24px; font-weight: 600;">Password Reset Request</h1>
        </div>
        <div style="padding: 40px; color: #333333; line-height: 1.6;">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>{safe_first_name}</strong>,</p>
            <p>We received a request to reset the password for your <strong>{safe_system_name}</strong> account associated with {safe_email}.</p>
            
            <p>To proceed with your password reset, please click the button below. This link will expire in 2 hours for your security.</p>

            <div style="text-align: center; margin: 40px 0;">
                <a href="{safe_reset_url}" style="background-color: #1e293b; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; display: inline-block;">Reset My Password</a>
            </div>

            <div style="background-color: #f8fafc; border-left: 4px solid #cbd5e1; padding: 15px; color: #64748b; font-size: 14px; margin: 25px 0;">
                <strong>Note:</strong> If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged.
            </div>
        </div>
        <div style="padding: 20px 40px; background-color: #f1f5f9; text-align: center; color: #64748b; font-size: 12px; border-top: 1px solid #e2e8f0;">
            <p>If you're having trouble clicking the "Reset My Password" button, copy and paste the URL below into your web browser:</p>
            <p style="word-break: break-all; color: #3b82f6;">{safe_reset_url}</p>
            <p style="margin: 20px 0 5px 0;">&copy; 2026 {safe_system_name} Infrastructure Team</p>
        </div>
    </div>
    """

    text_body = (
        f"Dear {first_name},\n\n"
        f"We received a request to reset your password for the {system_name} portal.\n\n"
        "To reset your password, please visit the following link:\n"
        f"{reset_url}\n\n"
        "This link will expire in 2 hours.\n\n"
        "If you did not initiate this request, you can safely ignore this email.\n\n"
        "Sincerely,\n"
        f"The {system_name} Team\n"
    )

    return (f"{system_name} - Password Reset Request", text_body, html_body)


