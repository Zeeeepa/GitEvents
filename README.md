# GitEvents - GitHub Events Dashboard

GitEvents is a comprehensive dashboard for monitoring GitHub events in real-time. It provides a user-friendly interface to track pull requests, branch events, and push events across your repositories.

## Features

- **Event Tracking**: Monitor GitHub events in real-time
- **Repository Insights**: View repository activity and statistics
- **User Activity**: Track user contributions and activity
- **Pull Request Tracking**: Monitor pull requests and their status
- **Customizable Settings**: Configure notifications and automation
- **System Configuration**: Set up GitHub integration and webhooks
- **Webhook Support**: Receive and process GitHub webhook events
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Ngrok Integration**: Expose local webhook endpoints to the internet

## Tech Stack

- **Frontend**: React with Tailwind CSS
- **Backend**: Python with FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Containerization**: Docker and Docker Compose
- **Tunneling**: Ngrok for exposing local endpoints

## Installation

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- Git
- Docker and Docker Compose (optional, for containerized deployment)
- Ngrok account (optional, for webhook tunneling)

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
   
   # Ngrok Configuration
   ENABLE_NGROK=false
   NGROK_AUTH_TOKEN=your_ngrok_auth_token_here
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

### Using Ngrok for Webhook Development

If you're developing locally and need to receive GitHub webhooks, you can use ngrok to expose your local webhook endpoint to the internet:

1. Set up ngrok in your `.env` file:
   ```
   ENABLE_NGROK=true
   NGROK_AUTH_TOKEN=your_ngrok_auth_token_here
   ```

2. Start the application:
   ```
   python main.py
   ```

3. The application will automatically start ngrok tunnels and display the public URLs for your webhook and API endpoints.

4. Use the displayed webhook URL in your GitHub repository webhook settings.

## Usage

### Dashboard

View GitHub events, repository activity, and user contributions in real-time.

### Event Filtering

Filter events by type, repository, user, or date range.

### System Configuration

Set up GitHub integration, webhook configuration, and database settings.

## Project Structure

```
GitEvents/
├── api/                  # Backend API code
│   ├── api_service.py    # FastAPI application for main API
│   ├── api_service_settings.py
│   ├── webhook_handler.py # Webhook handler for GitHub events
│   └── ngrok_service.py  # Ngrok integration for exposing local endpoints
├── dashboard/            # Frontend React components
│   ├── GitHubEventsDashboard.jsx
│   ├── RecentEvents.jsx
│   ├── RepositoryInsights.jsx
│   └── UserActivity.jsx
├── db/                   # Database models and managers
│   ├── db_manager.py
│   └── models.py
├── handlers/             # Event handlers
│   └── github_event_handler.py
├── managers/             # Business logic managers
│   ├── event_manager.py
│   ├── repository_manager.py
│   └── user_manager.py
├── public/               # Static assets
│   ├── index.html
│   └── favicon.ico
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
└── README.md             # Project documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
