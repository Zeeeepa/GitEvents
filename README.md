# GitEvents - GitHub Events Dashboard

GitEvents is a comprehensive dashboard for monitoring GitHub events in real-time. It provides a user-friendly interface to track pull requests, branch events, and push events across your repositories.

## Features

- **Real-time Event Monitoring**: Track GitHub events as they happen
- **Repository Management**: View and manage repositories
- **Pull Request Tracking**: Monitor pull requests and their status
- **Customizable Settings**: Configure notifications and automation
- **System Configuration**: Set up GitHub integration and webhooks
- **Webhook Support**: Receive and process GitHub webhook events
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Tech Stack

- **Frontend**: React with Tailwind CSS
- **Backend**: Python with FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Containerization**: Docker and Docker Compose

## Installation

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- Git
- Docker and Docker Compose (optional, for containerized deployment)

### Environment Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/GitEvents.git
   cd GitEvents
   ```

2. Create a `.env` file based on the example:
   ```
   cp .env.example .env
   ```

3. Edit the `.env` file with your GitHub token and other settings:
   ```
   # API Configuration
   API_PORT=8001
   WEBHOOK_PORT=8002

   # GitHub Configuration
   GITHUB_TOKEN=your_github_token_here
   GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

   # Database Configuration
   GITHUB_EVENTS_DB=github_events.db

   # Frontend Configuration
   REACT_APP_API_URL=http://localhost:8001/api
   ```

### Standard Setup

#### Backend Setup

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start the backend server:
   ```
   python main.py
   ```

   This will start both the API server on port 8001 and the webhook handler on port 8002.

#### Frontend Setup

1. Install Node.js dependencies:
   ```
   npm install
   ```

2. Start the frontend development server:
   ```
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

### Docker Setup

1. Make sure Docker and Docker Compose are installed on your system.

2. Build and start the containers:
   ```
   docker-compose up -d
   ```

3. Open your browser and navigate to `http://localhost:3000`

4. To stop the containers:
   ```
   docker-compose down
   ```

## Webhook Configuration

To receive GitHub webhook events:

1. Go to your GitHub repository settings
2. Navigate to Webhooks > Add webhook
3. Set the Payload URL to `http://your-server:8002/webhook/github`
4. Set the Content type to `application/json`
5. Set the Secret to match your `GITHUB_WEBHOOK_SECRET` environment variable
6. Select the events you want to receive (recommended: Pull requests, Pushes, and Branch creation/deletion)
7. Ensure the webhook is active

## Usage

### Dashboard

The main dashboard displays recent GitHub events. You can filter events by type and repository.

### Repositories

The repositories section shows all connected GitHub repositories. Click on a repository to view its pull requests.

### Settings

Configure notification settings, automatic PR creation, and post-merge scripts.

### Configuration

Set up GitHub integration, webhook configuration, and database settings.

## Development

### Project Structure

```
GitEvents/
├── api/                  # Backend API code
│   ├── api_service.py    # FastAPI application for main API
│   ├── api_service_settings.py
│   └── webhook_handler.py # Webhook handler for GitHub events
├── dashboard/            # Frontend React components
│   ├── GitHubEventsDashboard.jsx
│   ├── RecentEvents.jsx
│   ├── RepositoryList.jsx
│   ├── RepositoryPRs.jsx
│   ├── SettingsPanel.jsx
│   └── ConfigurationPanel.jsx
├── db/                   # Database models and manager
│   ├── db_manager.py
│   └── db_schema.py
├── handlers/             # Event handlers
│   └── github_event_handler.py
├── managers/             # Business logic managers
│   ├── auto_branch_pr_manager.py
│   ├── github_integration_manager.py
│   └── notification_manager.py
├── public/               # Static assets
├── src/                  # React application source
│   ├── index.js
│   └── index.css
├── data/                 # Database storage
├── .env.example          # Example environment variables
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker configuration
├── main.py               # Application entry point
├── package.json          # Node.js dependencies
├── requirements.txt      # Python dependencies
└── tailwind.config.js    # Tailwind CSS configuration
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
