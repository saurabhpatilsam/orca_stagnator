#!/bin/bash

# ============================================================================
# Deployment Script for CSV Upload System
# ============================================================================

echo "🚀 CSV Upload System Deployment"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Railway URL is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Railway backend URL required${NC}"
    echo ""
    echo "Usage: ./deploy.sh <railway-backend-url>"
    echo "Example: ./deploy.sh https://csv-upload-api-production.up.railway.app"
    echo ""
    exit 1
fi

RAILWAY_URL=$1

echo -e "${BLUE}📝 Configuration:${NC}"
echo "Backend URL: $RAILWAY_URL"
echo ""

# Step 1: Update frontend API URL
echo -e "${BLUE}Step 1: Updating frontend API URL...${NC}"
cd frontend

# Create a temporary file with the API URL
cat > src/config.js << EOF
export const API_URL = '${RAILWAY_URL}';
EOF

# Update App.jsx to import config
if ! grep -q "import { API_URL } from './config'" src/App.jsx; then
    # Add import at the top of the file
    sed -i '' "1s/^/import { API_URL } from '.\/config';\n/" src/App.jsx
    
    # Replace fetch URLs
    sed -i '' "s|fetch('/api/upload-tick-data'|fetch(\`\${API_URL}/api/upload-tick-data\`|g" src/App.jsx
fi

echo -e "${GREEN}✅ Frontend API URL updated${NC}"
echo ""

# Step 2: Install dependencies
echo -e "${BLUE}Step 2: Installing frontend dependencies...${NC}"
npm install
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 3: Build frontend
echo -e "${BLUE}Step 3: Building frontend...${NC}"
npm run build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend built successfully${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi
echo ""

# Step 4: Deploy to Vercel
echo -e "${BLUE}Step 4: Deploying to Vercel...${NC}"
if command -v vercel &> /dev/null; then
    vercel --prod
    echo -e "${GREEN}✅ Deployed to Vercel${NC}"
else
    echo -e "${RED}❌ Vercel CLI not installed${NC}"
    echo "Install with: npm install -g vercel"
    echo "Then run: vercel --prod"
fi
echo ""

echo "================================"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Configure your domain in Vercel dashboard"
echo "2. Update DNS records in Hostinger"
echo "3. Test your deployment"
echo ""
echo "Frontend URL: Check Vercel dashboard"
echo "Backend URL: $RAILWAY_URL"
echo ""
