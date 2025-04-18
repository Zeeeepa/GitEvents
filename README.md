# GitEvents

A dashboard for monitoring GitHub events.

## Installation and Setup

1. Make sure you have the following prerequisites installed:
   - Python 3.6 or higher
   - Node.js and npm
   - Git

2. Clone this repository:
   ```
   git clone https://github.com/Zeeeepa/GitEvents.git
   cd GitEvents
   ```

3. Run the installation script:
   ```
   InstallAndStart.bat
   ```
   This will:
   - Create a Python virtual environment
   - Install Python dependencies
   - Install Node.js dependencies
   - Set up the database
   - Start the backend and frontend servers

## Troubleshooting

### "react-scripts is not recognized" Error

If you encounter an error about "react-scripts" not being recognized, you can fix it by:

1. Running the provided fix script:
   ```
   FixReactScripts.bat
   ```

2. Or manually installing react-scripts:
   ```
   npm install react-scripts --save-dev
   ```
   or globally:
   ```
   npm install -g react-scripts
   ```

### Other Common Issues

- **Backend fails to start**: Make sure all Python dependencies are installed correctly by running `pip install -r requirements.txt` in the virtual environment.
- **Frontend fails to start**: Make sure all Node.js dependencies are installed correctly by running `npm install`.
- **Database connection issues**: Check your .env file for correct database configuration.

## Starting the Application

After installation, you can start the application using:

```
start.bat
```

This will start both the backend and frontend servers.

- Backend: http://localhost:8001
- Frontend: http://localhost:3000

## Configuration

The application uses a .env file for configuration. If this file doesn't exist, it will be created during the installation process with interactive prompts.

Key configuration options:
- GitHub API token
- Database settings
- API ports
- Webhook configuration
