import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const SettingsPanel = ({ onSettingsChanged }) => {
  const [settings, setSettings] = useState({
    notifications: { enabled: false },
    auto_pr: { enabled: false, running: false },
    post_merge_scripts: { enabled: false }
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/settings/status`);
      setSettings(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching settings:', err);
      setError('Failed to load settings. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (settingKey) => {
    setSettings(prevSettings => {
      const newSettings = { ...prevSettings };
      newSettings[settingKey].enabled = !newSettings[settingKey].enabled;
      return newSettings;
    });
  };

  const saveSettings = async () => {
    try {
      setSaving(true);
      setSuccessMessage(null);
      setError(null);
      
      await axios.post(`${API_BASE_URL}/settings/update`, settings);
      
      setSuccessMessage('Settings saved successfully!');
      if (onSettingsChanged) {
        onSettingsChanged();
      }
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
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium">Notifications</h3>
            <p className="text-sm text-gray-500">
              Receive notifications for GitHub events
            </p>
          </div>
          <div className="relative inline-block w-12 mr-2 align-middle select-none">
            <input
              type="checkbox"
              id="toggle-notifications"
              checked={settings.notifications.enabled}
              onChange={() => handleToggle('notifications')}
              className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
              style={{
                right: settings.notifications.enabled ? '0' : 'auto',
                transition: 'right 0.2s ease-in-out',
                backgroundColor: settings.notifications.enabled ? '#4F46E5' : 'white',
                borderColor: settings.notifications.enabled ? '#4F46E5' : '#D1D5DB'
              }}
            />
            <label
              htmlFor="toggle-notifications"
              className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
              style={{
                backgroundColor: settings.notifications.enabled ? '#C7D2FE' : '#D1D5DB'
              }}
            ></label>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium">Auto PR Creation</h3>
            <p className="text-sm text-gray-500">
              Automatically create PRs for new branches
            </p>
          </div>
          <div className="relative inline-block w-12 mr-2 align-middle select-none">
            <input
              type="checkbox"
              id="toggle-auto-pr"
              checked={settings.auto_pr.enabled}
              onChange={() => handleToggle('auto_pr')}
              className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
              style={{
                right: settings.auto_pr.enabled ? '0' : 'auto',
                transition: 'right 0.2s ease-in-out',
                backgroundColor: settings.auto_pr.enabled ? '#4F46E5' : 'white',
                borderColor: settings.auto_pr.enabled ? '#4F46E5' : '#D1D5DB'
              }}
            />
            <label
              htmlFor="toggle-auto-pr"
              className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
              style={{
                backgroundColor: settings.auto_pr.enabled ? '#C7D2FE' : '#D1D5DB'
              }}
            ></label>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium">Post-Merge Scripts</h3>
            <p className="text-sm text-gray-500">
              Run scripts automatically after PR merges
            </p>
          </div>
          <div className="relative inline-block w-12 mr-2 align-middle select-none">
            <input
              type="checkbox"
              id="toggle-post-merge"
              checked={settings.post_merge_scripts.enabled}
              onChange={() => handleToggle('post_merge_scripts')}
              className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
              style={{
                right: settings.post_merge_scripts.enabled ? '0' : 'auto',
                transition: 'right 0.2s ease-in-out',
                backgroundColor: settings.post_merge_scripts.enabled ? '#4F46E5' : 'white',
                borderColor: settings.post_merge_scripts.enabled ? '#4F46E5' : '#D1D5DB'
              }}
            />
            <label
              htmlFor="toggle-post-merge"
              className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
              style={{
                backgroundColor: settings.post_merge_scripts.enabled ? '#C7D2FE' : '#D1D5DB'
              }}
            ></label>
          </div>
        </div>
        
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
    </div>
  );
};

export default SettingsPanel;
