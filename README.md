# GitEvents

A real-time GitHub events dashboard that allows you to monitor repository activities, pull requests, and more.

## Features

- Real-time monitoring of GitHub events via webhooks
- Dashboard for visualizing repository activities
- Pull request tracking and notifications
- Branch monitoring and event history
- Configurable settings for notifications and automations
- Support for both SQLite and MySQL databases
- Easy setup with ngrok for webhook testing
- One-click deployment options for all platforms

## System Requirements

- Python 3.8+
- Node.js 14+
- npm or yarn
- Git

## Quick Start (All Platforms)

### Option 1: One-Click Deployment Script

The easiest way to deploy GitEvents is using our universal deployment script:

1. Clone the repository:
   ```bash
   git clone https://github.com/Zeeeepa/GitEvents.git
   cd GitEvents
   ```

2. Run the deployment script:
   - **Linux/macOS**: `./deploy.sh`
   - **Windows**: `deploy.bat`

   This script will:
   - Check for required dependencies
   - Set up the environment
   - Create a Python virtual environment
   - Install Python and Node.js dependencies
   - Initialize the database
   - Start the backend and frontend servers

3. Access the application:
   - Frontend: http://localhost:3000
   - API: http://localhost:8001
   - Webhook endpoint: http://localhost:8002/webhook/github

### Option 2: Docker Deployment

For a containerized deployment:

1. Clone the repository:
   ```bash
   git clone https://github.com/Zeeeepa/GitEvents.git
   cd GitEvents
   ```

2. Run the Docker deployment script:
   - **Linux/macOS**: `./docker-deploy.sh`
   - **Windows**: Use Docker Desktop and run `docker-compose up -d`

3. Access the application:
   - Frontend: http://localhost:3000
   - API: http://localhost:8001
   - Webhook endpoint: http://localhost:8002/webhook/github

## Manual Setup

### Windows

1. Clone the repository:
   ```
   git clone https://github.com/Zeeeepa/GitEvents.git
   cd GitEvents
   ```

2. Create and configure the environment file:
   ```
   copy .env.example .env
   ```
   Edit the `.env` file with your GitHub token and other settings.

3. Create a Python virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Install Node.js dependencies:
   ```
   npm install
   ```

6. Start the backend server:
   ```
   python main.py
   ```

7. In a new terminal, start the frontend server:
   ```
   npm start
   ```

### Linux/macOS

1. Clone the repository:
   ```bash
   git clone https://github.com/Zeeeepa/GitEvents.git
   cd GitEvents
   ```

2. Create and configure the environment file:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your GitHub token and other settings.

3. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Install Node.js dependencies:
   ```bash
   npm install
   ```

6. Start the backend server:
   ```bash
   python main.py
   ```

7. In a new terminal, start the frontend server:
   ```bash
   npm start
   ```

## Setting Up Ngrok for Webhooks

To receive GitHub webhooks on your local machine, you need to expose your webhook endpoint to the internet. Ngrok is a tool that creates a secure tunnel to your local server.

1. Sign up for a free ngrok account at https://ngrok.com/

2. Get your auth token from the ngrok dashboard

3. Update your `.env` file:
   ```
   ENABLE_NGROK=true
   NGROK_AUTH_TOKEN=your_ngrok_auth_token_here
   ```

4. Start the application using one of the deployment methods

5. The ngrok URL will be displayed in the console. Use this URL to set up your GitHub webhook:
   - Go to your GitHub repository
   - Click on Settings > Webhooks > Add webhook
   - Set Payload URL to the ngrok URL + `/webhook/github`
   - Set Content type to `application/json`
   - Set Secret to the value of `GITHUB_WEBHOOK_SECRET` in your `.env` file
   - Select events you want to trigger the webhook
   - Click "Add webhook"

6. The ngrok web interface is available at http://localhost:4040

## Database Configuration

By default, GitEvents uses SQLite, which requires no additional setup. For MySQL:

1. Install MySQL Server for your platform

2. Create a new database:
   ```sql
   CREATE DATABASE github_events;
   ```

3. Update your `.env` file:
   ```
   DB_TYPE=mysql
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=github_events
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   ```

## Command Line Options

The deployment script supports several command line options:

```
python deploy.py [--no-frontend] [--no-browser] [--debug]
```

Options:
- `--no-frontend`: Skip starting the frontend server
- `--no-browser`: Don't open browser automatically
- `--debug`: Enable debug mode with verbose logging

## Project Structure

- `/api` - Backend API services
- `/dashboard` - React components for the dashboard
- `/db` - Database models and managers
- `/handlers` - Event handlers for GitHub webhooks
- `/managers` - Business logic for handling events
- `/public` - Static assets for the frontend
- `/src` - Frontend source code

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
