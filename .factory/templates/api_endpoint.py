"""
API Endpoint Template
FastAPI エンドポイントのテンプレート

使い方:
1. このファイルをコピーして新しいエンドポイントファイルを作成
2. ResourceNameを実際のリソース名に置換
3. 必要なエンドポイントを実装
4. テナントIDフィルタリングを必ず実装
"""

from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.models.resource import ResourceName  # 置換: ResourceName
from app.schemas.resource import (
    ResourceNameCreate,  # 置換: ResourceName
    ResourceNameUpdate,  # 置換: ResourceName
    ResourceNameResponse,  # 置換: ResourceName
)
from app.services.resource_service import ResourceNameService  # 置換: ResourceName

router = APIRouter()


@router.get(
    "/tenants/{tenant_id}/resources",  # 置換: resources
    response_model=List[ResourceNameResponse],  # 置換: ResourceName
    summary="List all resources",  # 置換: resources
)
async def list_resources(
    tenant_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    リソース一覧を取得
    
    **重要**: テナントIDで必ずフィルタリング
    
    Parameters:
    - tenant_id: テナントID（パスパラメータ）
    - skip: スキップ件数（ページネーション）
    - limit: 取得件数上限
    """
    # テナントIDの検証
    if current_user.tenant_id != tenant_id or current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's resources is forbidden"
        )
    
    service = ResourceNameService(db)  # 置換: ResourceName
    resources = await service.list_by_tenant(
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )
    
    return resources


@router.get(
    "/tenants/{tenant_id}/resources/{resource_id}",  # 置換: resources, resource_id
    response_model=ResourceNameResponse,  # 置換: ResourceName
    summary="Get a resource by ID",  # 置換: resource
)
async def get_resource(
    tenant_id: UUID,
    resource_id: UUID,  # 置換: resource_id
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    リソースを取得
    
    **重要**: テナントIDとリソースIDの両方で検証
    """
    # テナントIDの検証
    if current_user.tenant_id != tenant_id or current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )
    
    service = ResourceNameService(db)  # 置換: ResourceName
    resource = await service.get_by_id(
        resource_id=resource_id,
        tenant_id=tenant_id  # 必須: テナントフィルタ
    )
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    return resource


@router.post(
    "/tenants/{tenant_id}/resources",  # 置換: resources
    response_model=ResourceNameResponse,  # 置換: ResourceName
    status_code=status.HTTP_201_CREATED,
    summary="Create a new resource",  # 置換: resource
)
async def create_resource(
    tenant_id: UUID,
    resource_data: ResourceNameCreate,  # 置換: ResourceName
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    新しいリソースを作成
    
    **重要**: 作成時に必ずtenant_idを設定
    """
    # テナントIDの検証
    if current_user.tenant_id != tenant_id or current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )
    
    service = ResourceNameService(db)  # 置換: ResourceName
    resource = await service.create(
        data=resource_data,
        tenant_id=tenant_id,  # 必須: テナントID設定
        created_by=current_user.id
    )
    
    return resource


@router.put(
    "/tenants/{tenant_id}/resources/{resource_id}",  # 置換: resources, resource_id
    response_model=ResourceNameResponse,  # 置換: ResourceName
    summary="Update a resource",  # 置換: resource
)
async def update_resource(
    tenant_id: UUID,
    resource_id: UUID,  # 置換: resource_id
    resource_data: ResourceNameUpdate,  # 置換: ResourceName
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    リソースを更新
    
    **重要**: 更新前にテナントとリソースの所有権を確認
    """
    # テナントIDの検証
    if current_user.tenant_id != tenant_id or current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )
    
    service = ResourceNameService(db)  # 置換: ResourceName
    
    # 既存リソースの確認（テナントフィルタ付き）
    existing_resource = await service.get_by_id(
        resource_id=resource_id,
        tenant_id=tenant_id
    )
    
    if not existing_resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # 更新実行
    resource = await service.update(
        resource_id=resource_id,
        data=resource_data,
        tenant_id=tenant_id  # 必須: テナントフィルタ
    )
    
    return resource


@router.delete(
    "/tenants/{tenant_id}/resources/{resource_id}",  # 置換: resources, resource_id
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resource",  # 置換: resource
)
async def delete_resource(
    tenant_id: UUID,
    resource_id: UUID,  # 置換: resource_id
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    リソースを削除
    
    **重要**: 削除前にテナントとリソースの所有権を確認
    """
    # テナントIDの検証
    if current_user.tenant_id != tenant_id or current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )
    
    service = ResourceNameService(db)  # 置換: ResourceName
    
    # 既存リソースの確認（テナントフィルタ付き）
    existing_resource = await service.get_by_id(
        resource_id=resource_id,
        tenant_id=tenant_id
    )
    
    if not existing_resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # 削除実行
    await service.delete(
        resource_id=resource_id,
        tenant_id=tenant_id  # 必須: テナントフィルタ
    )
    
    return None
