import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import GitHubEventsDashboard from './components/dashboard/GitHubEventsDashboard';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <GitHubEventsDashboard />
  </React.StrictMode>
);
