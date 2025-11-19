#!/bin/bash

# CI/CD Error Analysis Script
#
# This script downloads error logs from failed GitHub Actions runs
# and formats them for Claude Code to analyze and fix.
#
# Usage:
#   ./scripts/analyze-cicd-errors.sh [run-id]
#   ./scripts/analyze-cicd-errors.sh              # Uses latest failed run
#   ./scripts/analyze-cicd-errors.sh 1234567890   # Uses specific run ID

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo ""
    echo -e "${YELLOW}You have two options:${NC}"
    echo ""
    echo -e "${GREEN}Option 1: Install GitHub CLI (Recommended)${NC}"
    echo "  macOS:   brew install gh"
    echo "  Linux:   sudo apt install gh"
    echo "  Windows: winget install --id GitHub.cli"
    echo "  Or visit: https://cli.github.com/"
    echo ""
    echo -e "${GREEN}Option 2: Use Python version (No installation required)${NC}"
    echo "  Run: python scripts/analyze-cicd-errors.py"
    echo "  Or:  python3 scripts/analyze-cicd-errors.py"
    echo ""
    echo -e "${BLUE}The Python version uses GitHub API directly and doesn't require 'gh' command.${NC}"
    echo ""

    # Try to run Python version automatically
    if command -v python3 &> /dev/null; then
        read -p "Do you want to run the Python version now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 scripts/analyze-cicd-errors.py "$@"
            exit $?
        fi
    fi

    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo -e "${BLUE}Repository: $REPO${NC}"

# Get run ID
if [ -z "$1" ]; then
    echo -e "${YELLOW}No run ID provided. Fetching latest failed run...${NC}"
    RUN_ID=$(gh run list --workflow "CI/CD Pipeline" --status failure --limit 1 --json databaseId -q '.[0].databaseId')

    if [ -z "$RUN_ID" ]; then
        echo -e "${RED}Error: No failed runs found${NC}"
        exit 1
    fi

    echo -e "${GREEN}Using latest failed run: $RUN_ID${NC}"
else
    RUN_ID=$1
    echo -e "${GREEN}Using specified run: $RUN_ID${NC}"
fi

# Get run details
echo -e "${BLUE}Fetching run details...${NC}"
RUN_INFO=$(gh run view $RUN_ID --json headBranch,headSha,conclusion,createdAt,url)

BRANCH=$(echo $RUN_INFO | jq -r .headBranch)
COMMIT=$(echo $RUN_INFO | jq -r .headSha)
STATUS=$(echo $RUN_INFO | jq -r .conclusion)
CREATED_AT=$(echo $RUN_INFO | jq -r .createdAt)
URL=$(echo $RUN_INFO | jq -r .url)

echo -e "${BLUE}Branch: $BRANCH${NC}"
echo -e "${BLUE}Commit: $COMMIT${NC}"
echo -e "${BLUE}Status: ${RED}$STATUS${NC}"
echo -e "${BLUE}Created: $CREATED_AT${NC}"
echo -e "${BLUE}URL: $URL${NC}"

# Create output directory
OUTPUT_DIR="cicd-errors/$RUN_ID"
mkdir -p "$OUTPUT_DIR"

# Download artifacts
echo -e "${YELLOW}Downloading error logs...${NC}"

# Try to download backend errors
if gh run download $RUN_ID --name "backend-error-logs-$RUN_ID" --dir "$OUTPUT_DIR/backend" 2>/dev/null; then
    echo -e "${GREEN}✓ Downloaded backend error logs${NC}"
else
    echo -e "${YELLOW}⚠ No backend error logs found${NC}"
fi

# Try to download frontend errors
if gh run download $RUN_ID --name "frontend-error-logs-$RUN_ID" --dir "$OUTPUT_DIR/frontend" 2>/dev/null; then
    echo -e "${GREEN}✓ Downloaded frontend error logs${NC}"
else
    echo -e "${YELLOW}⚠ No frontend error logs found${NC}"
fi

# Create analysis report
REPORT_FILE="$OUTPUT_DIR/ERROR_ANALYSIS_REPORT.md"

cat > "$REPORT_FILE" <<EOF
# CI/CD Error Analysis Report

**Run ID**: $RUN_ID
**Branch**: $BRANCH
**Commit**: $COMMIT
**Status**: $STATUS
**Created**: $CREATED_AT
**URL**: [$URL]($URL)

---

## Error Summary

EOF

# Analyze backend errors
if [ -d "$OUTPUT_DIR/backend" ]; then
    echo "## 🐍 Backend Errors" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    if [ -f "$OUTPUT_DIR/backend/pytest-errors.log" ]; then
        echo "### Pytest Errors" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo '```python' >> "$REPORT_FILE"
        tail -n 200 "$OUTPUT_DIR/backend/pytest-errors.log" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi

    if [ -f "$OUTPUT_DIR/backend/ruff-errors.log" ]; then
        echo "### Ruff Linter Errors" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        cat "$OUTPUT_DIR/backend/ruff-errors.log" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi

    if [ -f "$OUTPUT_DIR/backend/mypy-errors.log" ]; then
        echo "### MyPy Type Errors" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        cat "$OUTPUT_DIR/backend/mypy-errors.log" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi

    if [ -f "$OUTPUT_DIR/backend/metadata.txt" ]; then
        echo "### Metadata" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        cat "$OUTPUT_DIR/backend/metadata.txt" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
fi

# Analyze frontend errors
if [ -d "$OUTPUT_DIR/frontend" ]; then
    echo "## ⚛️ Frontend Errors" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    if [ -f "$OUTPUT_DIR/frontend/lint-errors.log" ]; then
        echo "### ESLint Errors" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo '```javascript' >> "$REPORT_FILE"
        cat "$OUTPUT_DIR/frontend/lint-errors.log" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi

    if [ -f "$OUTPUT_DIR/frontend/typescript-errors.log" ]; then
        echo "### TypeScript Errors" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo '```typescript' >> "$REPORT_FILE"
        tail -n 200 "$OUTPUT_DIR/frontend/typescript-errors.log" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi

    if [ -f "$OUTPUT_DIR/frontend/build-errors.log" ]; then
        echo "### Build Errors" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        tail -n 200 "$OUTPUT_DIR/frontend/build-errors.log" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi

    if [ -f "$OUTPUT_DIR/frontend/metadata.txt" ]; then
        echo "### Metadata" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        cat "$OUTPUT_DIR/frontend/metadata.txt" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
fi

# Add Claude Code instructions
cat >> "$REPORT_FILE" <<'EOF'

---

## 🤖 Instructions for Claude Code

### Analysis Steps

1. **Identify Error Type**
   - Syntax errors
   - Type errors
   - Test failures
   - Linter violations
   - Build errors

2. **Locate Error Source**
   - File path
   - Line number
   - Function/class name

3. **Determine Root Cause**
   - Missing imports
   - Type mismatches
   - Logic errors
   - Configuration issues

4. **Propose Fix**
   - Specific code changes
   - Configuration updates
   - Dependency additions

### Quick Fix Commands

```bash
# Backend fixes
cd backend
ruff check --fix .
ruff format .
mypy app/
pytest tests/ -v

# Frontend fixes
cd frontend
npm run lint -- --fix
npx tsc --noEmit
npm run build
npm test
```

### After Fixing

1. Run tests locally
2. Commit changes
3. Push to trigger CI/CD
4. Monitor workflow run

---

**Generated**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Tool**: analyze-cicd-errors.sh
EOF

# Print summary
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Error analysis complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Report saved to: ${GREEN}$REPORT_FILE${NC}"
echo ""

# Count errors
BACKEND_ERROR_COUNT=0
FRONTEND_ERROR_COUNT=0

if [ -d "$OUTPUT_DIR/backend" ]; then
    BACKEND_ERROR_COUNT=$(find "$OUTPUT_DIR/backend" -name "*.log" -type f | wc -l)
fi

if [ -d "$OUTPUT_DIR/frontend" ]; then
    FRONTEND_ERROR_COUNT=$(find "$OUTPUT_DIR/frontend" -name "*.log" -type f | wc -l)
fi

echo -e "${BLUE}Error log files found:${NC}"
echo -e "  Backend:  ${RED}$BACKEND_ERROR_COUNT${NC}"
echo -e "  Frontend: ${RED}$FRONTEND_ERROR_COUNT${NC}"
echo ""

# Show quick view
echo -e "${YELLOW}Quick Preview:${NC}"
echo ""
head -n 50 "$REPORT_FILE"
echo ""
echo -e "${YELLOW}... (see full report in $REPORT_FILE)${NC}"
echo ""

# Suggest next steps
echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. ${GREEN}cat $REPORT_FILE${NC} - View full report"
echo -e "  2. ${GREEN}code $REPORT_FILE${NC} - Open in VS Code"
echo -e "  3. Use Claude Code to analyze and fix errors"
echo ""

# Open in default editor if available
if command -v code &> /dev/null; then
    read -p "Open report in VS Code? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        code "$REPORT_FILE"
    fi
fi
