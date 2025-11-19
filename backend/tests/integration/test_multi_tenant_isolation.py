"""
マルチテナント分離の包括的統合テスト

このテストスイートは、マルチテナント環境でのデータ分離を検証します。
テナント間のデータ漏洩を防ぐことは、セキュリティ上最も重要な要件です。

テストカバレッジ:
- Lead（リード）
- Assessment（診断）
- Response（回答）
- QRCode
- Integration（外部連携）
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.lead import Lead
from app.models.tenant import Tenant
from app.models.user import User

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def tenant_alpha(db_session: Session) -> Tenant:
    """テナントAlpha（SaaS企業）"""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Alpha SaaS Co.",
        slug="alpha-saas",
        plan="professional",
        settings={"max_assessments": 10},
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def tenant_beta(db_session: Session) -> Tenant:
    """テナントBeta（コンサル企業）"""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Beta Consulting",
        slug="beta-consulting",
        plan="enterprise",
        settings={"max_assessments": 50},
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def user_alpha(db_session: Session, tenant_alpha: Tenant) -> User:
    """テナントAlphaの管理者ユーザー"""
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_alpha.id,
        email="admin@alpha-saas.com",
        password_hash="$2b$12$hashed_password",
        name="Alpha Admin",
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_beta(db_session: Session, tenant_beta: Tenant) -> User:
    """テナントBetaの管理者ユーザー"""
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_beta.id,
        email="admin@beta-consulting.com",
        password_hash="$2b$12$hashed_password",
        name="Beta Admin",
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def assessment_alpha(db_session: Session, tenant_alpha: Tenant, user_alpha: User) -> Assessment:
    """テナントAlphaの診断"""
    assessment = Assessment(
        id=uuid.uuid4(),
        tenant_id=tenant_alpha.id,
        created_by=user_alpha.id,
        title="SaaS導入診断",
        description="あなたの企業に最適なSaaSツールを診断します",
        status="published",
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)
    return assessment


@pytest.fixture
def assessment_beta(db_session: Session, tenant_beta: Tenant, user_beta: User) -> Assessment:
    """テナントBetaの診断"""
    assessment = Assessment(
        id=uuid.uuid4(),
        tenant_id=tenant_beta.id,
        created_by=user_beta.id,
        title="経営課題診断",
        description="経営課題を可視化します",
        status="published",
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)
    return assessment


@pytest.fixture
def lead_alpha(db_session: Session, tenant_alpha: Tenant, user_alpha: User) -> Lead:
    """テナントAlphaのリード"""
    lead = Lead(
        id=uuid.uuid4(),
        tenant_id=tenant_alpha.id,
        email="customer@example.com",
        name="山田太郎",
        company="株式会社サンプル",
        score=75,
        status="new",
        created_by=user_alpha.id,
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


@pytest.fixture
def lead_beta(db_session: Session, tenant_beta: Tenant, user_beta: User) -> Lead:
    """テナントBetaのリード"""
    lead = Lead(
        id=uuid.uuid4(),
        tenant_id=tenant_beta.id,
        email="client@example.com",
        name="佐藤花子",
        company="株式会社テスト",
        score=85,
        status="new",
        created_by=user_beta.id,
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


# ============================================================================
# テスト: データベースレベルのテナント分離
# ============================================================================


class TestDatabaseLevelIsolation:
    """データベースクエリレベルでのテナント分離検証"""

    def test_assessment_query_isolation(
        self,
        db_session: Session,
        tenant_alpha: Tenant,
        tenant_beta: Tenant,
        assessment_alpha: Assessment,
        assessment_beta: Assessment,
    ):
        """診断クエリがテナントでフィルタリングされることを確認"""
        # テナントAlphaの診断のみを取得
        assessments_alpha = (
            db_session.query(Assessment)
            .filter(Assessment.tenant_id == tenant_alpha.id)
            .all()
        )

        assert len(assessments_alpha) == 1
        assert assessments_alpha[0].id == assessment_alpha.id
        assert assessments_alpha[0].tenant_id == tenant_alpha.id

        # テナントBetaの診断が含まれていないことを確認
        assessment_ids = [a.id for a in assessments_alpha]
        assert assessment_beta.id not in assessment_ids

    def test_lead_query_isolation(
        self,
        db_session: Session,
        tenant_alpha: Tenant,
        tenant_beta: Tenant,
        lead_alpha: Lead,
        lead_beta: Lead,
    ):
        """リードクエリがテナントでフィルタリングされることを確認"""
        # テナントAlphaのリードのみを取得
        leads_alpha = (
            db_session.query(Lead)
            .filter(Lead.tenant_id == tenant_alpha.id)
            .all()
        )

        assert len(leads_alpha) == 1
        assert leads_alpha[0].id == lead_alpha.id
        assert leads_alpha[0].email == "customer@example.com"

        # テナントBetaのリードが含まれていないことを確認
        lead_ids = [lead.id for lead in leads_alpha]
        assert lead_beta.id not in lead_ids

    def test_cross_tenant_access_prevention(
        self,
        db_session: Session,
        tenant_alpha: Tenant,
        tenant_beta: Tenant,
        lead_alpha: Lead,
        lead_beta: Lead,
    ):
        """
        【重要】クロステナントアクセスが防止されることを確認

        テナントAのフィルタでテナントBのデータを取得しようとしても、
        取得できないことを検証
        """
        # テナントAlphaのフィルタでテナントBetaのリードを取得しようとする
        cross_tenant_lead = (
            db_session.query(Lead)
            .filter(Lead.tenant_id == tenant_alpha.id)
            .filter(Lead.id == lead_beta.id)
            .first()
        )

        # None が返されることを確認（データ漏洩なし）
        assert cross_tenant_lead is None

    # NOTE: This test is disabled because Lead model no longer has direct assessment_id
    # Lead is connected to Assessment through Response model (Lead -> Response -> Assessment)
    # def test_join_query_isolation(
    #     self,
    #     db_session: Session,
    #     tenant_alpha: Tenant,
    #     assessment_alpha: Assessment,
    #     lead_alpha: Lead,
    #     lead_beta: Lead,
    # ):
    #     """JOIN クエリでもテナント分離が保たれることを確認"""
    #     # Assessment と Lead を JOIN
    #     results = (
    #         db_session.query(Lead, Assessment)
    #         .join(Assessment, Lead.assessment_id == Assessment.id)
    #         .filter(Assessment.tenant_id == tenant_alpha.id)
    #         .all()
    #     )
    #
    #     # テナントAlphaのリードのみが返される
    #     assert len(results) == 1
    #     lead, assessment = results[0]
    #     assert lead.id == lead_alpha.id
    #     assert assessment.id == assessment_alpha.id
    #
    #     # テナントBetaのリードが含まれていないことを確認
    #     lead_ids = [r[0].id for r in results]
    #     assert lead_beta.id not in lead_ids

    def test_count_query_isolation(
        self,
        db_session: Session,
        tenant_alpha: Tenant,
        tenant_beta: Tenant,
        lead_alpha: Lead,
        lead_beta: Lead,
    ):
        """COUNT クエリでもテナント分離が保たれることを確認"""
        # テナントAlphaのリード数
        count_alpha = (
            db_session.query(Lead)
            .filter(Lead.tenant_id == tenant_alpha.id)
            .count()
        )
        assert count_alpha == 1

        # テナントBetaのリード数
        count_beta = (
            db_session.query(Lead)
            .filter(Lead.tenant_id == tenant_beta.id)
            .count()
        )
        assert count_beta == 1

        # 全体のリード数（両方のテナント）
        total_count = db_session.query(Lead).count()
        assert total_count == 2


# ============================================================================
# テスト: サービス層のテナント分離
# ============================================================================


class TestServiceLayerIsolation:
    """サービス層でのテナント分離検証"""

    def test_lead_service_filters_by_tenant(
        self,
        db_session: Session,
        tenant_alpha: Tenant,
        tenant_beta: Tenant,
        lead_alpha: Lead,
        lead_beta: Lead,
    ):
        """LeadServiceがテナントIDでフィルタリングすることを確認"""
        from app.services.lead_service import LeadService

        service = LeadService(db_session)

        # テナントAlphaのリードを取得
        leads_alpha = service.list_by_tenant(tenant_alpha.id)

        # テナントAlphaのリードのみが返される
        assert len(leads_alpha) == 1
        assert leads_alpha[0].id == lead_alpha.id

        # テナントBetaのリードが含まれていない
        lead_ids = [lead.id for lead in leads_alpha]
        assert lead_beta.id not in lead_ids

    def test_assessment_service_filters_by_tenant(
        self,
        db_session: Session,
        tenant_alpha: Tenant,
        assessment_alpha: Assessment,
        assessment_beta: Assessment,
    ):
        """AssessmentServiceがテナントIDでフィルタリングすることを確認"""
        from app.services.assessment_service import AssessmentService

        service = AssessmentService(db_session)

        # テナントAlphaの診断を取得
        assessments_alpha = service.list_by_tenant(tenant_alpha.id)

        # テナントAlphaの診断のみが返される
        assert len(assessments_alpha) == 1
        assert assessments_alpha[0].id == assessment_alpha.id

        # テナントBetaの診断が含まれていない
        assessment_ids = [a.id for a in assessments_alpha]
        assert assessment_beta.id not in assessment_ids


# ============================================================================
# テスト: APIエンドポイントレベルのテナント分離
# ============================================================================


class TestAPIEndpointIsolation:
    """APIエンドポイントでのテナント分離検証"""

    def test_get_leads_returns_only_tenant_data(
        self,
        client: TestClient,
        tenant_alpha: Tenant,
        user_alpha: User,
        lead_alpha: Lead,
        lead_beta: Lead,
    ):
        """GET /api/v1/leads がテナントのデータのみを返すことを確認"""
        # テナントAlphaのユーザーとしてログイン
        # （実際のテストでは、認証ヘッダーを設定）
        headers = {"Authorization": f"Bearer {create_test_token(user_alpha)}"}

        response = client.get("/api/v1/leads", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # テナントAlphaのリードのみが返される
        assert len(data) == 1
        assert data[0]["id"] == str(lead_alpha.id)

        # テナントBetaのリードが含まれていない
        lead_ids = [item["id"] for item in data]
        assert str(lead_beta.id) not in lead_ids

    def test_get_lead_by_id_prevents_cross_tenant_access(
        self,
        client: TestClient,
        user_alpha: User,
        lead_beta: Lead,
    ):
        """
        【重要】GET /api/v1/leads/{id} がクロステナントアクセスを防ぐことを確認

        テナントAlphaのユーザーがテナントBetaのリードIDを指定しても、
        403 Forbidden が返されることを検証
        """
        headers = {"Authorization": f"Bearer {create_test_token(user_alpha)}"}

        # テナントBetaのリードIDを指定
        response = client.get(f"/api/v1/leads/{lead_beta.id}", headers=headers)

        # 403 Forbidden または 404 Not Found が返される
        assert response.status_code in [403, 404]


# ============================================================================
# テスト: 更新・削除操作でのテナント分離
# ============================================================================


class TestMutationOperationIsolation:
    """更新・削除操作でのテナント分離検証"""

    def test_update_lead_prevents_cross_tenant_modification(
        self,
        client: TestClient,
        user_alpha: User,
        lead_beta: Lead,
    ):
        """
        【重要】PUT /api/v1/leads/{id} がクロステナント更新を防ぐことを確認
        """
        headers = {"Authorization": f"Bearer {create_test_token(user_alpha)}"}

        # テナントBetaのリードを更新しようとする
        update_data = {"status": "contacted"}
        response = client.put(
            f"/api/v1/leads/{lead_beta.id}",
            json=update_data,
            headers=headers,
        )

        # 403 Forbidden または 404 Not Found が返される
        assert response.status_code in [403, 404]

    def test_delete_lead_prevents_cross_tenant_deletion(
        self,
        client: TestClient,
        db_session: Session,
        user_alpha: User,
        lead_beta: Lead,
    ):
        """
        【重要】DELETE /api/v1/leads/{id} がクロステナント削除を防ぐことを確認
        """
        headers = {"Authorization": f"Bearer {create_test_token(user_alpha)}"}

        # テナントBetaのリードを削除しようとする
        response = client.delete(f"/api/v1/leads/{lead_beta.id}", headers=headers)

        # 403 Forbidden または 404 Not Found が返される
        assert response.status_code in [403, 404]

        # データベースでリードがまだ存在することを確認
        db_lead = db_session.query(Lead).filter(Lead.id == lead_beta.id).first()
        assert db_lead is not None


# ============================================================================
# ヘルパー関数
# ============================================================================


def create_test_token(user: User) -> str:
    """テスト用のJWTトークンを生成"""
    from app.services.auth import AuthService

    return AuthService.create_access_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id)}
    )


# ============================================================================
# パフォーマンステスト
# ============================================================================


class TestTenantIsolationPerformance:
    """大量データでのテナント分離パフォーマンス検証"""

    def test_isolation_with_large_dataset(self, db_session: Session):
        """
        大量データがあってもテナント分離が正しく機能することを確認
        （パフォーマンス低下がないか）
        """
        # 複数のテナントとユーザーを作成
        from app.models.user import User
        from app.services.auth import AuthService

        tenants = []
        users = []
        for i in range(10):
            tenant = Tenant(
                id=uuid.uuid4(),
                name=f"Tenant {i}",
                slug=f"tenant-{i}",
                plan="free",
                settings={},
            )
            db_session.add(tenant)
            db_session.flush()  # tenant.idを取得するため

            user = User(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                email=f"user{i}@tenant-{i}.com",
                password_hash=AuthService.hash_password("password"),
                name=f"User {i}",
                role="tenant_admin",
            )
            db_session.add(user)
            tenants.append(tenant)
            users.append(user)

        db_session.commit()

        # 各テナントに100個のリードを作成
        for tenant, user in zip(tenants, users):
            for j in range(100):
                lead = Lead(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    email=f"lead{j}@tenant{tenant.slug}.com",
                    name=f"Lead {j}",
                    score=50,
                    status="new",
                    created_by=user.id,
                )
                db_session.add(lead)

        db_session.commit()

        # 特定のテナントのリードのみを取得
        target_tenant = tenants[5]
        import time

        start = time.time()
        leads = (
            db_session.query(Lead)
            .filter(Lead.tenant_id == target_tenant.id)
            .all()
        )
        elapsed = time.time() - start

        # 正確に100件が返される
        assert len(leads) == 100

        # すべてのリードが同じテナントに属している
        for lead in leads:
            assert lead.tenant_id == target_tenant.id

        # パフォーマンス要件: 1秒以内
        assert elapsed < 1.0
