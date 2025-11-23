"""
Email Service

Handles email sending for password resets, notifications, etc.
Uses Jinja2 templates for customizable HTML emails.
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending transactional emails with Jinja2 template support"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

        # Initialize Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with the given context.

        Args:
            template_name: Name of the template file (e.g., 'password_reset.html')
            context: Dictionary of variables to pass to the template

        Returns:
            str: Rendered HTML content
        """
        # Add default context values
        default_context = {
            "app_name": "DiagnoLeads",
            "year": datetime.now().year,
            "support_email": getattr(settings, "SUPPORT_EMAIL", None),
        }

        # Merge default context with provided context (provided takes precedence)
        full_context = {**default_context, **context}

        template = self.template_env.get_template(template_name)
        return template.render(**full_context)

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
        self,
        to_email: str,
        reset_token: str,
        user_name: Optional[str] = None,
        brand_color: Optional[str] = None,
        logo_url: Optional[str] = None,
    ) -> bool:
        """
        Send password reset email using Jinja2 template.

        Args:
            to_email: Recipient email
            reset_token: Password reset token
            user_name: User's name (optional)
            brand_color: Custom brand color (optional, defaults to #3b82f6)
            logo_url: Custom logo URL (optional)

        Returns:
            bool: True if sent successfully
        """
        # Build reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        # Render HTML template
        context = {
            "reset_link": reset_link,
            "user_name": user_name,
            "brand_color": brand_color,
            "brand_color_hover": "#2563eb" if not brand_color else brand_color,
            "logo_url": logo_url,
        }
        html_content = self.render_template("password_reset.html", context)

        # Plain text fallback
        text_content = f"""DiagnoLeads パスワードリセット

こんにちは{", " + user_name if user_name else ""}、

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

    def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        brand_color: Optional[str] = None,
        brand_color_secondary: Optional[str] = None,
        logo_url: Optional[str] = None,
        dashboard_url: Optional[str] = None,
    ) -> bool:
        """
        Send welcome email to new users using Jinja2 template.

        Args:
            to_email: Recipient email
            user_name: User's name
            brand_color: Custom brand color (optional, defaults to #3b82f6)
            brand_color_secondary: Secondary brand color for gradients (optional)
            logo_url: Custom logo URL (optional)
            dashboard_url: URL to the dashboard (optional)

        Returns:
            bool: True if sent successfully
        """
        # Render HTML template
        context = {
            "user_name": user_name,
            "brand_color": brand_color,
            "brand_color_secondary": brand_color_secondary or brand_color or "#2563eb",
            "brand_color_hover": "#2563eb" if not brand_color else brand_color,
            "logo_url": logo_url,
            "dashboard_url": dashboard_url or f"{settings.FRONTEND_URL}/dashboard",
        }
        html_content = self.render_template("welcome.html", context)

        # Plain text fallback
        text_content = f"""DiagnoLeads へようこそ！

こんにちは、{user_name}さん

DiagnoLeadsへの登録ありがとうございます！

診断コンテンツを作成して、見込み顧客の獲得を始めましょう。

主な機能：
🤖 AI診断生成 - トピックを入力するだけで自動生成
📊 リアルタイム分析 - 診断完了率、CVファネルを可視化
🎯 AIリード分析 - 企業課題を自動検出、ホットリードスコアを算出

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
        lead_company: Optional[str] = None,
        recommended_actions: Optional[str] = None,
        logo_url: Optional[str] = None,
        dashboard_url: Optional[str] = None,
    ) -> bool:
        """
        Send notification email when a new lead is captured, using Jinja2 template.

        Args:
            to_email: Recipient email (tenant admin)
            lead_name: Lead's name
            lead_email: Lead's email
            assessment_title: Assessment title
            score: Lead score (0-100)
            lead_company: Lead's company name (optional)
            recommended_actions: AI-generated recommended actions (optional)
            logo_url: Custom logo URL (optional)
            dashboard_url: URL to the dashboard (optional)

        Returns:
            bool: True if sent successfully
        """
        # Render HTML template
        context = {
            "lead_name": lead_name,
            "lead_email": lead_email,
            "lead_company": lead_company,
            "assessment_title": assessment_title,
            "score": score,
            "recommended_actions": recommended_actions,
            "logo_url": logo_url,
            "dashboard_url": dashboard_url or f"{settings.FRONTEND_URL}/dashboard/leads",
        }
        html_content = self.render_template("lead_notification.html", context)

        # Determine lead temperature
        if score >= 61:
            temp = "🔥 ホットリード"
        elif score >= 31:
            temp = "⚡ ウォームリード"
        else:
            temp = "❄️ コールドリード"

        # Plain text fallback
        text_content = f"""新しいリードが獲得されました！

リード情報:
名前: {lead_name}
メール: {lead_email}
{f"会社: {lead_company}" if lead_company else ""}
診断: {assessment_title}
スコア: {score} ({temp})

{f"推奨アクション: {recommended_actions}" if recommended_actions else ""}

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
