# GitEvents - GitHub Events Dashboard

GitEvents is a comprehensive dashboard for monitoring GitHub events in real-time. It provides a user-friendly interface to track pull requests, branch events, and push events across your repositories.

## Features

- **Real-time Event Monitoring**: Track GitHub events as they happen
- **Repository Management**: View and manage repositories
- **Pull Request Tracking**: Monitor pull requests and their status
- **Customizable Settings**: Configure notifications and automation
- **System Configuration**: Set up GitHub integration and webhooks

## Tech Stack

- **Frontend**: React with Tailwind CSS
- **Backend**: Python with FastAPI
- **Database**: SQLite with SQLAlchemy ORM

## Installation

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- Git

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/GitEvents.git
   cd GitEvents
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables (optional):
   ```
   export GITHUB_EVENTS_DB=path/to/database.db
   export API_PORT=8001
   ```

4. Start the backend server:
   ```
   python main.py
   ```

### Frontend Setup

1. Install Node.js dependencies:
   ```
   npm install
   ```

2. Set up environment variables (optional):
   Create a `.env` file in the root directory:
   ```
   REACT_APP_API_URL=http://localhost:8001/api
   ```

3. Start the frontend development server:
   ```
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000`

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
│   ├── api_service.py    # FastAPI application
│   └── api_service_settings.py
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
├── main.py               # Application entry point
├── package.json          # Node.js dependencies
├── requirements.txt      # Python dependencies
└── tailwind.config.js    # Tailwind CSS configuration
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
