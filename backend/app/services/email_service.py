"""
Email Service

Handles email sending for password resets, notifications, etc.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending transactional emails"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email using SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (fallback)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.smtp_host or not self.smtp_user:
            logger.warning("SMTP not configured. Email not sent.")
            logger.info(f"Would send email to {to_email}: {subject}")
            logger.info(f"Content: {text_content or html_content}")
            return False

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add text part
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_port == 587:
                    server.starttls()

                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                server.send_message(message)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_password_reset_email(
        self, to_email: str, reset_token: str, user_name: Optional[str] = None
    ) -> bool:
        """
        Send password reset email.

        Args:
            to_email: Recipient email
            reset_token: Password reset token
            user_name: User's name (optional)

        Returns:
            bool: True if sent successfully
        """
        # Build reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #3b82f6;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>DiagnoLeads</h1>
                </div>
                <div class="content">
                    <h2>パスワードリセットのリクエスト</h2>
                    <p>こんにちは{', ' + user_name if user_name else ''}、</p>
                    <p>パスワードリセットのリクエストを受け付けました。</p>
                    <p>以下のボタンをクリックして、新しいパスワードを設定してください：</p>
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">パスワードをリセット</a>
                    </p>
                    <p>このリンクは1時間後に無効になります。</p>
                    <p>もしこのリクエストに心当たりがない場合は、このメールを無視してください。</p>
                </div>
                <div class="footer">
                    <p>このメールはDiagnoLeadsから送信されています。</p>
                    <p>© 2025 DiagnoLeads. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text fallback
        text_content = f"""
        DiagnoLeads パスワードリセット

        こんにちは{', ' + user_name if user_name else ''}、

        パスワードリセットのリクエストを受け付けました。

        以下のリンクをクリックして、新しいパスワードを設定してください：
        {reset_link}

        このリンクは1時間後に無効になります。

        もしこのリクエストに心当たりがない場合は、このメールを無視してください。

        ---
        DiagnoLeads
        """

        return self.send_email(
            to_email=to_email,
            subject="パスワードリセットのリクエスト - DiagnoLeads",
            html_content=html_content,
            text_content=text_content,
        )

    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """
        Send welcome email to new users.

        Args:
            to_email: Recipient email
            user_name: User's name

        Returns:
            bool: True if sent successfully
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>DiagnoLeads へようこそ！</h1>
                </div>
                <div class="content">
                    <h2>こんにちは、{user_name}さん</h2>
                    <p>DiagnoLeadsへの登録ありがとうございます！</p>
                    <p>診断コンテンツを作成して、見込み顧客の獲得を始めましょう。</p>
                    <p>ご質問やサポートが必要な場合は、お気軽にお問い合わせください。</p>
                </div>
                <div class="footer">
                    <p>© 2025 DiagnoLeads. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        DiagnoLeads へようこそ！

        こんにちは、{user_name}さん

        DiagnoLeadsへの登録ありがとうございます！

        診断コンテンツを作成して、見込み顧客の獲得を始めましょう。

        ご質問やサポートが必要な場合は、お気軽にお問い合わせください。

        ---
        DiagnoLeads
        """

        return self.send_email(
            to_email=to_email,
            subject="DiagnoLeadsへようこそ！",
            html_content=html_content,
            text_content=text_content,
        )

    def send_lead_notification_email(
        self,
        to_email: str,
        lead_name: str,
        lead_email: str,
        assessment_title: str,
        score: int,
    ) -> bool:
        """
        Send notification email when a new lead is captured.

        Args:
            to_email: Recipient email (tenant admin)
            lead_name: Lead's name
            lead_email: Lead's email
            assessment_title: Assessment title
            score: Lead score

        Returns:
            bool: True if sent successfully
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #10b981; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .score {{ font-size: 48px; font-weight: bold; color: #10b981; text-align: center; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 新しいリードが獲得されました！</h1>
                </div>
                <div class="content">
                    <h2>リード情報</h2>
                    <p><strong>名前:</strong> {lead_name}</p>
                    <p><strong>メール:</strong> {lead_email}</p>
                    <p><strong>診断:</strong> {assessment_title}</p>
                    <p class="score">スコア: {score}</p>
                    <p>ダッシュボードで詳細を確認してください。</p>
                </div>
                <div class="footer">
                    <p>© 2025 DiagnoLeads. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        新しいリードが獲得されました！

        リード情報:
        名前: {lead_name}
        メール: {lead_email}
        診断: {assessment_title}
        スコア: {score}

        ダッシュボードで詳細を確認してください。

        ---
        DiagnoLeads
        """

        return self.send_email(
            to_email=to_email,
            subject=f"新しいリードが獲得されました - {lead_name}",
            html_content=html_content,
            text_content=text_content,
        )


# Singleton instance
email_service = EmailService()
