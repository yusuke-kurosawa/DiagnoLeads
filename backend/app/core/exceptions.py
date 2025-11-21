"""
統一エラーハンドリングシステム

このモジュールは、DiagnoLeads全体で使用する標準化された例外クラスとエラーコードを提供します。
すべてのカスタムビジネスロジックエラーは、このモジュールの例外クラスを使用してください。
"""

from enum import Enum
from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class ErrorCode(str, Enum):
    """アプリケーション全体で使用するエラーコード"""

    # ========================================================================
    # 認証・認可エラー (AUTH_xxx)
    # ========================================================================
    AUTH_INVALID_CREDENTIALS = "AUTH_001"
    AUTH_TOKEN_EXPIRED = "AUTH_002"
    AUTH_TOKEN_INVALID = "AUTH_003"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_004"
    AUTH_USER_NOT_FOUND = "AUTH_005"
    AUTH_USER_ALREADY_EXISTS = "AUTH_006"
    AUTH_EMAIL_NOT_VERIFIED = "AUTH_007"

    # ========================================================================
    # テナント関連エラー (TENANT_xxx)
    # ========================================================================
    TENANT_NOT_FOUND = "TENANT_001"
    TENANT_INVALID = "TENANT_002"
    TENANT_LIMIT_EXCEEDED = "TENANT_003"
    TENANT_SUBSCRIPTION_INACTIVE = "TENANT_004"
    TENANT_ACCESS_DENIED = "TENANT_005"  # マルチテナント分離違反

    # ========================================================================
    # 診断 (Assessment) エラー (ASSESS_xxx)
    # ========================================================================
    ASSESSMENT_NOT_FOUND = "ASSESS_001"
    ASSESSMENT_INVALID_STATUS = "ASSESS_002"
    ASSESSMENT_VALIDATION_FAILED = "ASSESS_003"
    ASSESSMENT_PUBLISH_FAILED = "ASSESS_004"
    ASSESSMENT_QUESTION_LIMIT = "ASSESS_005"
    ASSESSMENT_AI_GENERATION_FAILED = "ASSESS_006"

    # ========================================================================
    # リード (Lead) エラー (LEAD_xxx)
    # ========================================================================
    LEAD_NOT_FOUND = "LEAD_001"
    LEAD_INVALID_STATUS = "LEAD_002"
    LEAD_DUPLICATE_EMAIL = "LEAD_003"
    LEAD_SCORING_FAILED = "LEAD_004"
    LEAD_EXPORT_FAILED = "LEAD_005"

    # ========================================================================
    # レスポンス (Response) エラー (RESP_xxx)
    # ========================================================================
    RESPONSE_NOT_FOUND = "RESP_001"
    RESPONSE_INVALID_ANSWER = "RESP_002"
    RESPONSE_ALREADY_SUBMITTED = "RESP_003"
    RESPONSE_EXPIRED = "RESP_004"

    # ========================================================================
    # QRコードエラー (QR_xxx)
    # ========================================================================
    QR_CODE_NOT_FOUND = "QR_001"
    QR_CODE_GENERATION_FAILED = "QR_002"
    QR_CODE_INVALID_FORMAT = "QR_003"

    # ========================================================================
    # 外部連携エラー (INTEGRATION_xxx)
    # ========================================================================
    INTEGRATION_NOT_FOUND = "INTEGRATION_001"
    INTEGRATION_AUTH_FAILED = "INTEGRATION_002"
    INTEGRATION_API_ERROR = "INTEGRATION_003"
    INTEGRATION_GA4_FAILED = "INTEGRATION_004"
    INTEGRATION_TEAMS_FAILED = "INTEGRATION_005"
    INTEGRATION_SALESFORCE_FAILED = "INTEGRATION_006"

    # ========================================================================
    # バリデーションエラー (VALID_xxx)
    # ========================================================================
    VALIDATION_ERROR = "VALID_001"
    VALIDATION_REQUIRED_FIELD = "VALID_002"
    VALIDATION_INVALID_FORMAT = "VALID_003"
    VALIDATION_OUT_OF_RANGE = "VALID_004"

    # ========================================================================
    # データベースエラー (DB_xxx)
    # ========================================================================
    DB_QUERY_FAILED = "DB_001"
    DB_INTEGRITY_ERROR = "DB_002"
    DB_TRANSACTION_FAILED = "DB_003"
    DB_CONNECTION_FAILED = "DB_004"

    # ========================================================================
    # 外部サービスエラー (EXT_xxx)
    # ========================================================================
    EXTERNAL_SERVICE_UNAVAILABLE = "EXT_001"
    EXTERNAL_SERVICE_TIMEOUT = "EXT_002"
    EXTERNAL_API_RATE_LIMIT = "EXT_003"

    # ========================================================================
    # システムエラー (SYS_xxx)
    # ========================================================================
    SYSTEM_ERROR = "SYS_001"
    SYSTEM_CONFIGURATION_ERROR = "SYS_002"
    SYSTEM_RESOURCE_EXHAUSTED = "SYS_003"


class DiagnoLeadsException(Exception):
    """
    DiagnoLeadsアプリケーションの基底例外クラス

    すべてのカスタムビジネスロジックエラーはこのクラスを継承してください。

    Attributes:
        code: エラーコード (ErrorCodeから選択)
        message: ユーザー向けエラーメッセージ
        details: 追加のエラー詳細情報（デバッグ用）
        http_status: 対応するHTTPステータスコード
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        http_status: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.http_status = http_status
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """例外を辞書形式に変換（APIレスポンス用）"""
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "details": self.details,
            }
        }

    def to_http_exception(self) -> HTTPException:
        """FastAPI HTTPException に変換"""
        return HTTPException(
            status_code=self.http_status,
            detail=self.to_dict()["error"],
        )


# ============================================================================
# 特定ドメイン向けの例外クラス
# ============================================================================


class AuthenticationError(DiagnoLeadsException):
    """認証エラー"""

    def __init__(
        self,
        code: ErrorCode = ErrorCode.AUTH_INVALID_CREDENTIALS,
        message: str = "認証に失敗しました",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            http_status=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationError(DiagnoLeadsException):
    """認可エラー（権限不足）"""

    def __init__(
        self,
        code: ErrorCode = ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
        message: str = "この操作を実行する権限がありません",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            http_status=status.HTTP_403_FORBIDDEN,
        )


class TenantError(DiagnoLeadsException):
    """テナント関連エラー"""

    def __init__(
        self,
        code: ErrorCode = ErrorCode.TENANT_NOT_FOUND,
        message: str = "テナントが見つかりません",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            http_status=status.HTTP_404_NOT_FOUND,
        )


class TenantAccessDeniedError(DiagnoLeadsException):
    """マルチテナント分離違反エラー（セキュリティクリティカル）"""

    def __init__(
        self,
        message: str = "他のテナントのリソースにアクセスできません",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code=ErrorCode.TENANT_ACCESS_DENIED,
            message=message,
            details=details,
            http_status=status.HTTP_403_FORBIDDEN,
        )


class ResourceNotFoundError(DiagnoLeadsException):
    """リソースが見つからないエラー"""

    def __init__(
        self,
        code: ErrorCode,
        resource_type: str,
        resource_id: Any,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"{resource_type} (ID: {resource_id}) が見つかりません"
        super().__init__(
            code=code,
            message=message,
            details=details or {"resource_type": resource_type, "resource_id": resource_id},
            http_status=status.HTTP_404_NOT_FOUND,
        )


class ValidationError(DiagnoLeadsException):
    """バリデーションエラー"""

    def __init__(
        self,
        code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        message: str = "入力データが無効です",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class ExternalServiceError(DiagnoLeadsException):
    """外部サービス連携エラー"""

    def __init__(
        self,
        code: ErrorCode,
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code=code,
            message=f"{service_name}: {message}",
            details=details or {"service": service_name},
            http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class DatabaseError(DiagnoLeadsException):
    """データベースエラー"""

    def __init__(
        self,
        code: ErrorCode = ErrorCode.DB_QUERY_FAILED,
        message: str = "データベース操作に失敗しました",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ============================================================================
# エラーハンドラー用ヘルパー関数
# ============================================================================


def handle_exception(exc: Exception) -> HTTPException:
    """
    例外を適切なHTTPExceptionに変換する

    Usage:
        try:
            # ビジネスロジック
        except Exception as e:
            raise handle_exception(e)
    """
    if isinstance(exc, DiagnoLeadsException):
        return exc.to_http_exception()

    # 予期しないエラーは500エラーとして扱う
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "code": ErrorCode.SYSTEM_ERROR.value,
            "message": "システムエラーが発生しました",
            "details": {"error": str(exc)} if isinstance(exc, Exception) else {},
        },
    )
