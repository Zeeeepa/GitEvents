import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const DatabaseManagement = () => {
  const [dbInfo, setDbInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [showDbInfo, setShowDbInfo] = useState(false);
  
  // SQLite form state
  const [sqliteConfig, setSqliteConfig] = useState({
    type: 'sqlite',
    path: 'github_events.db',
    create_new: false
  });
  
  // MySQL form state
  const [mysqlConfig, setMysqlConfig] = useState({
    type: 'mysql',
    host: 'localhost',
    port: '3306',
    name: 'github_events',
    user: 'root',
    password: ''
  });
  
  // Test connection state
  const [testingConnection, setTestingConnection] = useState(false);
  const [testResult, setTestResult] = useState(null);
  
  useEffect(() => {
    fetchDatabaseInfo();
  }, []);
  
  const fetchDatabaseInfo = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/database/info`);
      setDbInfo(response.data);
      
      // Update form values based on current config
      if (response.data.type === 'sqlite') {
        setSqliteConfig({
          ...sqliteConfig,
          path: response.data.path || 'github_events.db'
        });
      } else if (response.data.type === 'mysql') {
        setMysqlConfig({
          ...mysqlConfig,
          host: response.data.host || 'localhost',
          port: response.data.port || '3306',
          name: response.data.name || 'github_events',
          user: response.data.user || 'root'
        });
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching database info:', err);
      setError('Failed to load database information. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleSqliteChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSqliteConfig({
      ...sqliteConfig,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  const handleMysqlChange = (e) => {
    const { name, value } = e.target;
    setMysqlConfig({
      ...mysqlConfig,
      [name]: value
    });
  };
  
  const testConnection = async (config) => {
    try {
      setTestingConnection(true);
      setTestResult(null);
      
      const response = await axios.post(`${API_BASE_URL}/database/test-connection`, config);
      setTestResult(response.data);
    } catch (err) {
      console.error('Error testing connection:', err);
      setTestResult({
        success: false,
        message: err.response?.data?.detail || 'Failed to test connection. Please try again.'
      });
    } finally {
      setTestingConnection(false);
    }
  };
  
  const updateDatabaseConfig = async (config) => {
    try {
      setLoading(true);
      setSuccessMessage(null);
      setError(null);
      
      const response = await axios.post(`${API_BASE_URL}/database/update-config`, config);
      
      if (response.data.success) {
        setSuccessMessage(response.data.message);
        await fetchDatabaseInfo();
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      console.error('Error updating database config:', err);
      setError(err.response?.data?.detail || 'Failed to update database configuration. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const createSqliteDatabase = async () => {
    try {
      setLoading(true);
      setSuccessMessage(null);
      setError(null);
      
      const response = await axios.post(`${API_BASE_URL}/database/create-sqlite?db_path=${encodeURIComponent(sqliteConfig.path)}`);
      
      if (response.data.success) {
        setSuccessMessage(response.data.message);
        await fetchDatabaseInfo();
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      console.error('Error creating SQLite database:', err);
      setError(err.response?.data?.detail || 'Failed to create SQLite database. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  if (loading && !dbInfo) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Database Management</h2>
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-6">Database Management</h2>
      
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
      
      {/* Current Database Information */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-medium">Database Information</h3>
          <button
            onClick={() => setShowDbInfo(!showDbInfo)}
            className="text-indigo-600 hover:text-indigo-800"
          >
            {showDbInfo ? 'Hide Details' : 'Show Details'}
          </button>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-md">
          <div className="flex items-center justify-between mb-2">
            <div>
              <span className="font-medium">Type:</span> {dbInfo?.type.toUpperCase()}
            </div>
            <div>
              <span className="font-medium">Status:</span>{' '}
              <span className={`px-2 py-1 rounded text-xs ${dbInfo?.connection_status === 'connected' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {dbInfo?.connection_status}
              </span>
            </div>
          </div>
          
          {dbInfo?.type === 'sqlite' && (
            <div className="mb-2">
              <span className="font-medium">Path:</span> {dbInfo.path}
            </div>
          )}
          
          {dbInfo?.type === 'mysql' && (
            <>
              <div className="mb-2">
                <span className="font-medium">Host:</span> {dbInfo.host}:{dbInfo.port}
              </div>
              <div className="mb-2">
                <span className="font-medium">Database:</span> {dbInfo.name}
              </div>
              <div className="mb-2">
                <span className="font-medium">User:</span> {dbInfo.user}
              </div>
            </>
          )}
          
          {showDbInfo && dbInfo?.tables && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Tables</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Columns</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rows</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {dbInfo.tables.map((table, index) => (
                      <tr key={index}>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">{table.name}</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">{table.columns}</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">{table.rows !== null ? table.rows : 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* SQLite Configuration */}
      <div className="mb-6 border-t pt-6">
        <h3 className="text-lg font-medium mb-4">SQLite Database Configuration</h3>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="sqlite-path" className="block text-sm font-medium text-gray-700">
              Database Path
            </label>
            <input
              type="text"
              id="sqlite-path"
              name="path"
              value={sqliteConfig.path}
              onChange={handleSqliteChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Path to SQLite database file"
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="create-new-sqlite"
              name="create_new"
              checked={sqliteConfig.create_new}
              onChange={handleSqliteChange}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label htmlFor="create-new-sqlite" className="ml-2 block text-sm text-gray-700">
              Create New SQLite DB
            </label>
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={() => testConnection(sqliteConfig)}
              disabled={testingConnection}
              className={`px-4 py-2 rounded-md text-white font-medium ${
                testingConnection ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
              }`}
            >
              {testingConnection ? 'Testing...' : 'Test Connection'}
            </button>
            
            <button
              onClick={() => updateDatabaseConfig(sqliteConfig)}
              disabled={loading}
              className={`px-4 py-2 rounded-md text-white font-medium ${
                loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {loading ? 'Updating...' : 'Update Configuration'}
            </button>
            
            {sqliteConfig.create_new && (
              <button
                onClick={createSqliteDatabase}
                disabled={loading}
                className={`px-4 py-2 rounded-md text-white font-medium ${
                  loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {loading ? 'Creating...' : 'Create Database'}
              </button>
            )}
          </div>
        </div>
      </div>
      
      {/* MySQL Configuration */}
      <div className="mb-6 border-t pt-6">
        <h3 className="text-lg font-medium mb-4">MySQL Database Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="mysql-host" className="block text-sm font-medium text-gray-700">
              Host
            </label>
            <input
              type="text"
              id="mysql-host"
              name="host"
              value={mysqlConfig.host}
              onChange={handleMysqlChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Database host"
            />
          </div>
          
          <div>
            <label htmlFor="mysql-port" className="block text-sm font-medium text-gray-700">
              Port
            </label>
            <input
              type="text"
              id="mysql-port"
              name="port"
              value={mysqlConfig.port}
              onChange={handleMysqlChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Database port"
            />
          </div>
          
          <div>
            <label htmlFor="mysql-name" className="block text-sm font-medium text-gray-700">
              Database Name
            </label>
            <input
              type="text"
              id="mysql-name"
              name="name"
              value={mysqlConfig.name}
              onChange={handleMysqlChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Database name"
            />
          </div>
          
          <div>
            <label htmlFor="mysql-user" className="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              type="text"
              id="mysql-user"
              name="user"
              value={mysqlConfig.user}
              onChange={handleMysqlChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Database username"
            />
          </div>
          
          <div>
            <label htmlFor="mysql-password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              id="mysql-password"
              name="password"
              value={mysqlConfig.password}
              onChange={handleMysqlChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Database password"
            />
          </div>
        </div>
        
        <div className="mt-4 flex space-x-4">
          <button
            onClick={() => testConnection(mysqlConfig)}
            disabled={testingConnection}
            className={`px-4 py-2 rounded-md text-white font-medium ${
              testingConnection ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
            }`}
          >
            {testingConnection ? 'Testing...' : 'Test Connection'}
          </button>
          
          <button
            onClick={() => updateDatabaseConfig(mysqlConfig)}
            disabled={loading}
            className={`px-4 py-2 rounded-md text-white font-medium ${
              loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {loading ? 'Updating...' : 'Update Configuration'}
          </button>
        </div>
      </div>
      
      {/* Test Connection Result */}
      {testResult && (
        <div className={`mt-4 p-4 rounded-md ${testResult.success ? 'bg-green-50 border border-green-200 text-green-700' : 'bg-red-50 border border-red-200 text-red-700'}`}>
          <div className="flex">
            <div className="flex-shrink-0">
              {testResult.success ? (
                <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium">
                {testResult.message}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatabaseManagement;
