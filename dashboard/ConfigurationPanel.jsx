import React, { useState, useEffect } from 'react';
import axios from 'axios';

// API URL - configure this to match your API service
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const ConfigurationPanel = () => {
  // Token configuration
  const [config, setConfig] = useState({
    github_token: '',
    ngrok_token: '',
    github_token_set: false,
    ngrok_token_set: false
  });
  
  // Validation results
  const [validation, setValidation] = useState({
    github_token: { valid: false, message: '' },
    ngrok_token: { valid: false, message: '' }
  });
  
  // Loading and status states
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  
  // Fetch current configuration
  useEffect(() => {
    fetchConfig();
  }, []);
  
  const fetchConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/config`);
      
      setConfig({
        ...config,
        github_token_set: response.data.github_token_set,
        ngrok_token_set: response.data.ngrok_token_set,
        api_port: response.data.api_port,
        webhook_port: response.data.webhook_port,
        db_path: response.data.db_path
      });
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching configuration:', error);
      setErrorMessage('Failed to load configuration');
      setLoading(false);
    }
  };
  
  const validateTokens = async () => {
    try {
      setValidating(true);
      const response = await axios.get(`${API_BASE_URL}/system/validate-tokens`);
      setValidation(response.data);
      setValidating(false);
    } catch (error) {
      console.error('Error validating tokens:', error);
      setErrorMessage('Failed to validate tokens');
      setValidating(false);
    }
  };
  
  const saveConfig = async () => {
    try {
      setLoading(true);
      
      // Only send tokens if they are not empty
      const configToSave = {};
      if (config.github_token) configToSave.github_token = config.github_token;
      if (config.ngrok_token) configToSave.ngrok_token = config.ngrok_token;
      
      const response = await axios.post(`${API_BASE_URL}/config`, configToSave);
      
      if (response.data.restart_required) {
        setStatusMessage('Configuration updated successfully. Services need to be restarted.');
      } else {
        setStatusMessage('Configuration updated successfully.');
      }
      
      // Refresh the config state
      await fetchConfig();
      
      // Clear input fields after save
      setConfig({
        ...config,
        github_token: '',
        ngrok_token: ''
      });
      
      setLoading(false);
      setTimeout(() => setStatusMessage(''), 5000);
    } catch (error) {
      console.error('Error saving configuration:', error);
      setErrorMessage('Failed to save configuration');
      setLoading(false);
      setTimeout(() => setErrorMessage(''), 5000);
    }
  };
  
  return (
    <div className="bg-white rounded shadow p-6">
      <h2 className="text-xl font-bold mb-6">System Configuration</h2>
      
      {loading && <div className="text-center my-4">Loading...</div>}
      
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
      
      <div className="space-y-6">
        {/* GitHub Token */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            GitHub Token
          </label>
          
          <div className="mb-2">
            <input
              type="password"
              className="w-full p-2 border rounded"
              placeholder={config.github_token_set ? "Token already set (enter to change)" : "Enter your GitHub token"}
              value={config.github_token}
              onChange={(e) => setConfig({ ...config, github_token: e.target.value })}
            />
          </div>
          
          <div className="text-sm">
            {config.github_token_set ? (
              <span className="text-green-600">✓ GitHub token is configured</span>
            ) : (
              <span className="text-yellow-600">⚠ GitHub token is not configured</span>
            )}
            
            {validation.github_token && validation.github_token.valid !== undefined && (
              <div className={`mt-1 ${validation.github_token.valid ? 'text-green-600' : 'text-red-600'}`}>
                {validation.github_token.message}
              </div>
            )}
          </div>
        </div>
        
        {/* Ngrok Token */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Ngrok Token
          </label>
          
          <div className="mb-2">
            <input
              type="password"
              className="w-full p-2 border rounded"
              placeholder={config.ngrok_token_set ? "Token already set (enter to change)" : "Enter your Ngrok token"}
              value={config.ngrok_token}
              onChange={(e) => setConfig({ ...config, ngrok_token: e.target.value })}
            />
          </div>
          
          <div className="text-sm">
            {config.ngrok_token_set ? (
              <span className="text-green-600">✓ Ngrok token is configured</span>
            ) : (
              <span className="text-yellow-600">⚠ Ngrok token is not configured</span>
            )}
            
            {validation.ngrok_token && validation.ngrok_token.valid !== undefined && (
              <div className={`mt-1 ${validation.ngrok_token.valid ? 'text-green-600' : 'text-red-600'}`}>
                {validation.ngrok_token.message}
              </div>
            )}
          </div>
        </div>
        
        {/* System Information */}
        <div className="border-t pt-4">
          <h3 className="font-medium mb-2">System Information</h3>
          
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>API Port:</div>
            <div>{config.api_port}</div>
            
            <div>Webhook Port:</div>
            <div>{config.webhook_port}</div>
            
            <div>Database Path:</div>
            <div className="truncate">{config.db_path}</div>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="flex justify-between pt-4">
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            onClick={saveConfig}
            disabled={loading || (!config.github_token && !config.ngrok_token)}
          >
            {loading ? 'Saving...' : 'Save Configuration'}
          </button>
          
          <button
            className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
            onClick={validateTokens}
            disabled={validating}
          >
            {validating ? 'Validating...' : 'Validate Tokens'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfigurationPanel;