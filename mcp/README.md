# 🔧 MCP (Model Context Protocol) Configuration Hub

This directory contains all MCP server configurations, templates, and setup scripts organized for easy reuse across different projects and environments.

## 📁 Directory Structure

```
mcp/
├── README.md                    # This file
├── configs/                     # MCP server configurations
│   ├── complete/               # Complete configurations with all servers
│   ├── individual/             # Individual server configs
│   └── templates/              # Template configurations
├── keys/                       # API keys and tokens (NEVER commit to git)
│   ├── .env.example           # Template for environment variables
│   ├── github.key.example     # GitHub token template
│   ├── vercel.key.example     # Vercel token template
│   └── supabase.key.example   # Supabase token template
├── scripts/                    # Setup and management scripts
│   ├── setup.sh              # Main setup script
│   ├── install-servers.sh     # Install MCP servers
│   └── validate-config.sh     # Validate configurations
└── docs/                      # Documentation
    ├── setup-guide.md         # Detailed setup guide
    ├── quick-start.md         # Quick setup guide
    └── troubleshooting.md     # Common issues and solutions
```

## 🚀 Quick Start

1. **Get API Tokens:**
   ```bash
   # Copy environment template
   cp mcp/keys/.env.example mcp/keys/.env
   
   # Edit with your actual tokens
   nano mcp/keys/.env
   ```

2. **Run Setup:**
   ```bash
   cd mcp/scripts
   ./setup.sh
   ```

3. **Restart Windsurf** (Cmd+Q, then reopen)

## 🔑 Supported MCP Servers

- **GitHub MCP** - Repository management, code deployment
- **Vercel MCP** - Web application deployment
- **Supabase MCP** - Database operations and queries
- **Railway MCP** - Application hosting and deployment
- **Postman MCP** - API testing, collection management, and documentation
- **MCPify Ninja Trader** - Trading platform integration
- **MCPify Google Places** - Location and search services

## 🛡️ Security Features

- ✅ **Separated Keys** - All API tokens stored separately from configs
- ✅ **Environment Variables** - Secure token management
- ✅ **Template System** - Easy setup without exposing secrets
- ✅ **Gitignore Ready** - Keys directory excluded from version control

## 📚 Usage Examples

After setup, you can use commands like:
- "Deploy my frontend to Vercel"
- "Push code to GitHub"
- "Query the database in Supabase"
- "Deploy to Railway"
- "Import API collection to Postman"
- "Run API tests in Postman"

## 🔧 Customization

Each MCP server can be configured individually. See `configs/individual/` for standalone configurations you can mix and match.
