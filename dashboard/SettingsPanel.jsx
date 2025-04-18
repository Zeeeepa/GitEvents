import React, { useState, useEffect } from 'react';
import axios from 'axios';

// API URL - configure this to match your API service
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const SettingsPanel = () => {
  // Notification settings
  const [notificationSettings, setNotificationSettings] = useState({
    enabled: false,
    settings: {
      'pull_request:opened': true,
      'pull_request:closed': true,
      'pull_request:merged': true,
      'branch:created': false,
      'branch:deleted': false,
      'push': false
    },
    status: {
      enabled: false,
      platform: ''
    }
  });

  // Auto PR settings
  const [autoPrSettings, setAutoPrSettings] = useState({
    enabled: false,
    title_template: 'PR for branch: {branch_name}',
    body_template: 'Automatically created PR for branch `{branch_name}`.',
    base_branch: 'main',
    auto_assign_creator: true,
    excluded_branches: ['main', 'master', 'dev', 'develop', 'release', 'hotfix'],
    included_repos: []
  });
  
  // Post-merge scripts
  const [postMergeScripts, setPostMergeScripts] = useState([]);
  const [newScript, setNewScript] = useState({
    project_name: '',
    script_path: '',
    repo_patterns: '',
    enabled: true
  });
  
  // Repositories for selection
  const [repositories, setRepositories] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState('');
  
  // Status messages
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  // Fetch settings on component mount
  useEffect(() => {
    fetchSettings();
    fetchRepositories();
  }, []);

  const fetchSettings = async () => {
    try {
      // Fetch notification settings
      const notificationResponse = await axios.get(`${API_BASE_URL}/settings/notifications`);
      setNotificationSettings(notificationResponse.data);
      
      // Fetch auto PR settings
      const autoPrResponse = await axios.get(`${API_BASE_URL}/settings/auto-pr`);
      setAutoPrSettings(autoPrResponse.data);
      
      // Fetch post-merge scripts
      const scriptsResponse = await axios.get(`${API_BASE_URL}/settings/post-merge-scripts`);
      setPostMergeScripts(scriptsResponse.data);
      
      setStatusMessage('Settings loaded successfully');
      setTimeout(() => setStatusMessage(''), 3000);
    } catch (error) {
      console.error('Error fetching settings:', error);
      setErrorMessage('Failed to load settings. Please try again.');
      setTimeout(() => setErrorMessage(''), 5000);
    }
  };
  
  const fetchRepositories = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/repos`);
      setRepositories(response.data);
    } catch (error) {
      console.error('Error fetching repositories:', error);
    }
  };

  const saveNotificationSettings = async () => {
    try {
      await axios.post(`${API_BASE_URL}/settings/notifications`, {
        enabled: notificationSettings.enabled,
        settings: notificationSettings.settings
      });
      
      setStatusMessage('Notification settings saved successfully');
      setTimeout(() => setStatusMessage(''), 3000);
    } catch (error) {
      console.error('Error saving notification settings:', error);
      setErrorMessage('Failed to save notification settings');
      setTimeout(() => setErrorMessage(''), 5000);
    }
  };

  const saveAutoPrSettings = async () => {
    try {
      await axios.post(`${API_BASE_URL}/settings/auto-pr`, autoPrSettings);
      
      setStatusMessage('Auto PR settings saved successfully');
      setTimeout(() => setStatusMessage(''), 3000);
    } catch (error) {
      console.error('Error saving Auto PR settings:', error);
      setErrorMessage('Failed to save Auto PR settings');
      setTimeout(() => setErrorMessage(''), 5000);
    }
  };
  
  const addPostMergeScript = async () => {
    try {
      // Convert comma-separated repo patterns to array
      const repoPatterns = newScript.repo_patterns
        .split(',')
        .map(pattern => pattern.trim())
        .filter(pattern => pattern.length > 0);
      
      const scriptToAdd = {
        ...newScript,
        repo_patterns: repoPatterns
      };
      
      await axios.post(`${API_BASE_URL}/settings/post-merge-scripts`, scriptToAdd);
      
      // Refresh scripts list
      const scriptsResponse = await axios.get(`${API_BASE_URL}/settings/post-merge-scripts`);
      setPostMergeScripts(scriptsResponse.data);
      
      // Reset form
      setNewScript({
        project_name: '',
        script_path: '',
        repo_patterns: '',
        enabled: true
      });
      
      setStatusMessage('Post-merge script added successfully');
      setTimeout(() => setStatusMessage(''), 3000);
    } catch (error) {
      console.error('Error adding post-merge script:', error);
      setErrorMessage('Failed to add post-merge script');
      setTimeout(() => setErrorMessage(''), 5000);
    }
  };
  
  const removePostMergeScript = async (projectName) => {
    try {
      await axios.delete(`${API_BASE_URL}/settings/post-merge-scripts/${encodeURIComponent(projectName)}`);
      
      // Refresh scripts list
      const scriptsResponse = await axios.get(`${API_BASE_URL}/settings/post-merge-scripts`);
      setPostMergeScripts(scriptsResponse.data);
      
      setStatusMessage('Post-merge script removed successfully');
      setTimeout(() => setStatusMessage(''), 3000);
    } catch (error) {
      console.error('Error removing post-merge script:', error);
      setErrorMessage('Failed to remove post-merge script');
      setTimeout(() => setErrorMessage(''), 5000);
    }
  };
  
  const togglePostMergeScript = async (projectName, enabled) => {
    try {
      await axios.patch(`${API_BASE_URL}/settings/post-merge-scripts/${encodeURIComponent(projectName)}`, {
        enabled: !enabled
      });
      
      // Refresh scripts list
      const scriptsResponse = await axios.get(`${API_BASE_URL}/settings/post-merge-scripts`);
      setPostMergeScripts(scriptsResponse.data);
      
      setStatusMessage('Script status updated successfully');
      setTimeout(() => setStatusMessage(''), 3000);
    } catch (error) {
      console.error('Error updating script status:', error);
      setErrorMessage('Failed to update script status');
      setTimeout(() => setErrorMessage(''), 5000);
    }
  };
  
  const addRepoToAutoPR = () => {
    if (!selectedRepo) return;
    
    if (!autoPrSettings.included_repos.includes(selectedRepo)) {
      setAutoPrSettings({
        ...autoPrSettings,
        included_repos: [...autoPrSettings.included_repos, selectedRepo]
      });
    }
  };
  
  const removeRepoFromAutoPR = (repo) => {
    setAutoPrSettings({
      ...autoPrSettings,
      included_repos: autoPrSettings.included_repos.filter(r => r !== repo)
    });
  };
  
  const handleNotificationToggle = (eventType) => {
    setNotificationSettings({
      ...notificationSettings,
      settings: {
        ...notificationSettings.settings,
        [eventType]: !notificationSettings.settings[eventType]
      }
    });
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">GitHub Integration Settings</h1>
      
      {statusMessage && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {statusMessage}
        </div>
      )}
      
      {errorMessage && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {errorMessage}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Notification Settings */}
        <div className="bg-white rounded shadow p-4">
          <h2 className="text-xl font-bold mb-4">Windows Notifications</h2>
          
          <div className="mb-4">
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                className="form-checkbox"
                checked={notificationSettings.enabled}
                onChange={() => setNotificationSettings({
                  ...notificationSettings,
                  enabled: !notificationSettings.enabled
                })}
              />
              <span className="ml-2">Enable notifications</span>
            </label>
          </div>
          
          <div className="mb-4">
            <h3 className="font-medium mb-2">Notification Events:</h3>
            {Object.entries(notificationSettings.settings).map(([eventType, enabled]) => (
              <div key={eventType} className="mb-2">
                <label className="inline-flex items-center">
                  <input
                    type="checkbox"
                    className="form-checkbox"
                    checked={enabled}
                    onChange={() => handleNotificationToggle(eventType)}
                  />
                  <span className="ml-2">{eventType}</span>
                </label>
              </div>
            ))}
          </div>
          
          <div className="mb-4">
            <p className="text-sm">
              Platform: {notificationSettings.status.platform || 'Unknown'}
              {!notificationSettings.status.enabled && (
                <span className="text-red-600 ml-2">
                  (Notifications not supported on this platform)
                </span>
              )}
            </p>
          </div>
          
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            onClick={saveNotificationSettings}
          >
            Save Notification Settings
          </button>
        </div>
        
        {/* Auto PR Settings */}
        <div className="bg-white rounded shadow p-4">
          <h2 className="text-xl font-bold mb-4">Auto Branch-to-PR</h2>
          
          <div className="mb-4">
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                className="form-checkbox"
                checked={autoPrSettings.enabled}
                onChange={() => setAutoPrSettings({
                  ...autoPrSettings,
                  enabled: !autoPrSettings.enabled
                })}
              />
              <span className="ml-2">Auto-create PRs for new branches</span>
            </label>
          </div>
          
          <div className="mb-4">
            <label className="block mb-2">PR Title Template:</label>
            <input
              type="text"
              className="w-full p-2 border rounded"
              value={autoPrSettings.title_template}
              onChange={(e) => setAutoPrSettings({
                ...autoPrSettings,
                title_template: e.target.value
              })}
            />
            <p className="text-sm text-gray-500">
              Use {'{branch_name}'} and {'{repo_name}'} as placeholders
            </p>
          </div>
          
          <div className="mb-4">
            <label className="block mb-2">PR Body Template:</label>
            <textarea
              className="w-full p-2 border rounded"
              rows="3"
              value={autoPrSettings.body_template}
              onChange={(e) => setAutoPrSettings({
                ...autoPrSettings,
                body_template: e.target.value
              })}
            ></textarea>
          </div>
          
          <div className="mb-4">
            <label className="block mb-2">Base Branch:</label>
            <input
              type="text"
              className="w-full p-2 border rounded"
              value={autoPrSettings.base_branch}
              onChange={(e) => setAutoPrSettings({
                ...autoPrSettings,
                base_branch: e.target.value
              })}
            />
          </div>
          
          <div className="mb-4">
            <h3 className="font-medium mb-2">Included Repositories:</h3>
            <div className="flex mb-2">
              <select
                className="flex-grow p-2 border rounded mr-2"
                value={selectedRepo}
                onChange={(e) => setSelectedRepo(e.target.value)}
              >
                <option value="">Select a repository</option>
                {repositories.map((repo) => (
                  <option key={repo.id} value={repo.full_name}>
                    {repo.full_name}
                  </option>
                ))}
              </select>
              <button
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                onClick={addRepoToAutoPR}
              >
                Add
              </button>
            </div>
            
            <ul className="border rounded p-2 max-h-32 overflow-y-auto">
              {autoPrSettings.included_repos.length === 0 ? (
                <li className="text-gray-500">No repositories added (will monitor all)</li>
              ) : (
                autoPrSettings.included_repos.map((repo) => (
                  <li key={repo} className="flex justify-between items-center py-1">
                    <span>{repo}</span>
                    <button
                      className="text-red-500 hover:text-red-700"
                      onClick={() => removeRepoFromAutoPR(repo)}
                    >
                      ✕
                    </button>
                  </li>
                ))
              )}
            </ul>
          </div>
          
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            onClick={saveAutoPrSettings}
          >
            Save Auto PR Settings
          </button>
        </div>
        
        {/* Post-Merge Scripts */}
        <div className="bg-white rounded shadow p-4 md:col-span-2">
          <h2 className="text-xl font-bold mb-4">Post-Merge Scripts</h2>
          
          <div className="mb-6">
            <h3 className="font-medium mb-3">Add New Script:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block mb-1">Project Name:</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded"
                  value={newScript.project_name}
                  onChange={(e) => setNewScript({
                    ...newScript,
                    project_name: e.target.value
                  })}
                />
              </div>
              
              <div>
                <label className="block mb-1">Script Path:</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded"
                  value={newScript.script_path}
                  onChange={(e) => setNewScript({
                    ...newScript,
                    script_path: e.target.value
                  })}
                  placeholder="C:\scripts\deploy.bat or /scripts/build.py"
                />
              </div>
              
              <div>
                <label className="block mb-1">Repository Patterns (comma-separated):</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded"
                  value={newScript.repo_patterns}
                  onChange={(e) => setNewScript({
                    ...newScript,
                    repo_patterns: e.target.value
                  })}
                  placeholder="myorg/repo, project-name"
                />
              </div>
              
              <div className="flex items-end">
                <button
                  className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                  onClick={addPostMergeScript}
                >
                  Add Script
                </button>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="font-medium mb-3">Configured Scripts:</h3>
            <table className="min-w-full bg-white">
              <thead>
                <tr>
                  <th className="py-2 px-4 border-b border-gray-200 text-left">Project</th>
                  <th className="py-2 px-4 border-b border-gray-200 text-left">Script Path</th>
                  <th className="py-2 px-4 border-b border-gray-200 text-left">Repo Patterns</th>
                  <th className="py-2 px-4 border-b border-gray-200 text-center">Status</th>
                  <th className="py-2 px-4 border-b border-gray-200 text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {postMergeScripts.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="py-4 text-center text-gray-500">
                      No scripts configured
                    </td>
                  </tr>
                ) : (
                  postMergeScripts.map((script) => (
                    <tr key={script.project_name}>
                      <td className="py-2 px-4 border-b border-gray-200">{script.project_name}</td>
                      <td className="py-2 px-4 border-b border-gray-200">{script.script_path}</td>
                      <td className="py-2 px-4 border-b border-gray-200">
                        {script.repo_patterns.join(", ") || "All repositories"}
                      </td>
                      <td className="py-2 px-4 border-b border-gray-200 text-center">
                        <span className={`inline-block px-2 py-1 rounded text-xs ${
                          script.enabled 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {script.enabled ? 'Enabled' : 'Disabled'}
                        </span>
                      </td>
                      <td className="py-2 px-4 border-b border-gray-200 text-center">
                        <button
                          className={`mr-2 ${
                            script.enabled 
                              ? 'text-yellow-500 hover:text-yellow-700' 
                              : 'text-green-500 hover:text-green-700'
                          }`}
                          onClick={() => togglePostMergeScript(script.project_name, script.enabled)}
                        >
                          {script.enabled ? 'Disable' : 'Enable'}
                        </button>
                        <button
                          className="text-red-500 hover:text-red-700"
                          onClick={() => removePostMergeScript(script.project_name)}
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;