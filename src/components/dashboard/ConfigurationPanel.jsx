import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const ConfigurationPanel = () => {
  const [githubToken, setGithubToken] = useState('');
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookSecret, setWebhookSecret] = useState('');
  const [dbPath, setDbPath] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setSuccessMessage(null);
      setError(null);
      
      // In a real application, this would send the configuration to the backend
      // For now, we'll just simulate a successful save
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccessMessage('Configuration saved successfully!');
    } catch (err) {
      console.error('Error saving configuration:', err);
      setError('Failed to save configuration. Please try again later.');
    } finally {
      setSaving(false);
      
      // Clear success message after 3 seconds
      if (successMessage) {
        setTimeout(() => {
          setSuccessMessage(null);
        }, 3000);
      }
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-6">System Configuration</h2>
      
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      
      {successMessage && (
        <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
          {successMessage}
        </div>
      )}
      
      <form onSubmit={handleSaveConfig}>
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-4">GitHub Integration</h3>
            
            <div className="mb-4">
              <label htmlFor="github-token" className="block text-sm font-medium text-gray-700 mb-1">
                GitHub API Token
              </label>
              <input
                type="password"
                id="github-token"
                value={githubToken}
                onChange={(e) => setGithubToken(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
              />
              <p className="mt-1 text-xs text-gray-500">
                Personal access token with repo and webhook permissions
              </p>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-medium mb-4">Webhook Configuration</h3>
            
            <div className="mb-4">
              <label htmlFor="webhook-url" className="block text-sm font-medium text-gray-700 mb-1">
                Webhook URL
              </label>
              <input
                type="text"
                id="webhook-url"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="https://example.com/webhook"
              />
              <p className="mt-1 text-xs text-gray-500">
                URL where GitHub will send webhook events
              </p>
            </div>
            
            <div className="mb-4">
              <label htmlFor="webhook-secret" className="block text-sm font-medium text-gray-700 mb-1">
                Webhook Secret
              </label>
              <input
                type="password"
                id="webhook-secret"
                value={webhookSecret}
                onChange={(e) => setWebhookSecret(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="webhook_secret_key"
              />
              <p className="mt-1 text-xs text-gray-500">
                Secret key for webhook payload verification
              </p>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-medium mb-4">Database Configuration</h3>
            
            <div className="mb-4">
              <label htmlFor="db-path" className="block text-sm font-medium text-gray-700 mb-1">
                Database Path
              </label>
              <input
                type="text"
                id="db-path"
                value={dbPath}
                onChange={(e) => setDbPath(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="/path/to/github_events.db"
              />
              <p className="mt-1 text-xs text-gray-500">
                Path to SQLite database file (leave empty for default)
              </p>
            </div>
          </div>
          
          <div className="pt-4 border-t border-gray-200">
            <button
              type="submit"
              disabled={saving}
              className={`px-4 py-2 rounded-md text-white font-medium ${
                saving ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
              }`}
            >
              {saving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ConfigurationPanel;
