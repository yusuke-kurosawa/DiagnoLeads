#!/bin/bash
#
# テスト環境セットアップスクリプト
#
# このスクリプトは、DiagnoLeadsプロジェクトのテスト環境をセットアップします。
# バックエンドとフロントエンドの両方のテスト環境を準備します。
#

set -e  # エラー時に終了

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

log_info "DiagnoLeads テスト環境セットアップを開始します..."

# ==============================================================================
# バックエンドのセットアップ
# ==============================================================================

log_info "バックエンドのテスト環境をセットアップ中..."

cd backend

# 仮想環境の確認
if [ ! -d "venv" ]; then
    log_warn "仮想環境が見つかりません。作成します..."
    python3 -m venv venv
fi

# 仮想環境の有効化
source venv/bin/activate

# 依存関係のインストール
log_info "バックエンドの依存関係をインストール中..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# テスト用環境変数の設定
if [ ! -f ".env.test" ]; then
    log_info "テスト用環境変数ファイルを作成中..."
    cat > .env.test << EOF
# テスト環境の環境変数
ENVIRONMENT=test
DEBUG=True

# Database (テスト用)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/diagnoleads_test

# Redis (テスト用)
REDIS_URL=redis://localhost:6379/1

# JWT
SECRET_KEY=test-secret-key-$(openssl rand -hex 16)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Anthropic Claude API (テスト時はモック使用)
ANTHROPIC_API_KEY=sk-ant-test-key

# 外部連携 (テスト時は無効)
SALESFORCE_CLIENT_ID=
SALESFORCE_CLIENT_SECRET=
EOF
    log_info ".env.test ファイルを作成しました"
fi

# PostgreSQL接続確認
log_info "PostgreSQLへの接続を確認中..."
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    log_info "PostgreSQLが実行中です"

    # テストデータベースの作成
    log_info "テストデータベースを作成中..."
    psql -U postgres -h localhost -c "DROP DATABASE IF EXISTS diagnoleads_test;" || true
    psql -U postgres -h localhost -c "CREATE DATABASE diagnoleads_test;"
    log_info "テストデータベースを作成しました"
else
    log_warn "PostgreSQLが実行されていません"
    log_warn "手動で起動してください: sudo systemctl start postgresql"
    log_warn "または Docker を使用してください: docker-compose up -d postgres"
fi

# Redisの接続確認
log_info "Redisへの接続を確認中..."
if redis-cli ping > /dev/null 2>&1; then
    log_info "Redisが実行中です"
else
    log_warn "Redisが実行されていません"
    log_warn "手動で起動してください: sudo systemctl start redis"
    log_warn "または Docker を使用してください: docker-compose up -d redis"
fi

log_info "バックエンドのセットアップ完了"

cd ..

# ==============================================================================
# フロントエンドのセットアップ
# ==============================================================================

log_info "フロントエンドのテスト環境をセットアップ中..."

cd frontend

# Node.jsのバージョン確認
NODE_VERSION=$(node -v)
log_info "Node.jsバージョン: $NODE_VERSION"

# 依存関係のインストール
if [ ! -d "node_modules" ]; then
    log_info "フロントエンドの依存関係をインストール中..."
    npm install
else
    log_info "node_modulesが存在します。スキップ..."
fi

log_info "フロントエンドのセットアップ完了"

cd ..

# ==============================================================================
# 最終確認
# ==============================================================================

log_info ""
log_info "========================================="
log_info "テスト環境のセットアップが完了しました！"
log_info "========================================="
log_info ""
log_info "次のステップ:"
log_info "1. バックエンドのテストを実行:"
log_info "   cd backend && source venv/bin/activate && pytest"
log_info ""
log_info "2. フロントエンドのテストを実行:"
log_info "   cd frontend && npm test"
log_info ""
log_info "3. マルチテナント分離テストを実行:"
log_info "   cd backend && source venv/bin/activate && pytest tests/integration/test_multi_tenant_isolation.py -v"
log_info ""
log_info "詳細なテスト方法は docs/DEVELOPER_GUIDE.md を参照してください"
log_info ""
