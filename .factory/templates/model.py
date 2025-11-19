"""
SQLAlchemy Model Template
データベースモデルのテンプレート

使い方:
1. このファイルをコピーして新しいモデルファイルを作成
2. ResourceNameを実際のモデル名に置換
3. 必要なカラムを追加
4. tenant_idカラムは必須（削除しないこと）
"""

from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ResourceName(Base):  # 置換: ResourceName
    """
    リソース名モデル  # 置換: リソース名

    **重要**: すべてのテナント固有データにはtenant_idが必須
    """

    __tablename__ = "resource_names"  # 置換: resource_names (複数形、スネークケース)

    # 主キー
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # マルチテナント（必須）
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # パフォーマンスのためインデックス追加
    )

    # 基本フィールド（例）
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")  # active, inactive, archived
    is_active = Column(Boolean, default=True)

    # 作成者・更新者
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # リレーション
    tenant = relationship(
        "Tenant", back_populates="resource_names"
    )  # 置換: resource_names
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

    # 追加のリレーション（必要に応じて）
    # items = relationship("RelatedModel", back_populates="resource_name")

    def __repr__(self):
        return f"<ResourceName(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"

    # インデックス定義（パフォーマンス最適化）
    __table_args__ = (
        # 複合インデックス: テナント + ステータス
        # Index('ix_resource_names_tenant_status', 'tenant_id', 'status'),
        # 複合インデックス: テナント + 名前（ユニーク制約の場合）
        # Index('ix_resource_names_tenant_name', 'tenant_id', 'name', unique=True),
    )


# Pydanticスキーマ（app/schemas/resource_name.pyに配置）
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class ResourceNameBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field(default="active")
    is_active: bool = True


class ResourceNameCreate(ResourceNameBase):
    pass


class ResourceNameUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class ResourceNameResponse(ResourceNameBase):
    id: UUID
    tenant_id: UUID
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
"""
