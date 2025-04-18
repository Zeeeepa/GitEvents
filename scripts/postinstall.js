#!/usr/bin/env node

/**
 * GitEvents - Dependency Conflict Resolution Script
 * 
 * This script runs after npm install to fix common dependency issues:
 * 1. Resolves vulnerabilities in nth-check and postcss
 * 2. Handles platform-specific dependencies
 * 3. Ensures proper setup for both development and production
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');

const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

console.log(`${colors.cyan}\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557${colors.reset}`);
console.log(`${colors.cyan}\u2551  GitEvents - Post-Installation Setup        \u2551${colors.reset}`);
console.log(`${colors.cyan}\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d${colors.reset}`);

function safeExec(command, errorMessage) {
  try {
    console.log(`${colors.blue}> ${command}${colors.reset}`);
    return execSync(command, { stdio: 'inherit' });
  } catch (error) {
    console.error(`${colors.red}ERROR: ${errorMessage}${colors.reset}`);
    console.error(`${colors.yellow}Command failed: ${command}${colors.reset}`);
    console.error(`${colors.yellow}You may need to run this command manually.${colors.reset}`);
    return null;
  }
}

function hasVulnerabilities(packageName) {
  try {
    const output = execSync(`npm audit --json`, { encoding: 'utf8' });
    const auditData = JSON.parse(output);
    
    if (auditData.vulnerabilities && auditData.vulnerabilities[packageName]) {
      return true;
    }
    
    return false;
  } catch (error) {
    console.error(`${colors.yellow}Warning: Could not check vulnerabilities for ${packageName}${colors.reset}`);
    return false;
  }
}

console.log(`\n${colors.green}Checking for and fixing known vulnerabilities...${colors.reset}`);

if (hasVulnerabilities('nth-check')) {
  console.log(`${colors.yellow}Detected vulnerability in nth-check. Attempting to fix...${colors.reset}`);
  safeExec('npm install nth-check@2.1.1 --save-dev', 'Failed to update nth-check');
}

if (hasVulnerabilities('postcss')) {
  console.log(`${colors.yellow}Detected vulnerability in postcss. Attempting to fix...${colors.reset}`);
  safeExec('npm install postcss@8.4.31 --save-dev', 'Failed to update postcss');
}

const isWindows = os.platform() === 'win32';
if (isWindows) {
  console.log(`\n${colors.green}Setting up Windows-specific configurations...${colors.reset}`);
  
  const envPath = path.join(process.cwd(), '.env');
  if (!fs.existsSync(envPath)) {
    console.log(`${colors.blue}Creating default .env file...${colors.reset}`);
    const defaultEnv = 
`# GitEvents Environment Configuration
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
GITHUB_API_TOKEN=your_github_token_here
GITHUB_EVENTS_DB=github_events.db
API_PORT=8001
`;
    fs.writeFileSync(envPath, defaultEnv);
    console.log(`${colors.green}Created .env file. Please edit it with your configuration.${colors.reset}`);
  }
}

console.log(`\n${colors.green}Ensuring proper React setup...${colors.reset}`);

const srcDir = path.join(process.cwd(), 'src');
if (!fs.existsSync(srcDir)) {
  fs.mkdirSync(srcDir, { recursive: true });
  console.log(`${colors.green}Created src directory${colors.reset}`);
}

const indexPath = path.join(srcDir, 'index.js');
if (!fs.existsSync(indexPath)) {
  console.log(`${colors.blue}Creating default src/index.js file...${colors.reset}`);
  const defaultIndex = 
`import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import GitHubEventsDashboard from './components/dashboard/GitHubEventsDashboard';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <GitHubEventsDashboard />
  </React.StrictMode>
);
`;
  fs.writeFileSync(indexPath, defaultIndex);
  console.log(`${colors.green}Created src/index.js file${colors.reset}`);
}

const cssPath = path.join(srcDir, 'index.css');
if (!fs.existsSync(cssPath)) {
  console.log(`${colors.blue}Creating default src/index.css file...${colors.reset}`);
  const defaultCss = 
`@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f3f4f6;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
`;
  fs.writeFileSync(cssPath, defaultCss);
  console.log(`${colors.green}Created src/index.css file${colors.reset}`);
}

const publicDir = path.join(process.cwd(), 'public');
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true });
  console.log(`${colors.green}Created public directory${colors.reset}`);
  
  const htmlPath = path.join(publicDir, 'index.html');
  const defaultHtml = 
`<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="GitHub Events Dashboard" />
    <title>GitHub Events Dashboard</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
`;
  fs.writeFileSync(htmlPath, defaultHtml);
  console.log(`${colors.green}Created public/index.html file${colors.reset}`);
}

const dataDir = path.join(process.cwd(), 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
  console.log(`${colors.green}Created data directory${colors.reset}`);
}

const componentsDir = path.join(srcDir, 'components', 'dashboard');
if (!fs.existsSync(componentsDir)) {
  fs.mkdirSync(componentsDir, { recursive: true });
  console.log(`${colors.green}Created src/components/dashboard directory${colors.reset}`);
  
  const dashboardDir = path.join(process.cwd(), 'dashboard');
  if (fs.existsSync(dashboardDir)) {
    try {
      const files = fs.readdirSync(dashboardDir);
      let copiedCount = 0;
      
      for (const file of files) {
        if (file.endsWith('.jsx')) {
          const sourcePath = path.join(dashboardDir, file);
          const destPath = path.join(componentsDir, file);
          fs.copyFileSync(sourcePath, destPath);
          copiedCount++;
        }
      }
      
      if (copiedCount > 0) {
        console.log(`${colors.green}Copied ${copiedCount} dashboard components to src/components/dashboard${colors.reset}`);
      }
    } catch (error) {
      console.error(`${colors.yellow}Warning: Could not copy dashboard components: ${error.message}${colors.reset}`);
    }
  }
}

console.log(`\n${colors.green}\u2713 Post-installation setup completed successfully!${colors.reset}`);
console.log(`${colors.cyan}\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557${colors.reset}`);
console.log(`${colors.cyan}\u2551  GitEvents is ready to use!                 \u2551${colors.reset}`);
console.log(`${colors.cyan}\u2551  Run 'npm start' to launch the application  \u2551${colors.reset}`);
console.log(`${colors.cyan}\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d${colors.reset}`);
