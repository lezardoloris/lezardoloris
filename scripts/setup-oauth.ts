import { open } from 'open';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';
import * as http from 'http';

/**
 * GOOGLE ADS OAUTH SETUP
 * Users simply run: npm run setup:auth
 * Everything is automated - no more hassle with Google Cloud Console!
 */

interface OAuthConfig {
  CLIENT_ID: string;
  CLIENT_SECRET: string;
  DEVELOPER_TOKEN: string;
  REDIRECT_URI: string;
  OAUTH_URL: string;
  TOKEN_URL: string;
}

const OAUTH_CONFIG: OAuthConfig = {
  CLIENT_ID: '',
  CLIENT_SECRET: '',
  DEVELOPER_TOKEN: '',
  REDIRECT_URI: 'http://localhost:3001/callback',
  OAUTH_URL: 'https://accounts.google.com/o/oauth2/v2/auth',
  TOKEN_URL: 'https://oauth2.googleapis.com/token',
};

const SCOPES = [
  'https://www.googleapis.com/auth/adwords',
];

async function getAuthorizationCode(): Promise<string> {
  return new Promise((resolve, reject) => {
    // Create a local server to receive the callback
    const server = http.createServer((req, res) => {
      const url = new URL(req.url || '', `http://localhost:3001`);
      const code = url.searchParams.get('code');
      const error = url.searchParams.get('error');

      if (error) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(`
          <html>
            <body style="font-family: Arial; padding: 50px; text-align: center;">
              <h1>❌ OAuth Error</h1>
              <p>Error: ${error}</p>
              <p>Close this window and try again.</p>
            </body>
          </html>
        `);
        reject(new Error(`OAuth error: ${error}`));
      } else if (code) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(`
          <html>
            <body style="font-family: Arial; padding: 50px; text-align: center;">
              <h1>✅ Authentication Successful!</h1>
              <p>You can now close this window and return to the terminal.</p>
            </body>
          </html>
        `);
        server.close();
        resolve(code);
      }
    });

    server.listen(3001, () => {
      // Construct the authentication URL
      const authUrl = new URL(OAUTH_CONFIG.OAUTH_URL);
      authUrl.searchParams.append('client_id', OAUTH_CONFIG.CLIENT_ID);
      authUrl.searchParams.append('redirect_uri', OAUTH_CONFIG.REDIRECT_URI);
      authUrl.searchParams.append('response_type', 'code');
      authUrl.searchParams.append('scope', SCOPES.join(' '));
      authUrl.searchParams.append('access_type', 'offline');
      authUrl.searchParams.append('prompt', 'consent');

      console.log('\n🔓 Opening Google OAuth...\n');
      console.log('A browser window will open.');
      console.log('Sign in with your Google Ads account.');
      console.log('After approving, you\'ll be redirected back automatically.\n');

      // Open the browser
      open(authUrl.toString()).catch(() => {
        console.log('Could not open browser automatically. Open this URL manually:');
        console.log(authUrl.toString());
      });
    });
  });
}

async function exchangeCodeForTokens(code: string): Promise<{ refresh_token: string; access_token: string }> {
  const params = new URLSearchParams({
    code,
    client_id: OAUTH_CONFIG.CLIENT_ID,
    client_secret: OAUTH_CONFIG.CLIENT_SECRET,
    redirect_uri: OAUTH_CONFIG.REDIRECT_URI,
    grant_type: 'authorization_code',
  });

  const response = await fetch(OAUTH_CONFIG.TOKEN_URL, {
    method: 'POST',
    body: params,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  if (!response.ok) {
    const errorData = await response.text();
    throw new Error(`Token exchange failed: ${response.statusText}\n${errorData}`);
  }

  const data = (await response.json()) as any;

  if (!data.refresh_token) {
    throw new Error('No refresh token received. Make sure you approved the request.');
  }

  return {
    refresh_token: data.refresh_token,
    access_token: data.access_token,
  };
}

async function getUserCustomerId(accessToken: string): Promise<string> {
  const response = await fetch('https://googleads.googleapis.com/v17/customers:listAccessibleCustomers', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'developer-token': OAUTH_CONFIG.DEVELOPER_TOKEN,
    },
  });

  if (!response.ok) {
    const errorData = await response.text();
    throw new Error(`Failed to fetch customer ID: ${response.statusText}\n${errorData}`);
  }

  const data = (await response.json()) as any;

  if (!data.resourceNames || data.resourceNames.length === 0) {
    throw new Error('No Google Ads accounts found. Check the account you used to authenticate.');
  }

  // Extract customer ID from format "customers/1234567890"
  const customerId = data.resourceNames[0].split('/')[1];

  console.log('\n📋 Available Google Ads Accounts:');
  data.resourceNames.forEach((resource: string, index: number) => {
    const id = resource.split('/')[1];
    console.log(`  ${index + 1}. Customer ID: ${id}`);
  });

  return customerId;
}

function askQuestion(question: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function main() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║       🎯 GOOGLE ADS SETUP - AUTOMATED VERSION             ║');
  console.log('║                                                            ║');
  console.log('║  This will ask for 3 pieces of info from Google Cloud,    ║');
  console.log('║  then everything else happens automatically.               ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  // Step 1: Get minimal info from Google Cloud
  console.log('📋 STEP 1: Google Cloud Console Info\n');
  console.log('You need 3 things (takes 5 minutes):');
  console.log('  1. CLIENT_ID');
  console.log('  2. CLIENT_SECRET');
  console.log('  3. DEVELOPER_TOKEN\n');
  console.log('Quick guide:');
  console.log('  - Go to: https://console.cloud.google.com');
  console.log('  - Create a new project (or use existing)');
  console.log('  - Enable Google Ads API');
  console.log('  - Create OAuth 2.0 credentials (Desktop app type)');
  console.log('  - Add redirect URI: http://localhost:3001/callback');
  console.log('  - Copy CLIENT_ID and CLIENT_SECRET\n');
  console.log('  - For DEVELOPER_TOKEN:');
  console.log('    • Go to Google Ads → Tools & Settings → API Center');
  console.log('    • Apply for developer token (may take 24 hours)\n');

  const clientId = await askQuestion('📌 Paste your CLIENT_ID: ');
  const clientSecret = await askQuestion('📌 Paste your CLIENT_SECRET: ');
  const developerToken = await askQuestion('📌 Paste your DEVELOPER_TOKEN: ');

  if (!clientId || !clientSecret || !developerToken) {
    console.error('\n❌ Error: All three values are required.');
    process.exit(1);
  }

  OAUTH_CONFIG.CLIENT_ID = clientId;
  OAUTH_CONFIG.CLIENT_SECRET = clientSecret;
  OAUTH_CONFIG.DEVELOPER_TOKEN = developerToken;

  // Step 2: Automatic OAuth flow
  console.log('\n✨ STEP 2: Automatic Authentication\n');

  try {
    const code = await getAuthorizationCode();
    console.log('✅ Authorization code received!\n');

    console.log('🔄 Exchanging code for tokens...\n');
    const { refresh_token, access_token } = await exchangeCodeForTokens(code);

    console.log('🔍 Fetching your Customer ID...\n');
    const customerId = await getUserCustomerId(access_token);

    // Step 3: Automatic save to .env
    console.log('\n💾 Saving configuration...\n');

    const envContent = `# 🎯 Google Ads Configuration (Auto-generated by setup:auth)
# Generated on: ${new Date().toISOString()}

GOOGLE_ADS_DEVELOPER_TOKEN=${developerToken}
GOOGLE_ADS_CLIENT_ID=${clientId}
GOOGLE_ADS_CLIENT_SECRET=${clientSecret}
GOOGLE_ADS_REFRESH_TOKEN=${refresh_token}
GOOGLE_ADS_CUSTOMER_ID=${customerId}

# Optional: If using MCC account, uncomment and set your login customer ID
# GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890
`;

    fs.writeFileSync(path.join(process.cwd(), '.env'), envContent);

    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║                  ✅ SETUP COMPLETE!                        ║');
    console.log('╠════════════════════════════════════════════════════════════╣');
    console.log('║                                                            ║');
    console.log('║  Your .env file has been created with all credentials.    ║');
    console.log('║  You can now run:                                         ║');
    console.log('║                                                            ║');
    console.log('║      npm run build                                         ║');
    console.log('║      npm start                                             ║');
    console.log('║                                                            ║');
    console.log('║  Or for development:                                       ║');
    console.log('║                                                            ║');
    console.log('║      npm run dev                                           ║');
    console.log('║                                                            ║');
    console.log('║  Your MCP server is ready! 🚀                              ║');
    console.log('║                                                            ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log('Saved credentials:');
    console.log(`  • Customer ID: ${customerId}`);
    console.log(`  • Developer Token: ${developerToken.slice(0, 10)}...`);
    console.log(`  • Client ID: ${clientId.slice(0, 20)}...`);
    console.log('\n🔐 IMPORTANT: Never share your .env file!\n');
    console.log('Next steps:');
    console.log('  1. Run "npm run build" to compile the TypeScript');
    console.log('  2. Configure Claude Desktop with this MCP server');
    console.log('  3. Start asking Claude about your Google Ads data!\n');
  } catch (error) {
    console.error('\n❌ Error:', error instanceof Error ? error.message : error);
    console.error('\nTroubleshooting:');
    console.error('  • Make sure redirect URI http://localhost:3001/callback is added in Google Cloud Console');
    console.error('  • Verify your CLIENT_ID and CLIENT_SECRET are correct');
    console.error('  • Check that Google Ads API is enabled in your project');
    console.error('  • Ensure port 3001 is not already in use\n');
    process.exit(1);
  }
}

main();
