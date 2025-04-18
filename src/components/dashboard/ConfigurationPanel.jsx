import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const ConfigurationPanel = () => {
  const [githubToken, setGithubToken] = useState('');
  const [ngrokEnabled, setNgrokEnabled] = useState(true);
  const [ngrokAuthToken, setNgrokAuthToken] = useState('');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [config, setConfig] = useState({});

  useEffect(() => {
    // Fetch current configuration
    fetchConfiguration();
  }, []);

  const fetchConfiguration = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/settings`);
      const data = response.data;
      
      setGithubToken(data.github_token || '');
      setNgrokEnabled(data.enable_ngrok || true);
      setNgrokAuthToken(data.ngrok_auth_token || '');
      setConfig(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching configuration:', err);
      setError('Failed to load configuration. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setSuccessMessage(null);
      setError(null);
      
      const configData = {
        github_token: githubToken,
        enable_ngrok: ngrokEnabled,
        ngrok_auth_token: ngrokAuthToken
      };
      
      const response = await axios.post(`${API_BASE_URL}/settings`, configData);
      
      if (response.data.success) {
        setSuccessMessage('Configuration saved successfully!');
        await fetchConfiguration();
      } else {
        setError(response.data.message || 'Failed to save configuration.');
      }
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

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-6">System Configuration</h2>
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

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
            <h3 className="text-lg font-medium mb-4">Ngrok Configuration</h3>
            
            <div className="mb-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="enable-ngrok"
                  checked={ngrokEnabled}
                  onChange={(e) => setNgrokEnabled(e.target.checked)}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="enable-ngrok" className="ml-2 block text-sm text-gray-700">
                  Enable Ngrok for webhook tunneling
                </label>
              </div>
              <p className="mt-1 text-xs text-gray-500">
                Automatically creates a public URL for receiving GitHub webhooks
              </p>
            </div>
            
            {ngrokEnabled && (
              <div className="mb-4">
                <label htmlFor="ngrok-auth-token" className="block text-sm font-medium text-gray-700 mb-1">
                  Ngrok Auth Token
                </label>
                <input
                  type="password"
                  id="ngrok-auth-token"
                  value={ngrokAuthToken}
                  onChange={(e) => setNgrokAuthToken(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="your_ngrok_auth_token"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Auth token from your Ngrok account (required for stable URLs)
                </p>
              </div>
            )}
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
