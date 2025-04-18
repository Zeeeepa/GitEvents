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

// ANSI color codes for better console output
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

console.log(`${colors.cyan}╔════════════════════════════════════════════╗${colors.reset}`);
console.log(`${colors.cyan}║  GitEvents - Post-Installation Setup        ║${colors.reset}`);
console.log(`${colors.cyan}╚════════════════════════════════════════════╝${colors.reset}`);

// Function to safely execute commands with error handling
function safeExec(command, errorMessage) {
  try {
    console.log(`${colors.blue}> ${command}${colors.reset}`);
    return execSync(command, { stdio: 'inherit' });
  } catch (error) {
    console.error(`${colors.red}ERROR: ${errorMessage}${colors.reset}`);
    console.error(`${colors.yellow}Command failed: ${command}${colors.reset}`);
    console.error(`${colors.yellow}You may need to run this command manually.${colors.reset}`);
    // Don't exit - continue with other fixes
    return null;
  }
}

// Function to check if a package has vulnerabilities
function hasVulnerabilities(packageName) {
  try {
    const output = execSync(`npm audit --json`, { encoding: 'utf8' });
    const auditData = JSON.parse(output);
    
    // Check if vulnerabilities exist for the specified package
    if (auditData.vulnerabilities && auditData.vulnerabilities[packageName]) {
      return true;
    }
    
    return false;
  } catch (error) {
    console.error(`${colors.yellow}Warning: Could not check vulnerabilities for ${packageName}${colors.reset}`);
    return false;
  }
}

// Fix known vulnerabilities
console.log(`\n${colors.green}Checking for and fixing known vulnerabilities...${colors.reset}`);

// Check and fix nth-check vulnerability
if (hasVulnerabilities('nth-check')) {
  console.log(`${colors.yellow}Detected vulnerability in nth-check. Attempting to fix...${colors.reset}`);
  safeExec('npm install nth-check@2.1.1 --save-dev', 'Failed to update nth-check');
}

// Check and fix postcss vulnerability
if (hasVulnerabilities('postcss')) {
  console.log(`${colors.yellow}Detected vulnerability in postcss. Attempting to fix...${colors.reset}`);
  safeExec('npm install postcss@8.4.31 --save-dev', 'Failed to update postcss');
}

// Platform-specific setup
const isWindows = os.platform() === 'win32';
if (isWindows) {
  console.log(`\n${colors.green}Setting up Windows-specific configurations...${colors.reset}`);
  
  // Create .env file if it doesn't exist
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

// Ensure proper React setup
console.log(`\n${colors.green}Ensuring proper React setup...${colors.reset}`);

// Create src directory if it doesn't exist
const srcDir = path.join(process.cwd(), 'src');
if (!fs.existsSync(srcDir)) {
  fs.mkdirSync(srcDir, { recursive: true });
  console.log(`${colors.green}Created src directory${colors.reset}`);
}

// Create index.js if it doesn't exist
const indexPath = path.join(srcDir, 'index.js');
if (!fs.existsSync(indexPath)) {
  console.log(`${colors.blue}Creating default src/index.js file...${colors.reset}`);
  const defaultIndex = 
`import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import GitHubEventsDashboard from '../dashboard/GitHubEventsDashboard';

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

// Create index.css if it doesn't exist
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

// Create public directory and index.html if they don't exist
const publicDir = path.join(process.cwd(), 'public');
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true });
  console.log(`${colors.green}Created public directory${colors.reset}`);
  
  // Create index.html
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

// Create data directory if it doesn't exist
const dataDir = path.join(process.cwd(), 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
  console.log(`${colors.green}Created data directory${colors.reset}`);
}

console.log(`\n${colors.green}✓ Post-installation setup completed successfully!${colors.reset}`);
console.log(`${colors.cyan}╔════════════════════════════════════════════╗${colors.reset}`);
console.log(`${colors.cyan}║  GitEvents is ready to use!                 ║${colors.reset}`);
console.log(`${colors.cyan}║  Run 'npm start' to launch the application  ║${colors.reset}`);
console.log(`${colors.cyan}╚════════════════════════════════════════════╝${colors.reset}`);
