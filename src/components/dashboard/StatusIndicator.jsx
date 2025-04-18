import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const StatusIndicator = () => {
  const [status, setStatus] = useState({
    github_api: {
      connected: false,
      message: 'Loading...',
      username: null
    },
    ngrok: {
      enabled: false,
      connected: false,
      message: 'Loading...',
      webhook_url: null,
      api_url: null
    }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStatus();
    // Refresh status every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/settings/status`);
      setStatus(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching status:', err);
      setError('Failed to load status. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-4 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">System Status</h2>
        <button
          onClick={fetchStatus}
          className="text-blue-500 hover:text-blue-700"
          disabled={loading}
        >
          <svg className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
          </svg>
        </button>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* GitHub API Status */}
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium">GitHub API</h3>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              status.github_api.connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {status.github_api.connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <p className="text-sm text-gray-600">{status.github_api.message}</p>
          {status.github_api.username && (
            <p className="text-sm text-gray-600 mt-1">
              Authenticated as: <span className="font-medium">{status.github_api.username}</span>
            </p>
          )}
        </div>

        {/* Ngrok Status */}
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium">Ngrok Tunnels</h3>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              !status.ngrok.enabled ? 'bg-gray-100 text-gray-800' :
              status.ngrok.connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {!status.ngrok.enabled ? 'Disabled' :
               status.ngrok.connected ? 'Active' : 'Inactive'}
            </span>
          </div>
          <p className="text-sm text-gray-600">{status.ngrok.message}</p>
          
          {status.ngrok.webhook_url && (
            <div className="mt-2">
              <p className="text-xs text-gray-500">Webhook URL:</p>
              <div className="flex items-center">
                <input
                  type="text"
                  value={status.ngrok.webhook_url}
                  readOnly
                  className="text-xs bg-gray-50 border border-gray-200 rounded py-1 px-2 w-full"
                />
                <button
                  onClick={() => navigator.clipboard.writeText(status.ngrok.webhook_url)}
                  className="ml-2 text-blue-500 hover:text-blue-700"
                  title="Copy to clipboard"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                    <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                  </svg>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatusIndicator;
