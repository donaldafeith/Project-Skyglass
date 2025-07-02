import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [status, setStatus] = useState('Connecting...');
  const [dataLayers, setDataLayers] = useState({ earthquakes_usgs: null, wildfires_firms: null });

  useEffect(() => {
    const fetchStatus = () => {
      fetch('http://127.0.0.1:5555/api/status')
        .then(res => (res.ok ? res.json() : Promise.reject(res)))
        .then(data => setStatus(data.message))
        .catch(() => setStatus('Connection FAILED. Is the backend running?'));
    };

    const fetchDataForSource = (source) => {
      fetch(`http://127.0.0.1:5555/api/latest/${source}`)
        .then(res => (res.ok ? res.json() : res.json().then(err => Promise.reject(err))))
        .then(data => setDataLayers(prev => ({ ...prev, [source]: data })))
        .catch(err => setDataLayers(prev => ({ ...prev, [source]: { error: err.error || 'Fetch failed' } })));
    };

    fetchStatus();
    const sources = ['earthquakes_usgs', 'wildfires_firms'];
    sources.forEach(fetchDataForSource);
    const interval = setInterval(() => sources.forEach(fetchDataForSource), 300000); // 5 min refresh
    return () => clearInterval(interval);
  }, []);

  const renderFeatureCount = (data) => {
    if (!data) return 'Fetching...';
    if (data.error) return 'ERROR';
    if (data.features) return `${data.features.length} active`;
    return 'No data';
  };

  return (
    <div className="container">
      <div className="sidebar">
        <h1>Skyglass Console</h1>
        <div className="status-box">Backend Status: {status}</div>
        <div className="layer-nav">
          <h2>Real-Time Layers</h2>
          <div className="layer-item">
            <span>USGS Earthquakes (2.5+)</span>
            <span className="data-count">{renderFeatureCount(dataLayers.earthquakes_usgs)}</span>
          </div>
          <div className="layer-item">
            <span>FIRMS Wildfires</span>
            <span className="data-count">{renderFeatureCount(dataLayers.wildfires_firms)}</span>
          </div>
        </div>
      </div>
      <div className="main-content">
        <div className="map-placeholder">
          <h2>Operational Map</h2>
          <p>
            This area will contain the main interactive map (e.g., Leaflet.js).
            <br />Live data is being fetched from the local backend and displayed in the sidebar.
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
