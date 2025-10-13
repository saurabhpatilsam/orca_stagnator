# 🔧 MCP Servers Setup Guide

## 📋 Overview

This guide will help you add GitHub, Vercel, Railway, and Supabase MCP servers to Windsurf.

---

## 🎯 Step 1: Get Your API Tokens

### **1. GitHub Token**

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `Windsurf MCP`
4. Scopes: Select all `repo` permissions
5. Click "Generate token"
6. **Copy the token** (starts with `ghp_` or `github_pat_`)

### **2. Vercel Token**

1. Go to: https://vercel.com/account/tokens
2. Click "Create Token"
3. Name: `Windsurf MCP`
4. Scope: Full Account
5. Click "Create"
6. **Copy the token**

### **3. Supabase Access Token**

1. Go to: https://supabase.com/dashboard/account/tokens
2. Click "Generate new token"
3. Name: `Windsurf MCP`
4. Click "Generate token"
5. **Copy the token** (starts with `sbp_`)

### **4. Railway Token** (Optional)

Railway doesn't have an official MCP server yet, but you can use their API:

1. Go to: https://railway.app/account/tokens
2. Click "Create token"
3. Name: `Windsurf MCP`
4. **Copy the token**

---

## 🎯 Step 2: Update MCP Configuration

### **Location:**
```
/Users/stagnator/.codeium/windsurf/mcp_config.json
```

### **Configuration:**

Replace the contents with this (update the tokens):

```json
{
  "mcpServers": {
    "github": {
      "serverUrl": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_GITHUB_TOKEN_HERE"
      }
    },
    "vercel": {
      "serverUrl": "https://mcp.vercel.com",
      "headers": {
        "Authorization": "Bearer YOUR_VERCEL_TOKEN_HERE"
      }
    },
    "supabase-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--access-token",
        "YOUR_SUPABASE_TOKEN_HERE"
      ],
      "env": {}
    },
    "mcpify-ninja-trader-python-bridge-mcp": {
      "command": "npx",
      "args": [
        "@composio/mcp@latest",
        "start",
        "--url",
        "https://agent.mcpify.ai/sse?server=b5ff8dce-f740-45db-91a7-14d0fff22898"
      ]
    },
    "mcpify-google-places-serp-tools": {
      "command": "npx",
      "args": [
        "@composio/mcp@latest",
        "start",
        "--url",
        "https://agent.mcpify.ai/sse?server=a2cca30d-4210-44ef-8da9-dcf164ccc4ed"
      ]
    }
  }
}
```

---

## 🎯 Step 3: Apply Configuration

### **Option 1: Manual Copy**

1. Open the file:
   ```bash
   open /Users/stagnator/.codeium/windsurf/mcp_config.json
   ```

2. Replace contents with the configuration above

3. **Replace these placeholders:**
   - `YOUR_GITHUB_TOKEN_HERE` → Your GitHub token
   - `YOUR_VERCEL_TOKEN_HERE` → Your Vercel token
   - `YOUR_SUPABASE_TOKEN_HERE` → Your Supabase token

4. Save the file

### **Option 2: Using Command Line**

I've created a template at: `mcp_config_complete.json`

1. Edit the template with your tokens:
   ```bash
   nano mcp_config_complete.json
   ```

2. Copy to Windsurf config:
   ```bash
   cp mcp_config_complete.json /Users/stagnator/.codeium/windsurf/mcp_config.json
   ```

---

## 🎯 Step 4: Restart Windsurf

1. **Quit Windsurf completely** (Cmd+Q)
2. **Reopen Windsurf**
3. **Start a new chat session**

---

## ✅ Step 5: Verify MCP Servers

After restarting, I'll have access to these tools:

### **GitHub MCP:**
- Create repositories
- Push code
- Create pull requests
- Manage issues
- View commits

### **Vercel MCP:**
- Deploy projects
- Manage deployments
- Configure domains
- View logs
- Manage environment variables

### **Supabase MCP:**
- Query database
- Manage tables
- Run SQL
- View data

---

## 🔒 Security Notes

### **Keep Your Tokens Safe:**

1. ✅ Never commit `mcp_config.json` to git
2. ✅ Tokens are stored locally only
3. ✅ Rotate tokens periodically
4. ✅ Use minimal required permissions

### **Token Permissions:**

- **GitHub:** Only `repo` scope needed
- **Vercel:** Full account access for deployments
- **Supabase:** Read/write access for database operations

---

## 🆘 Troubleshooting

### **MCP servers not showing up:**

1. Check file location: `/Users/stagnator/.codeium/windsurf/mcp_config.json`
2. Verify JSON syntax (no trailing commas, proper quotes)
3. Restart Windsurf completely (Cmd+Q)
4. Check Windsurf logs for errors

### **Authentication errors:**

1. Verify tokens are correct (no extra spaces)
2. Check token hasn't expired
3. Verify token has required permissions
4. Regenerate token if needed

### **Vercel deployment fails:**

1. Verify Vercel token has deployment permissions
2. Check project exists in Vercel dashboard
3. Verify GitHub repository is connected

---

## 📚 What You Can Do After Setup

### **With GitHub MCP:**
```
"Push my code to GitHub"
"Create a pull request"
"List my repositories"
```

### **With Vercel MCP:**
```
"Deploy the frontend to Vercel"
"Show my Vercel deployments"
"Configure domain for my project"
```

### **With Supabase MCP:**
```
"Query the ticks_es table"
"Show me the database schema"
"Run this SQL query"
```

---

## 🎉 Quick Setup Summary

```bash
# 1. Get tokens from:
# - GitHub: https://github.com/settings/tokens
# - Vercel: https://vercel.com/account/tokens
# - Supabase: https://supabase.com/dashboard/account/tokens

# 2. Edit config file
nano /Users/stagnator/.codeium/windsurf/mcp_config.json

# 3. Paste configuration and add your tokens

# 4. Restart Windsurf (Cmd+Q, then reopen)

# 5. Start new chat and test:
# "Deploy my frontend to Vercel"
```

---

## 📞 Need Help?

After setting this up and restarting Windsurf, I'll be able to:
- ✅ Deploy your frontend to Vercel automatically
- ✅ Push code to GitHub
- ✅ Query Supabase database
- ✅ Manage deployments

**Just restart Windsurf after adding the config, and I'll have all these powers!** 🚀
