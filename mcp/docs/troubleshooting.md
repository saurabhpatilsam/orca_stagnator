# 🆘 MCP Troubleshooting Guide

Common issues and solutions for MCP server setup and usage.

## 🔍 Diagnostic Commands

### Check Configuration
```bash
cd mcp/scripts
./validate-config.sh
```

### Check Windsurf Config Location
```bash
ls -la /Users/stagnator/.codeium/windsurf/mcp_config.json
```

### Check Environment Variables
```bash
cd mcp/keys
cat .env
```

## ❌ Common Issues

### 1. MCP Servers Not Showing Up

**Symptoms:**
- MCP commands don't work in Windsurf
- No MCP tools available in chat

**Solutions:**

1. **Check config file location:**
   ```bash
   ls -la /Users/stagnator/.codeium/windsurf/mcp_config.json
   ```

2. **Validate JSON syntax:**
   ```bash
   cd mcp/scripts
   ./validate-config.sh
   ```

3. **Restart Windsurf completely:**
   - Quit: Cmd+Q
   - Wait 5 seconds
   - Reopen Windsurf
   - Start new chat session

4. **Check Windsurf logs:**
   - Look for MCP-related errors in Windsurf console

### 2. Authentication Errors

**Symptoms:**
- "Unauthorized" or "Invalid token" errors
- MCP servers fail to connect

**Solutions:**

1. **Verify tokens are correct:**
   ```bash
   cd mcp/keys
   nano .env
   ```
   - Check for extra spaces or newlines
   - Ensure tokens haven't expired

2. **Test token validity:**
   
   **GitHub Token:**
   ```bash
   curl -H "Authorization: Bearer YOUR_GITHUB_TOKEN" https://api.github.com/user
   ```
   
   **Vercel Token:**
   ```bash
   curl -H "Authorization: Bearer YOUR_VERCEL_TOKEN" https://api.vercel.com/v2/user
   ```

3. **Regenerate tokens:**
   - GitHub: https://github.com/settings/tokens
   - Vercel: https://vercel.com/account/tokens
   - Supabase: https://supabase.com/dashboard/account/tokens

4. **Check token permissions:**
   - GitHub: Needs `repo` scope
   - Vercel: Needs Full Account access
   - Supabase: Needs read/write access

### 3. Environment Variables Not Loading

**Symptoms:**
- Configuration shows `${GITHUB_TOKEN}` instead of actual token
- "Token placeholder not resolved" errors

**Solutions:**

1. **Check .env file exists:**
   ```bash
   ls -la mcp/keys/.env
   ```

2. **Verify .env format:**
   ```bash
   cd mcp/keys
   cat .env
   ```
   Should look like:
   ```
   GITHUB_TOKEN=ghp_your_actual_token_here
   VERCEL_TOKEN=your_vercel_token_here
   ```

3. **Rerun setup script:**
   ```bash
   cd mcp/scripts
   ./setup.sh
   ```

### 4. Package Installation Issues

**Symptoms:**
- "Command not found" errors for MCP servers
- NPX fails to find packages

**Solutions:**

1. **Check Node.js and npm:**
   ```bash
   node --version
   npm --version
   ```

2. **Reinstall packages:**
   ```bash
   cd mcp/scripts
   ./install-servers.sh
   ```

3. **Clear npm cache:**
   ```bash
   npm cache clean --force
   ```

4. **Install packages manually:**
   ```bash
   npm install -g @supabase/mcp-server-supabase@latest
   npm install -g @railway/mcp-server
   npm install -g @composio/mcp@latest
   ```

### 5. JSON Syntax Errors

**Symptoms:**
- "Invalid JSON" errors
- Configuration not loading

**Solutions:**

1. **Validate JSON:**
   ```bash
   jq empty /Users/stagnator/.codeium/windsurf/mcp_config.json
   ```

2. **Check for common issues:**
   - Trailing commas
   - Missing quotes
   - Unescaped characters

3. **Regenerate configuration:**
   ```bash
   cd mcp/scripts
   ./setup.sh
   ```

### 6. Supabase MCP Server Issues

**Symptoms:**
- Supabase queries fail
- "Access token invalid" errors

**Solutions:**

1. **Check Supabase token format:**
   - Should start with `sbp_`
   - Get from: https://supabase.com/dashboard/account/tokens

2. **Verify project access:**
   - Token should have access to your Supabase project
   - Check project permissions

3. **Test Supabase connection:**
   ```bash
   npx @supabase/mcp-server-supabase@latest --access-token YOUR_TOKEN
   ```

### 7. Railway MCP Server Issues

**Symptoms:**
- Railway commands fail
- "Not authenticated" errors

**Solutions:**

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Verify Railway authentication:**
   ```bash
   railway whoami
   ```

## 🔧 Advanced Troubleshooting

### Reset Everything

If nothing works, start fresh:

```bash
# 1. Remove existing config
rm -f /Users/stagnator/.codeium/windsurf/mcp_config.json

# 2. Remove environment file
rm -f mcp/keys/.env

# 3. Reinstall packages
cd mcp/scripts
./install-servers.sh

# 4. Reconfigure
cp ../keys/.env.example ../keys/.env
nano ../keys/.env  # Add your tokens

# 5. Run setup
./setup.sh

# 6. Restart Windsurf
```

### Check Windsurf Logs

1. Open Windsurf
2. Go to View → Toggle Developer Tools
3. Check Console tab for MCP-related errors
4. Look for connection or authentication issues

### Manual Configuration

If scripts fail, configure manually:

1. **Create config file:**
   ```bash
   mkdir -p /Users/stagnator/.codeium/windsurf
   nano /Users/stagnator/.codeium/windsurf/mcp_config.json
   ```

2. **Use minimal config:**
   ```json
   {
     "mcpServers": {
       "github": {
         "serverUrl": "https://api.githubcopilot.com/mcp/",
         "headers": {
           "Authorization": "Bearer YOUR_GITHUB_TOKEN_HERE"
         }
       }
     }
   }
   ```

3. **Replace tokens manually**
4. **Restart Windsurf**

## 📞 Getting Help

### Check Documentation
- `mcp/docs/setup-guide.md` - Detailed setup
- `mcp/docs/quick-start.md` - Quick setup
- `mcp/README.md` - Overview

### Validate Setup
```bash
cd mcp/scripts
./validate-config.sh
```

### Test Individual Components
```bash
# Test environment loading
cd mcp/keys
source .env
echo $GITHUB_TOKEN

# Test JSON syntax
jq empty /Users/stagnator/.codeium/windsurf/mcp_config.json

# Test package installation
npx @supabase/mcp-server-supabase@latest --help
```

## 🎯 Prevention Tips

1. **Always backup configs** before changes
2. **Use the validation script** after setup
3. **Keep tokens secure** and rotate regularly
4. **Test after Windsurf updates**
5. **Use version control** for your configurations (without tokens)
