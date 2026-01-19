# Google Ads MCP Server - Installation Guide

## ⚡ Quick Setup (Recommended)

The easiest way to set up the Google Ads MCP server is using our automated setup script. **Total time: ~5 minutes.**

### Prerequisites

1. **Node.js 18+** installed ([Download here](https://nodejs.org/))
2. **Google Ads Account** with API access
3. **Google Cloud Project** (free to create)

### Step 1: Clone and Install

```bash
git clone https://github.com/yourusername/google-ads-mcp-server.git
cd google-ads-mcp-server
npm install
```

### Step 2: Get Google Cloud Credentials (One-Time, ~3 minutes)

You need 3 pieces of information from Google Cloud Console:

#### A. Enable Google Ads API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Search for "Google Ads API" and **Enable** it

#### B. Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Select **Desktop application** as the application type
4. Name it (e.g., "Google Ads MCP Server")
5. Click **Create**
6. **Important**: Click on your newly created credential
7. Add authorized redirect URI: `http://localhost:3001/callback`
8. Copy your **Client ID** and **Client Secret**

#### C. Get Developer Token

1. Sign in to your [Google Ads account](https://ads.google.com/)
2. Navigate to **Tools & Settings** (wrench icon) → **Setup** → **API Center**
3. Click **Apply for API access** (if not already done)
4. Copy your **Developer Token**

> **Note**: Developer token approval can take 24 hours, but you can use it in test mode immediately with test accounts.

### Step 3: Run Automated Setup

```bash
npm run setup:auth
```

The script will:
1. Ask for your **Client ID**, **Client Secret**, and **Developer Token**
2. Open your browser for Google authentication
3. Automatically retrieve your **Customer ID**
4. Create your `.env` file with all credentials

**That's it!** Your `.env` file is now configured.

### Step 4: Build and Start

```bash
npm run build
npm start
```

Or for development:

```bash
npm run dev
```

### Step 5: Configure Claude Desktop

Add this to your Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "node",
      "args": ["/absolute/path/to/google-ads-mcp-server/dist/index.js"],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "your_developer_token",
        "GOOGLE_ADS_CLIENT_ID": "your_client_id",
        "GOOGLE_ADS_CLIENT_SECRET": "your_client_secret",
        "GOOGLE_ADS_REFRESH_TOKEN": "your_refresh_token",
        "GOOGLE_ADS_CUSTOMER_ID": "1234567890"
      }
    }
  }
}
```

> **Tip**: You can copy these values directly from the `.env` file created by the setup script.

### Step 6: Restart Claude Desktop

Restart Claude Desktop completely. You should now see the Google Ads MCP server in your connectors panel!

---

## 🔧 Manual Setup (Advanced)

If you prefer to set everything up manually or the automated script doesn't work for you:

### 1. Create `.env` File Manually

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 2. Get Refresh Token Manually

Install the Google Ads API CLI tool:

```bash
npx google-ads-api --generate-refresh-token
```

Follow the prompts to generate your refresh token.

### 3. Fill in `.env`

```env
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
GOOGLE_ADS_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your_client_secret_here
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token_here
GOOGLE_ADS_CUSTOMER_ID=1234567890

# Optional: For MCC accounts
# GOOGLE_ADS_LOGIN_CUSTOMER_ID=9876543210
```

**Note**: Customer ID should be without hyphens (e.g., `1234567890` not `123-456-7890`)

---

## ✅ Verify Installation

Test your setup by running:

```bash
npm run dev
```

If everything is configured correctly, you should see:

```
Google Ads MCP Server running on stdio
```

---

## 🚀 Usage

Once installed and configured, you can ask Claude questions like:

```
Show me all my campaigns from the last 30 days
```

```
Find campaigns wasting budget with ROAS below 2x
```

```
Generate a comprehensive Google Ads audit for my account
```

See [EXAMPLES.md](./EXAMPLES.md) for 50+ example prompts.

---

## 🐛 Troubleshooting

### "Customer ID is required" Error

Make sure your `GOOGLE_ADS_CUSTOMER_ID` is set without hyphens (e.g., `1234567890`)

### "Invalid refresh token" Error

Your refresh token may have expired. Re-run the setup:

```bash
npm run setup:auth
```

### "Developer token not approved" Error

Your developer token needs approval from Google (takes ~24 hours). You can still use it in test mode with test accounts.

### "Port 3001 already in use" Error

Another application is using port 3001. Either:
- Stop the other application
- Or edit `scripts/setup-oauth.ts` and change `3001` to another port (e.g., `3002`)

### MCP Server Not Appearing in Claude

1. Check that the path in `claude_desktop_config.json` is **absolute** (not relative)
2. Ensure the server builds without errors: `npm run build`
3. Restart Claude Desktop **completely** (quit and reopen)
4. Check Claude's logs for error messages

### "Redirect URI mismatch" Error

Make sure you added `http://localhost:3001/callback` to the authorized redirect URIs in Google Cloud Console:

1. Go to Google Cloud Console → APIs & Services → Credentials
2. Click on your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", add: `http://localhost:3001/callback`
4. Save and try again

---

## 🔐 Security Best Practices

- **Never commit** your `.env` file to version control (already in `.gitignore`)
- **Don't share** your refresh token - it provides ongoing API access
- **Use environment variables** for production deployments
- **Rotate credentials** periodically for enhanced security
- **Use MCC accounts** with read-only access when possible

---

## 📊 API Limits

Google Ads API has daily operation limits:

| Access Level | Operations/Day |
|--------------|----------------|
| Standard     | 15,000         |
| Basic (Test) | 15,000         |

Monitor your usage in the Google Ads API Center dashboard.

---

## 🆘 Need Help?

1. Check the [README.md](./README.md) for general information
2. See [EXAMPLES.md](./EXAMPLES.md) for usage examples
3. Review [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
4. Open an issue on GitHub

---

## 📺 Video Tutorial

[Coming soon] - Step-by-step video walkthrough of the entire setup process.

---

**That's it! You're ready to analyze Google Ads with Claude AI. 🎉**
