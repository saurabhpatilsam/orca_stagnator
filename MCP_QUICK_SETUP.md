# ⚡ MCP Quick Setup - 5 Minutes

## 🎯 Get Your Tokens

1. **GitHub:** https://github.com/settings/tokens → Generate (select `repo` scope)
2. **Vercel:** https://vercel.com/account/tokens → Create
3. **Supabase:** https://supabase.com/dashboard/account/tokens → Generate

---

## 📝 Edit Config File

```bash
nano /Users/stagnator/.codeium/windsurf/mcp_config.json
```

**Paste this (replace YOUR_TOKEN with actual tokens):**

```json
{
  "mcpServers": {
    "github": {
      "serverUrl": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_GITHUB_TOKEN"
      }
    },
    "vercel": {
      "serverUrl": "https://mcp.vercel.com",
      "headers": {
        "Authorization": "Bearer YOUR_VERCEL_TOKEN"
      }
    },
    "supabase-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--access-token",
        "YOUR_SUPABASE_TOKEN"
      ],
      "env": {}
    }
  }
}
```

---

## 🔄 Restart Windsurf

1. **Quit:** Cmd+Q
2. **Reopen:** Windsurf
3. **New Chat:** Start fresh session

---

## ✅ Test It

After restart, ask me:
- "Deploy my frontend to Vercel"
- "Push code to GitHub"
- "Query Supabase database"

**I'll have full access to all MCP tools!** 🚀

---

## 📚 Full Guide

See `MCP_SETUP_GUIDE.md` for detailed instructions.
