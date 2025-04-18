import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const RepositoryList = ({ onSelectRepo }) => {
  const [repositories, setRepositories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRepoId, setSelectedRepoId] = useState(null);

  useEffect(() => {
    fetchRepositories();
  }, []);

  const fetchRepositories = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/repos`);
      setRepositories(response.data);
      
      // Select the first repository by default if available
      if (response.data.length > 0 && !selectedRepoId) {
        handleSelectRepo(response.data[0]);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching repositories:', err);
      setError('Failed to load repositories. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRepo = (repo) => {
    setSelectedRepoId(repo.id);
    onSelectRepo(repo);
  };

  if (loading && repositories.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Repositories</h2>
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Repositories</h2>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Repositories</h2>
        <button
          onClick={fetchRepositories}
          className="text-blue-500 hover:text-blue-700"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
          </svg>
        </button>
      </div>

      {repositories.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No repositories found. Add repositories to see them here.
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {repositories.map((repo) => (
            <div
              key={repo.id}
              className={`py-3 px-2 cursor-pointer hover:bg-gray-50 ${
                selectedRepoId === repo.id ? 'bg-blue-50' : ''
              }`}
              onClick={() => handleSelectRepo(repo)}
            >
              <div className="flex items-center">
                <svg className="w-5 h-5 text-gray-500 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                </svg>
                <div>
                  <div className="font-medium">{repo.name}</div>
                  <div className="text-xs text-gray-500">{repo.full_name}</div>
                </div>
                {repo.private && (
                  <span className="ml-auto bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                    Private
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RepositoryList;
