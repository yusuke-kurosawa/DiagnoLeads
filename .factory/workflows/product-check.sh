#!/bin/bash
# Product Droid - Comprehensive Product Check
# Usage: .factory/workflows/product-check.sh [release|qa|metrics]

set -e

COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_RESET='\033[0m'

echo -e "${COLOR_BLUE}🤖 Product Droid - Starting Comprehensive Check${COLOR_RESET}"
echo ""

# Function to run checks
run_check() {
    local name=$1
    local command=$2
    
    echo -e "${COLOR_YELLOW}▶ Running: ${name}${COLOR_RESET}"
    if eval $command; then
        echo -e "${COLOR_GREEN}✅ ${name}: PASSED${COLOR_RESET}"
        return 0
    else
        echo -e "${COLOR_RED}❌ ${name}: FAILED${COLOR_RESET}"
        return 1
    fi
    echo ""
}

# Release Readiness Check
if [ "$1" = "release" ] || [ -z "$1" ]; then
    echo -e "${COLOR_BLUE}═══════════════════════════════════════${COLOR_RESET}"
    echo -e "${COLOR_BLUE}🚀 RELEASE READINESS CHECK${COLOR_RESET}"
    echo -e "${COLOR_BLUE}═══════════════════════════════════════${COLOR_RESET}"
    echo ""
    
    run_check "Backend Tests" "cd backend && pytest tests/ --cov=app --cov-report=term"
    run_check "Frontend Tests" "cd frontend && npm test -- --run"
    run_check "Backend Lint" "cd backend && ruff check app/"
    run_check "Frontend Lint" "cd frontend && npm run lint"
    run_check "Type Check (Backend)" "cd backend && mypy app/"
    run_check "Type Check (Frontend)" "cd frontend && npm run type-check"
    run_check "Build Check (Frontend)" "cd frontend && npm run build"
    run_check "Security Audit (Frontend)" "cd frontend && npm audit --audit-level=moderate"
    
    echo ""
    echo -e "${COLOR_GREEN}✅ Release readiness check completed${COLOR_RESET}"
fi

# QA Comprehensive Check
if [ "$1" = "qa" ]; then
    echo -e "${COLOR_BLUE}═══════════════════════════════════════${COLOR_RESET}"
    echo -e "${COLOR_BLUE}🔍 COMPREHENSIVE QA CHECK${COLOR_RESET}"
    echo -e "${COLOR_BLUE}═══════════════════════════════════════${COLOR_RESET}"
    echo ""
    
    echo -e "${COLOR_YELLOW}▶ Running E2E Tests...${COLOR_RESET}"
    echo "(E2E test setup required)"
    
    echo -e "${COLOR_YELLOW}▶ Checking Accessibility...${COLOR_RESET}"
    echo "(Accessibility test setup required)"
    
    echo -e "${COLOR_YELLOW}▶ Performance Testing...${COLOR_RESET}"
    echo "(Performance test setup required)"
    
    echo ""
    echo -e "${COLOR_GREEN}✅ QA check completed${COLOR_RESET}"
fi

# Product Metrics
if [ "$1" = "metrics" ]; then
    echo -e "${COLOR_BLUE}═══════════════════════════════════════${COLOR_RESET}"
    echo -e "${COLOR_BLUE}📊 PRODUCT METRICS${COLOR_RESET}"
    echo -e "${COLOR_BLUE}═══════════════════════════════════════${COLOR_RESET}"
    echo ""
    
    echo -e "${COLOR_YELLOW}📈 Test Coverage:${COLOR_RESET}"
    cd backend && pytest tests/ --cov=app --cov-report=term | grep TOTAL || true
    
    echo ""
    echo -e "${COLOR_YELLOW}📦 Code Statistics (Backend):${COLOR_RESET}"
    find backend/app -name "*.py" | xargs wc -l | tail -1
    
    echo ""
    echo -e "${COLOR_YELLOW}📦 Code Statistics (Frontend):${COLOR_RESET}"
    find frontend/src -name "*.tsx" -o -name "*.ts" | xargs wc -l | tail -1
    
    echo ""
    echo -e "${COLOR_YELLOW}🐛 Open Issues:${COLOR_RESET}"
    gh issue list --limit 5 2>/dev/null || echo "GitHub CLI not configured"
    
    echo ""
    echo -e "${COLOR_GREEN}✅ Metrics generated${COLOR_RESET}"
fi

echo ""
echo -e "${COLOR_BLUE}════════════════════════════════════════${COLOR_RESET}"
echo -e "${COLOR_GREEN}✨ Product Droid Check Complete!${COLOR_RESET}"
echo -e "${COLOR_BLUE}════════════════════════════════════════${COLOR_RESET}"
