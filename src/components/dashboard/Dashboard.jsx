import React, { useState } from 'react';
import StatusIndicator from './StatusIndicator';
import RepositoryList from './RepositoryList';
import ConfigurationPanel from './ConfigurationPanel';
import DatabaseManagement from './DatabaseManagement';

const Dashboard = () => {
  const [selectedRepo, setSelectedRepo] = useState(null);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">GitEvents Dashboard</h1>
      
      <StatusIndicator />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <RepositoryList onSelectRepo={setSelectedRepo} />
        </div>
        
        <div className="lg:col-span-2">
          <div className="space-y-6">
            <ConfigurationPanel />
            <DatabaseManagement />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
