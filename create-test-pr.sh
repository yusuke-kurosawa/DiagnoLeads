#!/bin/bash

# CI/CD Error Auto-Fix System - Test PR Creation Script
#
# このスクリプトはPR #35マージ後に実行してください
# 新しいテストPRを作成し、自動修正システムをテストします

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CI/CD Error Auto-Fix System - Test PR Creation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# mainブランチに切り替えて最新を取得
echo "1. Updating main branch..."
git checkout main
git pull origin main

# 新しいテストブランチを作成
BRANCH_NAME="test/cicd-auto-fix-$(date +%Y%m%d-%H%M%S)"
echo "2. Creating new test branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Backendテストファイルを作成
echo "3. Creating backend test file..."
cat > backend/test_cicd_errors.py << 'EOF'
"""
Test file to verify CI/CD error detection system

This file intentionally contains linter errors that should be:
1. Detected by the CI/CD pipeline
2. Captured in error logs
3. Auto-fixed by the auto-fix-linter workflow
4. Commented on the PR by comment-on-failure workflow
"""

# Linter error: unused import (will be auto-fixed)
import os
import sys
import json

# Linter error: unused variable (will be auto-fixed)
unused_variable = "This should be removed"

# Linter error: line too long (will be auto-fixed)
very_long_line_that_exceeds_the_maximum_line_length_and_should_be_wrapped_by_the_formatter_to_comply_with_pep8_standards = "test"


def test_cicd_error_detection():
    """Test function to verify error detection"""
    # Linter error: missing docstring formatting
    x=1+2  # Linter error: no spaces around operators

    # This will pass
    result = x * 2
    assert result == 6

    return result


# Linter error: multiple blank lines at end of file



EOF

# Frontendテストファイルを作成
echo "4. Creating frontend test file..."
cat > frontend/src/testCicdErrors.ts << 'EOF'
// Test file to verify CI/CD error detection system
//
// This file intentionally contains ESLint errors that should be:
// 1. Detected by the CI/CD pipeline
// 2. Captured in error logs
// 3. Auto-fixed by the auto-fix-linter workflow

import { useState, useEffect } from 'react'

// Linter error: unused variable
const unusedVariable = 'This should be removed'

export default function TestCicdErrors() {
    // Linter error: console.log in production
    console.log('This should be removed')

    // Linter error: var instead of const/let
    var oldStyleVariable = 'use let or const'

    // Linter error: missing semicolon
    const x = 'missing semicolon'

    // Linter error: function expression instead of arrow function
    function oldStyleFunction() {
        return 'should use arrow function'
    }

    // Linter error: unnecessary else
    const y = true
    if (y) {
        return <div>Test</div>
    } else {
        return <div>Other</div>
    }
}
EOF

# Git add & commit
echo "5. Committing test files..."
git add backend/test_cicd_errors.py frontend/src/testCicdErrors.ts
git commit -m "test: Add intentional linter errors to verify CI/CD auto-fix system

This commit adds test files with intentional linter errors to verify:
- Error detection in CI/CD pipeline
- Error log capture and artifact upload
- PR auto-comment functionality (comment-on-failure.yml)
- Auto-fix linter workflow (auto-fix-linter.yml)

Expected flow:
1. CI/CD fails with linter errors
2. Error logs captured as artifacts
3. PR receives auto-comment with error details
4. Auto-fix workflow triggers and fixes errors
5. CI/CD re-runs and passes

Test files:
- backend/test_cicd_errors.py (5 types of errors)
- frontend/src/testCicdErrors.ts (8 types of errors)"

# Push
echo "6. Pushing to remote..."
git push -u origin "$BRANCH_NAME"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Test branch created and pushed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Branch: $BRANCH_NAME"
echo ""
echo "Next steps:"
echo "1. Create a PR on GitHub for branch: $BRANCH_NAME"
echo "2. Watch for CI/CD to fail with linter errors"
echo "3. Check for auto-comment on PR"
echo "4. Watch for auto-fix workflow to run"
echo "5. Verify that errors are fixed automatically"
echo "6. Confirm CI/CD passes after auto-fix"
echo ""
echo "PR creation URL:"
echo "https://github.com/yusuke-kurosawa/DiagnoLeads/pull/new/$BRANCH_NAME"
echo ""
