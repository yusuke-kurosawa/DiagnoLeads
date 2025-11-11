#!/bin/bash
# Product Droid - Docker-based Comprehensive Product Check
# Usage: .factory/workflows/product-check-docker.sh [release|qa|metrics]

set -e

COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_RESET='\033[0m'

echo -e "${COLOR_BLUE}🤖 Product Droid - Starting Comprehensive Check (Docker)${COLOR_RESET}"
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

# Check if containers are running
echo -e "${COLOR_YELLOW}Checking Docker containers...${COLOR_RESET}"
docker-compose ps

# Release Readiness Check
if [ "$1" = "release" ] || [ -z "$1" ]; then
    echo ""
    echo -e "${COLOR_BLUE}═══════════════════════════════════════${COLOR_RESET}"
    echo -e "${COLOR_BLUE}🚀 RELEASE READINESS CHECK${COLOR_RESET}"
    echo -e "${COLOR_BLUE}═══════════════════════════════════════${COLOR_RESET}"
    echo ""
    
    run_check "Backend Tests" "docker-compose exec -T backend pytest tests/ --cov=app --cov-report=term-missing" || true
    run_check "Frontend Tests" "docker-compose exec -T frontend npm test -- --run" || true
    run_check "Backend Lint" "docker-compose exec -T backend ruff check app/" || true
    run_check "Frontend Lint" "docker-compose exec -T frontend npm run lint" || true
    run_check "Type Check (Backend)" "docker-compose exec -T backend mypy app/" || true
    run_check "Type Check (Frontend)" "docker-compose exec -T frontend npm run type-check" || true
    run_check "Build Check (Frontend)" "docker-compose exec -T frontend npm run build" || true
    run_check "Security Audit (Frontend)" "docker-compose exec -T frontend npm audit --audit-level=moderate" || true
    
    echo ""
    echo -e "${COLOR_GREEN}✅ Release readiness check completed${COLOR_RESET}"
fi

# Product Metrics
if [ "$1" = "metrics" ]; then
    echo ""
    echo -e "${COLOR_BLUE}═══════════════════════════════════════${COLOR_RESET}"
    echo -e "${COLOR_BLUE}📊 PRODUCT METRICS${COLOR_RESET}"
    echo -e "${COLOR_BLUE}═══════════════════════════════════════${COLOR_RESET}"
    echo ""
    
    echo -e "${COLOR_YELLOW}📈 Test Coverage Summary:${COLOR_RESET}"
    docker-compose exec -T backend pytest tests/ --cov=app --cov-report=term | grep -E "TOTAL|Name" || true
    
    echo ""
    echo -e "${COLOR_YELLOW}📦 Code Statistics (Backend):${COLOR_RESET}"
    docker-compose exec -T backend find app -name "*.py" -type f | wc -l | xargs echo "Python files:"
    docker-compose exec -T backend sh -c "find app -name '*.py' -type f -exec wc -l {} + | tail -1"
    
    echo ""
    echo -e "${COLOR_YELLOW}📦 Code Statistics (Frontend):${COLOR_RESET}"
    docker-compose exec -T frontend find src -name "*.tsx" -o -name "*.ts" | wc -l | xargs echo "TypeScript files:"
    docker-compose exec -T frontend sh -c "find src \( -name '*.tsx' -o -name '*.ts' \) -exec wc -l {} + | tail -1"
    
    echo ""
    echo -e "${COLOR_YELLOW}🐳 Docker Container Status:${COLOR_RESET}"
    docker-compose ps
    
    echo ""
    echo -e "${COLOR_GREEN}✅ Metrics generated${COLOR_RESET}"
fi

echo ""
echo -e "${COLOR_BLUE}════════════════════════════════════════${COLOR_RESET}"
echo -e "${COLOR_GREEN}✨ Product Droid Check Complete!${COLOR_RESET}"
echo -e "${COLOR_BLUE}════════════════════════════════════════${COLOR_RESET}"
