#!/bin/bash

# CI/CD Error Analysis Tools - Setup Script
#
# このスクリプトはCI/CDエラー解析ツールのセットアップを支援します。
# GitHub CLI (gh) のインストール状況をチェックし、必要に応じてインストールガイドを提供します。

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}CI/CD Error Analysis Tools - Setup${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 環境検出
OS="$(uname -s)"
case "$OS" in
    Linux*)     PLATFORM="Linux";;
    Darwin*)    PLATFORM="macOS";;
    CYGWIN*)    PLATFORM="Windows";;
    MINGW*)     PLATFORM="Windows";;
    MSYS*)      PLATFORM="Windows";;
    *)          PLATFORM="Unknown";;
esac

echo -e "${BLUE}Detected Platform: ${GREEN}$PLATFORM${NC}"
echo ""

# Python チェック
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "  ${GREEN}✓ Python 3 is installed: $PYTHON_VERSION${NC}"
    PYTHON_AVAILABLE=true
else
    echo -e "  ${RED}✗ Python 3 is not installed${NC}"
    PYTHON_AVAILABLE=false
fi
echo ""

# GitHub CLI チェック
echo -e "${YELLOW}Checking GitHub CLI (gh) installation...${NC}"
if command -v gh &> /dev/null; then
    GH_VERSION=$(gh --version | head -n 1)
    echo -e "  ${GREEN}✓ GitHub CLI is installed: $GH_VERSION${NC}"
    GH_AVAILABLE=true

    # 認証状態チェック
    echo ""
    echo -e "${YELLOW}Checking GitHub CLI authentication...${NC}"
    if gh auth status &> /dev/null; then
        echo -e "  ${GREEN}✓ GitHub CLI is authenticated${NC}"
        GH_AUTHENTICATED=true
    else
        echo -e "  ${RED}✗ GitHub CLI is not authenticated${NC}"
        GH_AUTHENTICATED=false
    fi
else
    echo -e "  ${RED}✗ GitHub CLI (gh) is not installed${NC}"
    GH_AVAILABLE=false
    GH_AUTHENTICATED=false
fi
echo ""

# Git チェック
echo -e "${YELLOW}Checking Git installation...${NC}"
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo -e "  ${GREEN}✓ Git is installed: $GIT_VERSION${NC}"
    GIT_AVAILABLE=true
else
    echo -e "  ${RED}✗ Git is not installed${NC}"
    GIT_AVAILABLE=false
fi
echo ""

# サマリー
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Setup Summary${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 推奨セットアップ
echo -e "${BLUE}Available Analysis Methods:${NC}"
echo ""

if [ "$GH_AVAILABLE" = true ] && [ "$GH_AUTHENTICATED" = true ]; then
    echo -e "${GREEN}✓ Method 1: GitHub CLI (Recommended) - READY${NC}"
    echo "  Usage: ./scripts/analyze-cicd-errors.sh"
    echo "  - Easiest to use"
    echo "  - Full featured"
    echo "  - Fast and reliable"
    echo ""
elif [ "$GH_AVAILABLE" = true ]; then
    echo -e "${YELLOW}⚠ Method 1: GitHub CLI - NEEDS AUTHENTICATION${NC}"
    echo "  Run: gh auth login"
    echo "  Then: ./scripts/analyze-cicd-errors.sh"
    echo ""
else
    echo -e "${RED}✗ Method 1: GitHub CLI - NOT INSTALLED${NC}"
    echo ""
    echo "  To install GitHub CLI:"
    echo ""
    case "$PLATFORM" in
        macOS)
            echo "  ${GREEN}Using Homebrew:${NC}"
            echo "    brew install gh"
            echo ""
            ;;
        Linux)
            echo "  ${GREEN}Using apt (Ubuntu/Debian):${NC}"
            echo "    sudo apt update"
            echo "    sudo apt install gh"
            echo ""
            echo "  ${GREEN}Using dnf (Fedora/RHEL):${NC}"
            echo "    sudo dnf install gh"
            echo ""
            ;;
        Windows)
            echo "  ${GREEN}Using winget:${NC}"
            echo "    winget install --id GitHub.cli"
            echo ""
            echo "  ${GREEN}Using scoop:${NC}"
            echo "    scoop install gh"
            echo ""
            ;;
    esac
    echo "  ${GREEN}Or visit:${NC} https://cli.github.com/"
    echo ""
fi

if [ "$PYTHON_AVAILABLE" = true ]; then
    echo -e "${GREEN}✓ Method 2: Python Script - READY${NC}"
    echo "  Usage: python3 scripts/analyze-cicd-errors.py"
    echo "  - No GitHub CLI required"
    echo "  - Uses GitHub API directly"
    echo "  - Requires GITHUB_TOKEN for rate limits"
    echo ""
    echo "  ${YELLOW}To set GITHUB_TOKEN:${NC}"
    echo "    export GITHUB_TOKEN=your_token_here"
    echo "    # Create token at: https://github.com/settings/tokens"
    echo ""
else
    echo -e "${RED}✗ Method 2: Python Script - PYTHON NOT INSTALLED${NC}"
    echo ""
    echo "  To install Python:"
    echo ""
    case "$PLATFORM" in
        macOS)
            echo "  ${GREEN}Using Homebrew:${NC}"
            echo "    brew install python3"
            echo ""
            ;;
        Linux)
            echo "  ${GREEN}Using apt:${NC}"
            echo "    sudo apt install python3"
            echo ""
            ;;
        Windows)
            echo "  ${GREEN}Download from:${NC}"
            echo "    https://www.python.org/downloads/"
            echo ""
            ;;
    esac
fi

# 自動セットアップオプション
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Quick Setup${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# GitHub CLIのインストールと認証を促す
if [ "$GH_AVAILABLE" = false ]; then
    echo -e "${YELLOW}Would you like to install GitHub CLI now?${NC}"
    echo ""

    if [ "$PLATFORM" = "macOS" ] && command -v brew &> /dev/null; then
        read -p "Install with Homebrew? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Installing GitHub CLI...${NC}"
            brew install gh
            echo -e "${GREEN}✓ GitHub CLI installed successfully!${NC}"
            echo ""
            GH_AVAILABLE=true
        fi
    elif [ "$PLATFORM" = "Linux" ] && command -v apt &> /dev/null; then
        echo -e "${YELLOW}To install, run:${NC}"
        echo "  sudo apt update && sudo apt install gh"
        echo ""
    fi
fi

# GitHub CLI認証
if [ "$GH_AVAILABLE" = true ] && [ "$GH_AUTHENTICATED" = false ]; then
    echo -e "${YELLOW}GitHub CLI is installed but not authenticated.${NC}"
    read -p "Do you want to authenticate now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh auth login
        if gh auth status &> /dev/null; then
            echo -e "${GREEN}✓ Authentication successful!${NC}"
            GH_AUTHENTICATED=true
        fi
    fi
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Setup Complete!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 最終推奨
if [ "$GH_AVAILABLE" = true ] && [ "$GH_AUTHENTICATED" = true ]; then
    echo -e "${GREEN}✓ You're all set! Use the bash script for best experience:${NC}"
    echo "  ./scripts/analyze-cicd-errors.sh"
elif [ "$PYTHON_AVAILABLE" = true ]; then
    echo -e "${GREEN}✓ You can use the Python script:${NC}"
    echo "  python3 scripts/analyze-cicd-errors.py"
    echo ""
    echo -e "${YELLOW}Don't forget to set GITHUB_TOKEN for higher rate limits:${NC}"
    echo "  export GITHUB_TOKEN=your_token"
    echo "  # Create at: https://github.com/settings/tokens"
else
    echo -e "${RED}Please install either GitHub CLI or Python 3 to use the error analysis tools.${NC}"
fi

echo ""
echo -e "${BLUE}For more information, see:${NC}"
echo "  docs/cicd-error-auto-fix-usage.md"
echo ""
