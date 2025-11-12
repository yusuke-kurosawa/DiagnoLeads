"""
Taxonomy API Endpoints - Topics and Industries

Handles CRUD operations for taxonomy data (topics and industries).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.topic import Topic
from app.models.industry import Industry
from app.models.user import User
from app.schemas.taxonomy import (
    TopicResponse,
    TopicCreate,
    TopicUpdate,
    IndustryResponse,
    IndustryCreate,
    IndustryUpdate,
)

router = APIRouter()


# TOPICS ENDPOINTS

@router.get("/tenants/{tenant_id}/topics", response_model=list[TopicResponse])
async def get_topics(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all topics for a tenant."""
    topics = db.query(Topic).filter(Topic.tenant_id == tenant_id).all()
    return topics


@router.get("/tenants/{tenant_id}/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(
    tenant_id: str,
    topic_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific topic."""
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.tenant_id == tenant_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )
    
    return topic


@router.post("/tenants/{tenant_id}/topics", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    tenant_id: str,
    data: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new topic for a tenant."""
    topic = Topic(
        tenant_id=tenant_id,
        name=data.name,
        description=data.description,
        color=data.color,
        icon=data.icon,
    )
    
    db.add(topic)
    db.commit()
    db.refresh(topic)
    
    return topic


@router.put("/tenants/{tenant_id}/topics/{topic_id}", response_model=TopicResponse)
async def update_topic(
    tenant_id: str,
    topic_id: str,
    data: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a topic."""
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.tenant_id == tenant_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )
    
    # Partial update - only update provided fields
    if data.name is not None:
        topic.name = data.name
    if data.description is not None:
        topic.description = data.description
    if data.color is not None:
        topic.color = data.color
    if data.icon is not None:
        topic.icon = data.icon
    if data.sort_order is not None:
        topic.sort_order = data.sort_order
    
    db.commit()
    db.refresh(topic)
    
    return topic


@router.delete("/tenants/{tenant_id}/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    tenant_id: str,
    topic_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a topic."""
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.tenant_id == tenant_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )
    
    db.delete(topic)
    db.commit()


# INDUSTRIES ENDPOINTS

@router.get("/tenants/{tenant_id}/industries", response_model=list[IndustryResponse])
async def get_industries(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all industries for a tenant."""
    industries = db.query(Industry).filter(Industry.tenant_id == tenant_id).all()
    return industries


@router.get("/tenants/{tenant_id}/industries/{industry_id}", response_model=IndustryResponse)
async def get_industry(
    tenant_id: str,
    industry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific industry."""
    industry = db.query(Industry).filter(
        Industry.id == industry_id,
        Industry.tenant_id == tenant_id
    ).first()
    
    if not industry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry not found",
        )
    
    return industry


@router.post("/tenants/{tenant_id}/industries", response_model=IndustryResponse, status_code=status.HTTP_201_CREATED)
async def create_industry(
    tenant_id: str,
    data: IndustryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new industry for a tenant."""
    industry = Industry(
        tenant_id=tenant_id,
        name=data.name,
        description=data.description,
        color=data.color,
        icon=data.icon,
    )
    
    db.add(industry)
    db.commit()
    db.refresh(industry)
    
    return industry


@router.put("/tenants/{tenant_id}/industries/{industry_id}", response_model=IndustryResponse)
async def update_industry(
    tenant_id: str,
    industry_id: str,
    data: IndustryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an industry."""
    industry = db.query(Industry).filter(
        Industry.id == industry_id,
        Industry.tenant_id == tenant_id
    ).first()
    
    if not industry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry not found",
        )
    
    # Partial update - only update provided fields
    if data.name is not None:
        industry.name = data.name
    if data.description is not None:
        industry.description = data.description
    if data.color is not None:
        industry.color = data.color
    if data.icon is not None:
        industry.icon = data.icon
    if data.sort_order is not None:
        industry.sort_order = data.sort_order
    
    db.commit()
    db.refresh(industry)
    
    return industry


@router.delete("/tenants/{tenant_id}/industries/{industry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_industry(
    tenant_id: str,
    industry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an industry."""
    industry = db.query(Industry).filter(
        Industry.id == industry_id,
        Industry.tenant_id == tenant_id
    ).first()
    
    if not industry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry not found",
        )
    
    db.delete(industry)
    db.commit()
