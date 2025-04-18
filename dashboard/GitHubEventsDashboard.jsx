import React, { useState, useEffect } from 'react';
import axios from 'axios';

 Import our components
import RecentEvents from '.RecentEvents';
import RepositoryList from '.RepositoryList';
import RepositoryPRs from '.RepositoryPRs';
import SettingsPanel from '.SettingsPanel';
import ConfigurationPanel from '.ConfigurationPanel';

 API URL - configure this to match your API service
const API_BASE_URL = process.env.REACT_APP_API_URL  'httplocalhost8001api';

 Main Dashboard component
const GitHubEventsDashboard = () = {
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [activeTab, setActiveTab] = useState('events');
  const [systemStatus, setSystemStatus] = useState({
    notifications { enabled false },
    auto_pr { enabled false, running false },
    post_merge_scripts { enabled false }
  });

   Fetch system status on load
  useEffect(() = {
    fetchSystemStatus();
  }, []);

  const fetchSystemStatus = async () = {
    try {
      const response = await axios.get(`${API_BASE_URL}settingsstatus`);
      setSystemStatus(response.data);
    } catch (error) {
      console.error('Error fetching system status', error);
    }
  };

   Render status indicators
  const renderStatusIndicators = () = {
    return (
      div className=flex space-x-4 mb-4
        div className={`flex items-center px-3 py-1 rounded-full text-xs font-medium ${
          systemStatus.notifications.enabled  'bg-green-100 text-green-800'  'bg-gray-100 text-gray-800'
        }`}
          span className={`w-2 h-2 mr-1 rounded-full ${
            systemStatus.notifications.enabled  'bg-green-500'  'bg-gray-500'
          }`}span
          Notifications
        div
        
        div className={`flex items-center px-3 py-1 rounded-full text-xs font-medium ${
          systemStatus.auto_pr.enabled  'bg-green-100 text-green-800'  'bg-gray-100 text-gray-800'
        }`}
          span className={`w-2 h-2 mr-1 rounded-full ${
            systemStatus.auto_pr.enabled  'bg-green-500'  'bg-gray-500'
          }`}span
          Auto PR
        div
        
        div className={`flex items-center px-3 py-1 rounded-full text-xs font-medium ${
          systemStatus.post_merge_scripts.enabled  'bg-green-100 text-green-800'  'bg-gray-100 text-gray-800'
        }`}
          span className={`w-2 h-2 mr-1 rounded-full ${
            systemStatus.post_merge_scripts.enabled  'bg-green-500'  'bg-gray-500'
          }`}span
          Post-merge Scripts
        div
      div
    );
  };

  return (
    div className=container mx-auto p-4
      div className=flex justify-between items-center mb-6
        h1 className=text-2xl font-boldGitHub Events Dashboardh1
        {renderStatusIndicators()}
      div
      
      div className=mb-4
        div className=border-b border-gray-200
          nav className=flex -mb-px
            button
              onClick={() = setActiveTab('events')}
              className={`py-2 px-4 text-center border-b-2 font-medium text-sm ${
                activeTab === 'events'
                   'border-blue-500 text-blue-600'
                   'border-transparent text-gray-500 hovertext-gray-700 hoverborder-gray-300'
              }`}
            
              Recent Events
            button
            button
              onClick={() = setActiveTab('repos')}
              className={`ml-8 py-2 px-4 text-center border-b-2 font-medium text-sm ${
                activeTab === 'repos'
                   'border-blue-500 text-blue-600'
                   'border-transparent text-gray-500 hovertext-gray-700 hoverborder-gray-300'
              }`}
            
              Repositories
            button
            button
              onClick={() = setActiveTab('settings')}
              className={`ml-8 py-2 px-4 text-center border-b-2 font-medium text-sm ${
                activeTab === 'settings'
                   'border-blue-500 text-blue-600'
                   'border-transparent text-gray-500 hovertext-gray-700 hoverborder-gray-300'
              }`}
            
              Settings
            button
            button
              onClick={() = setActiveTab('config')}
              className={`ml-8 py-2 px-4 text-center border-b-2 font-medium text-sm ${
                activeTab === 'config'
                   'border-blue-500 text-blue-600'
                   'border-transparent text-gray-500 hovertext-gray-700 hoverborder-gray-300'
              }`}
            
              Configuration
            button
          nav
        div
      div
      
      {activeTab === 'events' && (
        div className=grid grid-cols-1 gap-6
          RecentEvents 
        div
      )}
      
      {activeTab === 'repos' && (
        div className=grid grid-cols-1 lggrid-cols-3 gap-6
          div className=lgcol-span-1
            RepositoryList onSelectRepo={setSelectedRepo} 
          div
          div className=lgcol-span-2
            RepositoryPRs repoId={selectedRepo.id} 
          div
        div
      )}
      
      {activeTab === 'settings' && (
        div className=grid grid-cols-1 gap-6
          SettingsPanel onSettingsChanged={fetchSystemStatus} 
        div
      )}
      
      {activeTab === 'config' && (
        div className=grid grid-cols-1 gap-6
          ConfigurationPanel 
        div
      )}
    div
  );
};

export default GitHubEventsDashboard;