import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DatabaseManagement from './DatabaseManagement';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const SettingsPanel = ({ onSettingsChanged }) => {
  const [settings, setSettings] = useState({
    notifications: { enabled: false },
    auto_pr: { enabled: false, running: false, add_comment: false, comment_text: '' },
    post_merge_scripts: { enabled: false, selected_project: '', selected_script: '' },
    projects: [],
    scripts: []
  });
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

  const handlePRCommentToggle = () => {
    setSettings(prevSettings => {
      const newSettings = { ...prevSettings };
      newSettings.auto_pr.add_comment = !newSettings.auto_pr.add_comment;
      return newSettings;
    });
  };

  const handleCommentTextChange = (e) => {
    setSettings(prevSettings => {
      const newSettings = { ...prevSettings };
      newSettings.auto_pr.comment_text = e.target.value;
      return newSettings;
    });
  };

  const handleProjectChange = (e) => {
    setSettings(prevSettings => {
      const newSettings = { ...prevSettings };
      newSettings.post_merge_scripts.selected_project = e.target.value;
      return newSettings;
    });
  };

  const handleScriptChange = (e) => {
    setSettings(prevSettings => {
      const newSettings = { ...prevSettings };
      newSettings.post_merge_scripts.selected_script = e.target.value;
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

            {settings.auto_pr.enabled && (
              <div className="ml-6 p-4 border-l-2 border-indigo-100">
                <div className="flex items-center mb-3">
                  <input
                    type="checkbox"
                    id="toggle-pr-comment"
                    checked={settings.auto_pr.add_comment}
                    onChange={handlePRCommentToggle}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor="toggle-pr-comment" className="ml-2 block text-sm text-gray-700">
                    Add Comment when PR is created
                  </label>
                </div>
                
                {settings.auto_pr.add_comment && (
                  <div className="mt-2">
                    <label htmlFor="pr-comment-text" className="block text-sm font-medium text-gray-700">
                      Comment Text
                    </label>
                    <textarea
                      id="pr-comment-text"
                      rows="3"
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Enter comment text to add to new PRs"
                      value={settings.auto_pr.comment_text}
                      onChange={handleCommentTextChange}
                    ></textarea>
                  </div>
                )}
              </div>
            )}
            
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

            {settings.post_merge_scripts.enabled && (
              <div className="ml-6 p-4 border-l-2 border-indigo-100">
                <div className="mb-3">
                  <label htmlFor="project-select" className="block text-sm font-medium text-gray-700">
                    Select Project
                  </label>
                  <select
                    id="project-select"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    value={settings.post_merge_scripts.selected_project}
                    onChange={handleProjectChange}
                  >
                    <option value="">Select a project</option>
                    {settings.projects && settings.projects.map((project, index) => (
                      <option key={index} value={project.id}>{project.name}</option>
                    ))}
                  </select>
                </div>
                
                <div className="mb-3">
                  <label htmlFor="script-select" className="block text-sm font-medium text-gray-700">
                    Select Script
                  </label>
                  <select
                    id="script-select"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    value={settings.post_merge_scripts.selected_script}
                    onChange={handleScriptChange}
                    disabled={!settings.post_merge_scripts.selected_project}
                  >
                    <option value="">Select a script</option>
                    {settings.scripts && settings.scripts.map((script, index) => (
                      <option key={index} value={script.id}>{script.name}</option>
                    ))}
                  </select>
                </div>
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
