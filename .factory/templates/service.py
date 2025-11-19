"""
Service Layer Template
ビジネスロジック層のテンプレート

使い方:
1. このファイルをコピーして新しいサービスファイルを作成
2. ResourceNameを実際のリソース名に置換
3. ビジネスロジックを実装
4. すべてのデータベース操作でtenant_idフィルタリング必須
"""

from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.resource import ResourceName  # 置換: ResourceName
from app.schemas.resource import (
    ResourceNameCreate,  # 置換: ResourceName
    ResourceNameUpdate,  # 置換: ResourceName
)


class ResourceNameService:  # 置換: ResourceName
    """
    リソース名サービス  # 置換: リソース名

    **重要**: すべてのメソッドでtenant_idフィルタリングを実施
    """

    def __init__(self, db: Session):
        self.db = db

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[ResourceName]:  # 置換: ResourceName
        """
        テナント固有のリソース一覧を取得

        Args:
            tenant_id: テナントID（必須）
            skip: スキップ件数
            limit: 取得件数上限
            status: ステータスフィルタ（オプション）

        Returns:
            リソースのリスト
        """
        query = self.db.query(ResourceName).filter(
            ResourceName.tenant_id == tenant_id  # 必須: テナントフィルタ
        )

        # オプションフィルタ
        if status:
            query = query.filter(ResourceName.status == status)

        # ソート・ページネーション
        resources = (
            query.order_by(ResourceName.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return resources

    async def get_by_id(
        self, resource_id: UUID, tenant_id: UUID
    ) -> Optional[ResourceName]:  # 置換: ResourceName
        """
        IDでリソースを取得

        **重要**: tenant_idとresource_idの両方でフィルタリング

        Args:
            resource_id: リソースID
            tenant_id: テナントID（必須）

        Returns:
            リソース、または存在しない場合はNone
        """
        resource = (
            self.db.query(ResourceName)
            .filter(
                and_(
                    ResourceName.id == resource_id,
                    ResourceName.tenant_id == tenant_id,  # 必須: テナントフィルタ
                )
            )
            .first()
        )

        return resource

    async def create(
        self,
        data: ResourceNameCreate,  # 置換: ResourceName
        tenant_id: UUID,
        created_by: UUID,
    ) -> ResourceName:  # 置換: ResourceName
        """
        新しいリソースを作成

        **重要**: 作成時に必ずtenant_idを設定

        Args:
            data: リソース作成データ
            tenant_id: テナントID（必須）
            created_by: 作成者ユーザーID

        Returns:
            作成されたリソース
        """
        resource = ResourceName(  # 置換: ResourceName
            **data.model_dump(),
            tenant_id=tenant_id,  # 必須: テナントID設定
            created_by=created_by,
        )

        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)

        return resource

    async def update(
        self,
        resource_id: UUID,
        data: ResourceNameUpdate,  # 置換: ResourceName
        tenant_id: UUID,
    ) -> Optional[ResourceName]:  # 置換: ResourceName
        """
        リソースを更新

        **重要**: 更新時もtenant_idでフィルタリング

        Args:
            resource_id: リソースID
            data: 更新データ
            tenant_id: テナントID（必須）

        Returns:
            更新されたリソース、または存在しない場合はNone
        """
        resource = await self.get_by_id(
            resource_id=resource_id,
            tenant_id=tenant_id,  # 必須: テナントフィルタ
        )

        if not resource:
            return None

        # 更新データを適用
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(resource, field, value)

        self.db.commit()
        self.db.refresh(resource)

        return resource

    async def delete(self, resource_id: UUID, tenant_id: UUID) -> bool:
        """
        リソースを削除

        **重要**: 削除時もtenant_idでフィルタリング

        Args:
            resource_id: リソースID
            tenant_id: テナントID（必須）

        Returns:
            削除成功の場合True、リソースが存在しない場合False
        """
        resource = await self.get_by_id(
            resource_id=resource_id,
            tenant_id=tenant_id,  # 必須: テナントフィルタ
        )

        if not resource:
            return False

        self.db.delete(resource)
        self.db.commit()

        return True

    async def count_by_tenant(
        self, tenant_id: UUID, status: Optional[str] = None
    ) -> int:
        """
        テナントのリソース数を取得

        Args:
            tenant_id: テナントID（必須）
            status: ステータスフィルタ（オプション）

        Returns:
            リソース数
        """
        query = self.db.query(ResourceName).filter(
            ResourceName.tenant_id == tenant_id  # 必須: テナントフィルタ
        )

        if status:
            query = query.filter(ResourceName.status == status)

        return query.count()

    async def search_by_name(
        self, tenant_id: UUID, name_query: str, limit: int = 10
    ) -> List[ResourceName]:  # 置換: ResourceName
        """
        名前でリソースを検索

        Args:
            tenant_id: テナントID（必須）
            name_query: 検索クエリ
            limit: 取得件数上限

        Returns:
            検索結果のリスト
        """
        resources = (
            self.db.query(ResourceName)
            .filter(
                and_(
                    ResourceName.tenant_id == tenant_id,  # 必須: テナントフィルタ
                    ResourceName.name.ilike(f"%{name_query}%"),  # 部分一致検索
                )
            )
            .limit(limit)
            .all()
        )

        return resources

    # AI機能統合の例
    async def generate_with_ai(
        self, tenant_id: UUID, prompt: str, created_by: UUID
    ) -> ResourceName:  # 置換: ResourceName
        """
        AI（Claude）を使用してリソースを生成

        Args:
            tenant_id: テナントID（必須）
            prompt: AI生成用プロンプト
            created_by: 作成者ユーザーID

        Returns:
            AI生成されたリソース
        """
        # TODO: AI生成ロジックを実装
        # from app.services.ai.generator import AIGenerator
        # ai_generator = AIGenerator()
        # generated_data = await ai_generator.generate(prompt)

        # 仮実装
        generated_data = {
            "name": f"AI Generated: {prompt[:50]}",
            "description": "AI generated content",
        }

        # 生成データからリソースを作成
        resource = ResourceName(
            **generated_data,
            tenant_id=tenant_id,  # 必須: テナントID設定
            created_by=created_by,
        )

        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)

        return resource
