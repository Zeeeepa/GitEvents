import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DatabaseManagement from './DatabaseManagement';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const SettingsPanel = () => {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [activeTab, setActiveTab] = useState('general'); // 'general' or 'database'

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/settings`);
      setSettings(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching settings:', err);
      setError('Failed to load settings. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      [field]: value
    }));
  };

  const saveSettings = async () => {
    try {
      setSaving(true);
      setSuccessMessage(null);
      setError(null);
      
      await axios.post(`${API_BASE_URL}/settings`, settings);
      
      setSuccessMessage('Settings saved successfully!');
    } catch (err) {
      console.error('Error saving settings:', err);
      setError('Failed to save settings. Please try again later.');
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
        <h2 className="text-xl font-semibold mb-4">Settings</h2>
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-6">Settings</h2>
      
      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('general')}
            className={`${
              activeTab === 'general'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            General Settings
          </button>
          <button
            onClick={() => setActiveTab('database')}
            className={`${
              activeTab === 'database'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Database Management
          </button>
        </nav>
      </div>
      
      {activeTab === 'general' && (
        <>
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
          
          <div className="space-y-6">
            <div className="mb-4">
              <label htmlFor="github-token" className="block text-sm font-medium text-gray-700">
                GitHub Token
              </label>
              <input
                type="password"
                id="github-token"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="Enter your GitHub token"
                value={settings.github_token || ''}
                onChange={(e) => handleChange('github_token', e.target.value)}
              />
              <p className="mt-1 text-sm text-gray-500">
                Your GitHub personal access token with repo and webhook permissions
              </p>
            </div>
            
            <div className="flex items-center mb-4">
              <input
                type="checkbox"
                id="enable-ngrok"
                checked={settings.enable_ngrok || false}
                onChange={(e) => handleChange('enable_ngrok', e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="enable-ngrok" className="ml-2 block text-sm text-gray-700">
                Enable Ngrok for webhook tunneling
              </label>
            </div>
            
            {settings.enable_ngrok && (
              <div className="mb-4 ml-6 p-4 border-l-2 border-indigo-100">
                <label htmlFor="ngrok-token" className="block text-sm font-medium text-gray-700">
                  Ngrok Auth Token
                </label>
                <input
                  type="password"
                  id="ngrok-token"
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Enter your Ngrok auth token"
                  value={settings.ngrok_auth_token || ''}
                  onChange={(e) => handleChange('ngrok_auth_token', e.target.value)}
                />
                <p className="mt-1 text-sm text-gray-500">
                  Your Ngrok authentication token for creating tunnels
                </p>
              </div>
            )}
            
            <div className="pt-4 border-t border-gray-200">
              <button
                onClick={saveSettings}
                disabled={saving}
                className={`px-4 py-2 rounded-md text-white font-medium ${
                  saving ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
                }`}
              >
                {saving ? 'Saving...' : 'Save Settings'}
              </button>
            </div>
          </div>
        </>
      )}
      
      {activeTab === 'database' && (
        <DatabaseManagement />
      )}
    </div>
  );
};

export default SettingsPanel;
