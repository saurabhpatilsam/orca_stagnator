# 📋 MCP Configuration Index

Complete inventory of all MCP servers, configurations, and keys in this repository.

## 🗂️ Available MCP Servers

### Core Development Servers
| Server | Purpose | Config File | Requires Token |
|--------|---------|-------------|----------------|
| **GitHub MCP** | Repository management, code deployment | `configs/individual/github-mcp.json` | ✅ GitHub Token |
| **Vercel MCP** | Web application deployment | `configs/individual/vercel-mcp.json` | ✅ Vercel Token |
| **Supabase MCP** | Database operations and queries | `configs/individual/supabase-mcp.json` | ✅ Supabase Token |
| **Railway MCP** | Application hosting and deployment | `configs/individual/railway-mcp.json` | ❌ Uses CLI auth |

### Extended Services
| Server | Purpose | Config File | Requires Token |
|--------|---------|-------------|----------------|
| **MCPify Ninja Trader** | Trading platform integration | `configs/individual/mcpify-ninja-trader.json` | ❌ Public endpoint |
| **MCPify Google Places** | Location and search services | `configs/individual/mcpify-google-places.json` | ❌ Public endpoint |

## 🔑 API Keys & Tokens

### Secure Storage Locations
- **Template:** `keys/.env.example` - Safe template for new setups
- **Production:** `keys/.env.production` - Contains actual extracted tokens
- **Development:** `keys/.env` - Your working environment (created by setup)

### Required Tokens
| Token | Purpose | Get From | Scope Required |
|-------|---------|----------|----------------|
| `GITHUB_TOKEN` | GitHub API access | https://github.com/settings/tokens | `repo` |
| `VERCEL_TOKEN` | Vercel deployments | https://vercel.com/account/tokens | Full Account |
| `SUPABASE_TOKEN` | Database access | https://supabase.com/dashboard/account/tokens | Read/Write |
| `RAILWAY_TOKEN` | Railway deployments (optional) | https://railway.app/account/tokens | Full Access |

### Extracted Token Values
> **⚠️ SECURITY WARNING:** These are actual production tokens!

- **GitHub:** `[REDACTED - Use environment variable GITHUB_TOKEN]`
- **Vercel:** `MyaHokrgQhkajr06zJLvDmPn`
- **Supabase:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3Mjc4MDc0MDAsCiAgImV4cCI6IDE4ODU1NzM4MDAKfQ.OycUXKTNplHa5qAUj6-RByHhAQ6Fqh4tLI2quSKo6y4`

## 📦 Configuration Templates

### Complete Configurations
| Template | Description | Use Case |
|----------|-------------|----------|
| `configs/templates/complete-mcp-template.json` | All MCP servers | Full development environment |
| `configs/templates/minimal-mcp-template.json` | Core servers only | Basic setup |
| `configs/complete/production-ready.json` | Production configuration | Ready-to-deploy setup |

### Individual Server Configs
| Config | Server | Can Use Standalone |
|--------|--------|-------------------|
| `configs/individual/github-mcp.json` | GitHub MCP | ✅ Yes |
| `configs/individual/vercel-mcp.json` | Vercel MCP | ✅ Yes |
| `configs/individual/supabase-mcp.json` | Supabase MCP | ✅ Yes |
| `configs/individual/railway-mcp.json` | Railway MCP | ✅ Yes |
| `configs/individual/mcpify-ninja-trader.json` | Ninja Trader | ✅ Yes |
| `configs/individual/mcpify-google-places.json` | Google Places | ✅ Yes |

## 🛠️ Setup Scripts

### Main Scripts
| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/setup.sh` | Complete MCP setup | `./setup.sh` |
| `scripts/install-servers.sh` | Install MCP packages | `./install-servers.sh` |
| `scripts/validate-config.sh` | Validate configuration | `./validate-config.sh` |
| `scripts/migrate-from-old.sh` | Migrate from old setup | `./migrate-from-old.sh` |

### Legacy Files (Migrated)
| File | Status | New Location |
|------|--------|--------------|
| `mcp_config_complete.json` | ✅ Migrated | `configs/complete/production-ready.json` |
| `setup_mcp_config.sh` | ✅ Replaced | `scripts/setup.sh` |
| `MCP_TOKENS_STATUS.md` | ✅ Archived | `keys/.env.production` |

## 📚 Documentation

### User Guides
| Document | Purpose | Audience |
|----------|---------|----------|
| `README.md` | Overview and quick start | All users |
| `docs/quick-start.md` | 5-minute setup guide | New users |
| `docs/setup-guide.md` | Detailed setup instructions | Advanced users |
| `docs/troubleshooting.md` | Common issues and solutions | Support |

### Technical Reference
| Document | Purpose | Audience |
|----------|---------|----------|
| `MCP_INDEX.md` | This file - complete inventory | Developers |
| `keys/.env.example` | Environment template | Setup |
| `configs/README.md` | Configuration reference | Customization |

## 🚀 Quick Usage Guide

### For New Users
```bash
# 1. Quick setup
cd mcp/scripts
./setup.sh

# 2. Restart Windsurf
# 3. Test: "Deploy to Vercel"
```

### For Migration from Old Setup
```bash
# Migrate existing setup
cd mcp/scripts
./migrate-from-old.sh
```

### For Custom Configuration
```bash
# Use individual configs
cp configs/individual/github-mcp.json my-config.json
cp configs/individual/vercel-mcp.json temp.json
# Merge configurations as needed
```

## 🔒 Security Features

### Token Protection
- ✅ **Separated Keys** - All tokens in dedicated `keys/` directory
- ✅ **Environment Variables** - No hardcoded tokens in configs
- ✅ **Gitignore Protection** - Keys directory excluded from version control
- ✅ **Template System** - Safe sharing without exposing secrets

### Access Control
- ✅ **Minimal Permissions** - Tokens have only required scopes
- ✅ **Backup System** - Automatic backups before changes
- ✅ **Validation** - Scripts validate token format and access

## 📊 Usage Statistics

### Configuration Complexity
- **Total MCP Servers:** 6
- **Servers Requiring Tokens:** 3
- **Individual Config Files:** 6
- **Template Configurations:** 3
- **Setup Scripts:** 4
- **Documentation Files:** 8

### Token Requirements
- **Required for Basic Setup:** 3 tokens (GitHub, Vercel, Supabase)
- **Optional Tokens:** 1 (Railway - uses CLI auth by default)
- **Public Endpoints:** 2 (MCPify services)

## 🎯 Recommended Setups

### Beginner Setup
```bash
# Use minimal template with core servers
cd mcp/scripts
./setup.sh
# Choose option 2 (Minimal)
```

### Full Development Environment
```bash
# Use complete template with all servers
cd mcp/scripts  
./setup.sh
# Choose option 1 (Complete)
```

### Production Environment
```bash
# Use production-ready configuration
cp configs/complete/production-ready.json /Users/stagnator/.codeium/windsurf/mcp_config.json
# Edit tokens manually for security
```

---

**📝 Last Updated:** $(date)  
**🔧 Maintained By:** MCP Configuration System  
**📍 Location:** `/mcp/` directory in orca-ven-backend repository
