# ⚡ MCP Quick Start Guide

Get your MCP servers running in 5 minutes!

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
cd mcp/scripts
./install-servers.sh
```

### 2. Configure Environment
```bash
# Copy environment template
cp mcp/keys/.env.example mcp/keys/.env

# Edit with your tokens
nano mcp/keys/.env
```

### 3. Get API Tokens

**GitHub Token:**
- Go to: https://github.com/settings/tokens
- Generate new token (classic)
- Select `repo` scope
- Copy token to `.env` file

**Vercel Token:**
- Go to: https://vercel.com/account/tokens
- Create new token
- Full Account scope
- Copy token to `.env` file

**Supabase Token:**
- Go to: https://supabase.com/dashboard/account/tokens
- Generate new token
- Copy token to `.env` file

### 4. Run Setup
```bash
cd mcp/scripts
./setup.sh
```

### 5. Restart Windsurf
1. Quit Windsurf (Cmd+Q)
2. Reopen Windsurf
3. Start new chat session

## ✅ Test Your Setup

Try these commands after restart:
- "Deploy my frontend to Vercel"
- "Push code to GitHub"
- "Query Supabase database"
- "Show my Railway projects"

## 🔧 Troubleshooting

**Config not working?**
```bash
cd mcp/scripts
./validate-config.sh
```

**Need help?** See `setup-guide.md` for detailed instructions.
