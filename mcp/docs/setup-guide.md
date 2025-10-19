# 🔧 MCP Servers Detailed Setup Guide

Complete guide for setting up all MCP servers with separated keys and modular configurations.

## 📋 Overview

This setup provides:
- ✅ **Separated API Keys** - Secure token management
- ✅ **Modular Configs** - Individual server configurations
- ✅ **Template System** - Easy setup and customization
- ✅ **Automated Scripts** - One-command setup

## 🎯 Supported MCP Servers

### Core Servers
- **GitHub MCP** - Repository management, code deployment
- **Vercel MCP** - Web application deployment  
- **Supabase MCP** - Database operations and queries
- **Railway MCP** - Application hosting and deployment

### Extended Servers
- **MCPify Ninja Trader** - Trading platform integration
- **MCPify Google Places** - Location and search services

## 🚀 Installation Steps

### Step 1: Install MCP Server Packages

```bash
cd mcp/scripts
./install-servers.sh
```

This installs:
- `@supabase/mcp-server-supabase@latest`
- `@railway/mcp-server`
- `@composio/mcp@latest`

### Step 2: Configure Environment Variables

```bash
# Copy the environment template
cp mcp/keys/.env.example mcp/keys/.env

# Edit with your actual tokens
nano mcp/keys/.env
```

### Step 3: Get API Tokens

#### GitHub Token
1. Visit: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `Windsurf MCP`
4. Scopes: Select all `repo` permissions
5. Click "Generate token"
6. Copy token (starts with `ghp_` or `github_pat_`)

#### Vercel Token
1. Visit: https://vercel.com/account/tokens
2. Click "Create Token"
3. Name: `Windsurf MCP`
4. Scope: Full Account
5. Click "Create"
6. Copy the token

#### Supabase Token
1. Visit: https://supabase.com/dashboard/account/tokens
2. Click "Generate new token"
3. Name: `Windsurf MCP`
4. Click "Generate token"
5. Copy token (starts with `sbp_`)

#### Railway Token (Optional)
1. Visit: https://railway.app/account/tokens
2. Click "Create token"
3. Name: `Windsurf MCP`
4. Copy the token

### Step 4: Run Setup Script

```bash
cd mcp/scripts
./setup.sh
```

The setup script will:
1. Load your environment variables
2. Validate all required tokens
3. Let you choose configuration type:
   - **Complete** - All MCP servers
   - **Minimal** - Core servers only (GitHub, Vercel, Supabase)
   - **Custom** - Select individual servers
4. Generate final configuration
5. Install to Windsurf config directory

### Step 5: Restart Windsurf

1. **Quit Windsurf completely** (Cmd+Q)
2. **Reopen Windsurf**
3. **Start a new chat session**

## 🔍 Validation

Validate your setup:

```bash
cd mcp/scripts
./validate-config.sh
```

This checks:
- Configuration file exists and is valid JSON
- All MCP servers are properly configured
- Token placeholders are resolved

## 📁 Directory Structure

```
mcp/
├── configs/
│   ├── individual/          # Single server configs
│   │   ├── github-mcp.json
│   │   ├── vercel-mcp.json
│   │   ├── supabase-mcp.json
│   │   ├── railway-mcp.json
│   │   ├── mcpify-ninja-trader.json
│   │   └── mcpify-google-places.json
│   └── templates/           # Complete configurations
│       ├── complete-mcp-template.json
│       └── minimal-mcp-template.json
├── keys/                    # API tokens (gitignored)
│   ├── .env.example        # Environment template
│   └── .gitignore          # Security exclusions
├── scripts/                 # Setup and utility scripts
│   ├── setup.sh            # Main setup script
│   ├── install-servers.sh  # Install MCP packages
│   └── validate-config.sh  # Validate configuration
└── docs/                   # Documentation
    ├── quick-start.md      # Quick setup guide
    ├── setup-guide.md      # This file
    └── troubleshooting.md  # Common issues
```

## 🔧 Customization

### Using Individual Configurations

You can mix and match individual server configs:

```bash
# Copy individual configs to create custom setup
cp mcp/configs/individual/github-mcp.json /tmp/my-config.json
# Merge other configs as needed
```

### Environment Variables

All configurations use environment variables for tokens:
- `${GITHUB_TOKEN}` - GitHub API token
- `${VERCEL_TOKEN}` - Vercel API token  
- `${SUPABASE_TOKEN}` - Supabase access token
- `${RAILWAY_TOKEN}` - Railway API token (optional)

### Adding New Servers

1. Create individual config in `configs/individual/`
2. Add to template in `configs/templates/`
3. Update environment template if new tokens needed
4. Update setup script for validation

## 🛡️ Security Features

### Token Separation
- All API tokens stored in separate `keys/` directory
- Environment variables used in configurations
- Keys directory excluded from git via `.gitignore`

### Template System
- Configurations use `${TOKEN}` placeholders
- `envsubst` replaces placeholders during setup
- No hardcoded tokens in configuration files

### Backup System
- Existing configurations backed up before replacement
- Timestamped backup files for recovery

## 📚 Usage Examples

After successful setup, you can use these commands:

### GitHub Operations
- "Push my code to GitHub"
- "Create a new repository"
- "Create a pull request"
- "List my repositories"

### Vercel Deployments
- "Deploy my frontend to Vercel"
- "Show my Vercel deployments"
- "Configure domain for my project"
- "View deployment logs"

### Supabase Database
- "Query the users table"
- "Show database schema"
- "Run this SQL query"
- "Create a new table"

### Railway Hosting
- "Deploy to Railway"
- "Show my Railway projects"
- "View application logs"
- "Manage environment variables"

## 🆘 Troubleshooting

See `troubleshooting.md` for common issues and solutions.

## 🔄 Updates

To update MCP servers:

```bash
# Update packages
cd mcp/scripts
./install-servers.sh

# Rerun setup if needed
./setup.sh
```
