import React from 'react';
import MapView from './components/MapView';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>PokéWorld</h1>
      </header>
      <main>
        {/* Main map view with geolocation */}
        <MapView />
        {/* TODO: Add routing (react-router) for /collection, /login, /profile pages */}
        {/* TODO: Add authentication context and protected routes */}
        {/* TODO: Add creature spawn overlay on the map */}
      </main>
    </div>
  );
}

export default App;
