#!/bin/bash

# ============================================================================
# GitHub Repository Setup Script
# ============================================================================
# This script will:
# 1. Create .gitignore
# 2. Initialize git repository
# 3. Add and commit all files
# 4. Create GitHub repository (using gh CLI)
# 5. Push code to GitHub
# ============================================================================

set -e  # Exit on error

echo "🚀 Setting up GitHub repository: Orca_stagnator"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo ""
    echo "Install with:"
    echo "  brew install gh"
    echo ""
    echo "Or use manual method (see README_DEPLOYMENT.md)"
    exit 1
fi

# Check if logged in to GitHub
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to GitHub${NC}"
    echo ""
    echo "Logging in to GitHub..."
    gh auth login
fi

echo -e "${GREEN}✅ GitHub CLI ready${NC}"
echo ""

# Step 1: Create .gitignore
echo -e "${BLUE}Step 1: Creating .gitignore...${NC}"
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
*.log
*.pyc

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
dist/
build/
frontend/dist/
frontend/node_modules/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Temp files
*.tmp
*.temp
temp/
tmp/

# Sensitive data
.env.local
.env.production
*.pem
*.key
*_with_duplicates

# Test files
test_*.py
*_test.py

# Backup files
*.backup
*.bak
*_backup.*
EOF

echo -e "${GREEN}✅ .gitignore created${NC}"
echo ""

# Step 2: Initialize git
echo -e "${BLUE}Step 2: Initializing git repository...${NC}"
if [ ! -d .git ]; then
    git init
    echo -e "${GREEN}✅ Git initialized${NC}"
else
    echo -e "${YELLOW}⚠️  Git already initialized${NC}"
fi
echo ""

# Step 3: Add all files
echo -e "${BLUE}Step 3: Adding files to git...${NC}"
git add .
echo -e "${GREEN}✅ Files added${NC}"
echo ""

# Step 4: Commit
echo -e "${BLUE}Step 4: Creating initial commit...${NC}"
git commit -m "Initial commit: CSV Upload System

Features:
- React frontend with drag-and-drop UI
- FastAPI backend for CSV uploads
- Supabase integration with duplicate detection
- Automatic deployment to Vercel + Railway
- Support for ES/NQ tick-by-tick data
- Real-time progress tracking
- Mobile responsive design

Tech stack:
- Frontend: React + Vite
- Backend: FastAPI + Python
- Database: Supabase (PostgreSQL)
- Deployment: Vercel (frontend) + Railway (backend)
"
echo -e "${GREEN}✅ Initial commit created${NC}"
echo ""

# Step 5: Create GitHub repository
echo -e "${BLUE}Step 5: Creating GitHub repository...${NC}"
gh repo create Orca_stagnator \
    --public \
    --source=. \
    --remote=origin \
    --description="CSV Upload System - Tick Data Management for Supabase (ES/NQ)" \
    --push

echo ""
echo "================================================"
echo -e "${GREEN}🎉 Success! Repository created and code pushed!${NC}"
echo "================================================"
echo ""
echo "Repository URL:"
gh repo view --web --json url -q .url
echo ""
echo "Next steps:"
echo "1. Deploy backend to Railway:"
echo "   - Go to https://railway.app"
echo "   - Click 'New Project' → 'Deploy from GitHub'"
echo "   - Select 'Orca_stagnator' repository"
echo ""
echo "2. Deploy frontend to Vercel:"
echo "   - Run: ./deploy.sh <your-railway-url>"
echo ""
echo "3. Configure domain in Vercel dashboard"
echo ""
echo "See DEPLOY_SUMMARY.md for detailed instructions!"
echo ""
