"""
A/B Test API Endpoints

REST API for AI-powered A/B testing with Thompson Sampling.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field, validator

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.ab_test import ABTest, ABTestVariant, ABTestStatus, ABTestType
from app.services.thompson_sampling import ThompsonSamplingEngine


router = APIRouter()


# Schemas
class ABTestVariantCreate(BaseModel):
    """A/B test variant creation"""
    name: str = Field(..., max_length=50, description="Variant name (A, B, Control, etc.)")
    description: Optional[str] = None
    is_control: bool = Field(default=False, description="Is this the control variant?")
    config: dict = Field(default={}, description="Variant configuration")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Variant A - Red Button",
                "is_control": False,
                "config": {
                    "cta_text": "今すぐ診断開始",
                    "cta_color": "#FF5722"
                }
            }
        }


class ABTestCreate(BaseModel):
    """A/B test creation"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    assessment_id: UUID
    test_type: ABTestType = ABTestType.CUSTOM
    variants: List[ABTestVariantCreate] = Field(..., min_items=2, max_items=10)
    traffic_allocation: float = Field(default=1.0, ge=0.0, le=1.0)
    min_sample_size: int = Field(default=100, ge=10)
    confidence_threshold: float = Field(default=0.95, ge=0.90, le=0.99)
    exploration_rate: float = Field(default=0.1, ge=0.0, le=1.0)

    @validator("variants")
    def validate_variants(cls, v):
        if len(v) < 2:
            raise ValueError("At least 2 variants required")
        # Check for exactly one control variant
        control_count = sum(1 for var in v if var.is_control)
        if control_count > 1:
            raise ValueError("Only one control variant allowed")
        return v


class ABTestResponse(BaseModel):
    """A/B test response"""
    id: UUID
    name: str
    description: Optional[str]
    assessment_id: UUID
    test_type: ABTestType
    status: ABTestStatus
    total_impressions: int
    total_conversions: int
    overall_conversion_rate: float
    winner_variant_id: Optional[UUID]
    created_at: str

    class Config:
        from_attributes = True


class VariantSelectionResponse(BaseModel):
    """Selected variant for impression"""
    variant_id: UUID
    variant_name: str
    config: dict
    thompson_score: float


class ConversionRecordRequest(BaseModel):
    """Record conversion"""
    variant_id: UUID
    session_id: Optional[str] = None


# API Endpoints
@router.post(
    "/tenants/{tenant_id}/ab-tests",
    response_model=ABTestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create A/B Test",
    operation_id="createABTest",
)
async def create_ab_test(
    tenant_id: UUID,
    test_data: ABTestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new A/B test with variants"""
    # Permission check
    if current_user.tenant_id != tenant_id and current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    # Create A/B test
    ab_test = ABTest(
        tenant_id=tenant_id,
        assessment_id=test_data.assessment_id,
        created_by=current_user.id,
        name=test_data.name,
        description=test_data.description,
        test_type=test_data.test_type,
        traffic_allocation=test_data.traffic_allocation,
        min_sample_size=test_data.min_sample_size,
        confidence_threshold=test_data.confidence_threshold,
        exploration_rate=test_data.exploration_rate,
        status=ABTestStatus.DRAFT
    )

    db.add(ab_test)
    db.flush()  # Get ab_test.id

    # Create variants
    num_variants = len(test_data.variants)
    initial_allocation = 1.0 / num_variants

    for variant_data in test_data.variants:
        variant = ABTestVariant(
            ab_test_id=ab_test.id,
            tenant_id=tenant_id,
            name=variant_data.name,
            description=variant_data.description,
            is_control=variant_data.is_control,
            config=variant_data.config,
            current_traffic_allocation=initial_allocation
        )
        db.add(variant)

    db.commit()
    db.refresh(ab_test)

    return ABTestResponse(
        id=ab_test.id,
        name=ab_test.name,
        description=ab_test.description,
        assessment_id=ab_test.assessment_id,
        test_type=ab_test.test_type,
        status=ab_test.status,
        total_impressions=ab_test.total_impressions,
        total_conversions=ab_test.total_conversions,
        overall_conversion_rate=ab_test.overall_conversion_rate,
        winner_variant_id=ab_test.winner_variant_id,
        created_at=ab_test.created_at.isoformat()
    )


@router.post(
    "/tenants/{tenant_id}/ab-tests/{test_id}/start",
    summary="Start A/B Test",
    operation_id="startABTest",
)
async def start_ab_test(
    tenant_id: UUID,
    test_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start running an A/B test"""
    # Get test
    ab_test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.tenant_id == tenant_id
    ).first()

    if not ab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )

    if ab_test.status == ABTestStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test is already running"
        )

    # Start test
    ab_test.status = ABTestStatus.RUNNING
    ab_test.started_at = func.now()
    db.commit()

    return {"status": "success", "message": "A/B test started", "test_id": str(test_id)}


@router.get(
    "/tenants/{tenant_id}/ab-tests/{test_id}/select-variant",
    response_model=VariantSelectionResponse,
    summary="Select Variant (Thompson Sampling)",
    operation_id="selectVariant",
)
async def select_variant(
    tenant_id: UUID,
    test_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Select a variant using Thompson Sampling.

    This endpoint is called when showing the assessment to a user.
    """
    # Get test
    ab_test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.tenant_id == tenant_id,
        ABTest.status == ABTestStatus.RUNNING
    ).first()

    if not ab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active A/B test not found"
        )

    # Get variants
    variants = db.query(ABTestVariant).filter(
        ABTestVariant.ab_test_id == test_id
    ).all()

    if not variants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No variants found for this test"
        )

    # Prepare variant data for Thompson Sampling
    variants_data = [
        {
            "id": str(v.id),
            "name": v.name,
            "alpha": v.alpha,
            "beta": v.beta,
            "impressions": v.impressions,
            "conversions": v.conversions
        }
        for v in variants
    ]

    # Select variant using Thompson Sampling
    engine = ThompsonSamplingEngine(exploration_rate=ab_test.exploration_rate)
    selected_id, thompson_score = engine.select_variant(variants_data)

    # Find selected variant
    selected_variant = next(v for v in variants if str(v.id) == selected_id)

    # Record impression
    selected_variant.impressions += 1
    selected_variant.thompson_score = thompson_score
    selected_variant.update_statistics()

    ab_test.total_impressions += 1

    db.commit()

    return VariantSelectionResponse(
        variant_id=selected_variant.id,
        variant_name=selected_variant.name,
        config=selected_variant.config,
        thompson_score=thompson_score
    )


@router.post(
    "/tenants/{tenant_id}/ab-tests/{test_id}/record-conversion",
    summary="Record Conversion",
    operation_id="recordConversion",
)
async def record_conversion(
    tenant_id: UUID,
    test_id: UUID,
    conversion_data: ConversionRecordRequest,
    db: Session = Depends(get_db),
):
    """Record a successful conversion for a variant"""
    # Get variant
    variant = db.query(ABTestVariant).filter(
        ABTestVariant.id == conversion_data.variant_id,
        ABTestVariant.ab_test_id == test_id,
        ABTestVariant.tenant_id == tenant_id
    ).first()

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )

    # Get test
    ab_test = db.query(ABTest).filter(ABTest.id == test_id).first()

    # Record conversion
    variant.conversions += 1
    variant.update_statistics()

    ab_test.total_conversions += 1
    if ab_test.total_impressions > 0:
        ab_test.overall_conversion_rate = ab_test.total_conversions / ab_test.total_impressions

    db.commit()

    return {
        "status": "success",
        "variant_id": str(variant.id),
        "conversions": variant.conversions,
        "conversion_rate": variant.conversion_rate
    }


@router.get(
    "/tenants/{tenant_id}/ab-tests/{test_id}/results",
    summary="Get A/B Test Results",
    operation_id="getABTestResults",
)
async def get_ab_test_results(
    tenant_id: UUID,
    test_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive A/B test results and analysis"""
    # Get test
    ab_test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.tenant_id == tenant_id
    ).first()

    if not ab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )

    # Get variants
    variants = db.query(ABTestVariant).filter(
        ABTestVariant.ab_test_id == test_id
    ).all()

    # Prepare data for analysis
    variants_data = [
        {
            "id": str(v.id),
            "name": v.name,
            "alpha": v.alpha,
            "beta": v.beta,
            "impressions": v.impressions,
            "conversions": v.conversions,
            "conversion_rate": v.conversion_rate
        }
        for v in variants
    ]

    # Run Thompson Sampling analysis
    engine = ThompsonSamplingEngine(exploration_rate=ab_test.exploration_rate)

    # Calculate traffic allocation
    traffic_allocation = engine.calculate_traffic_allocation(
        variants=variants_data,
        min_sample_size=ab_test.min_sample_size
    )

    # Determine winner
    winner_analysis = engine.determine_winner(
        variants=variants_data,
        confidence_threshold=ab_test.confidence_threshold,
        min_sample_size=ab_test.min_sample_size
    )

    # Calculate expected loss
    expected_losses = engine.calculate_expected_loss(variants_data)

    # Get detailed statistics for each variant
    variant_stats = []
    for v in variants:
        stats = engine.get_variant_statistics(
            alpha=v.alpha,
            beta=v.beta,
            impressions=v.impressions,
            conversions=v.conversions,
            confidence=ab_test.confidence_threshold
        )
        stats["id"] = str(v.id)
        stats["name"] = v.name
        stats["is_control"] = v.is_control
        stats["traffic_allocation"] = traffic_allocation.get(str(v.id), 0.0)
        stats["expected_loss"] = expected_losses.get(str(v.id), 0.0)
        variant_stats.append(stats)

    return {
        "test_id": str(test_id),
        "test_name": ab_test.name,
        "status": ab_test.status,
        "total_impressions": ab_test.total_impressions,
        "total_conversions": ab_test.total_conversions,
        "overall_conversion_rate": ab_test.overall_conversion_rate,
        "winner_analysis": winner_analysis,
        "variants": variant_stats,
        "traffic_allocation": traffic_allocation
    }


@router.post(
    "/tenants/{tenant_id}/ab-tests/{test_id}/complete",
    summary="Complete A/B Test",
    operation_id="completeABTest",
)
async def complete_ab_test(
    tenant_id: UUID,
    test_id: UUID,
    force: bool = Query(default=False, description="Force completion without winner"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Complete an A/B test and declare winner"""
    # Get test
    ab_test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.tenant_id == tenant_id
    ).first()

    if not ab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )

    # Get variants
    variants = db.query(ABTestVariant).filter(
        ABTestVariant.ab_test_id == test_id
    ).all()

    variants_data = [
        {
            "id": str(v.id),
            "name": v.name,
            "alpha": v.alpha,
            "beta": v.beta,
            "impressions": v.impressions,
            "conversions": v.conversions,
            "conversion_rate": v.conversion_rate
        }
        for v in variants
    ]

    # Determine winner
    engine = ThompsonSamplingEngine()
    winner_analysis = engine.determine_winner(
        variants=variants_data,
        confidence_threshold=ab_test.confidence_threshold,
        min_sample_size=ab_test.min_sample_size
    )

    if not winner_analysis["has_winner"] and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "No statistically significant winner yet",
                "analysis": winner_analysis,
                "hint": "Use force=true to complete anyway"
            }
        )

    # Mark as completed
    ab_test.status = ABTestStatus.COMPLETED
    ab_test.completed_at = func.now()

    if winner_analysis["has_winner"]:
        ab_test.winner_variant_id = UUID(winner_analysis["winner_id"])

    db.commit()

    return {
        "status": "success",
        "message": "A/B test completed",
        "winner_analysis": winner_analysis
    }


@router.get(
    "/tenants/{tenant_id}/ab-tests",
    response_model=List[ABTestResponse],
    summary="List A/B Tests",
    operation_id="listABTests",
)
async def list_ab_tests(
    tenant_id: UUID,
    assessment_id: Optional[UUID] = None,
    status: Optional[ABTestStatus] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all A/B tests for tenant"""
    # Build query
    query = db.query(ABTest).filter(ABTest.tenant_id == tenant_id)

    if assessment_id:
        query = query.filter(ABTest.assessment_id == assessment_id)

    if status:
        query = query.filter(ABTest.status == status)

    tests = query.order_by(ABTest.created_at.desc()).offset(skip).limit(limit).all()

    return [
        ABTestResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            assessment_id=t.assessment_id,
            test_type=t.test_type,
            status=t.status,
            total_impressions=t.total_impressions,
            total_conversions=t.total_conversions,
            overall_conversion_rate=t.overall_conversion_rate,
            winner_variant_id=t.winner_variant_id,
            created_at=t.created_at.isoformat()
        )
        for t in tests
    ]
