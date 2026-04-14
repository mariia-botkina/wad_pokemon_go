import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

// Fix default Leaflet marker icon paths broken by Webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom icon for the player's current position
const playerIcon = new L.Icon({
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
  className: 'player-marker',
});

// Default map center (used before geolocation is available)
const DEFAULT_CENTER = [51.505, -0.09];
const DEFAULT_ZOOM = 15;

/**
 * Inner component that re-centers the map whenever the position prop changes.
 */
function RecenterMap({ position }) {
  const map = useMap();
  useEffect(() => {
    if (position) {
      map.setView(position, map.getZoom());
    }
  }, [position, map]);
  return null;
}

/**
 * MapView – displays an interactive Leaflet map centred on the user's
 * real-time GPS position.  Requests geolocation permission and updates
 * the map as the device moves.
 *
 * TODO: Overlay nearby creature spawns as additional markers.
 * TODO: Show creature-capture radius circle around the player.
 * TODO: Add player avatar / custom player icon based on user profile.
 * TODO: Integrate with backend spawn API to fetch live creature positions.
 * TODO: Add collection view accessible from this screen.
 * TODO: Show catch animation when the user taps a nearby creature.
 */
function MapView() {
  const [position, setPosition] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [permissionState, setPermissionState] = useState('prompt'); // 'prompt' | 'granted' | 'denied'
  const watchIdRef = useRef(null);

  /**
   * Start watching the device's geolocation.  Called once permission is
   * explicitly granted (via button) or automatically if permission was
   * already granted on a previous visit.
   */
  const startWatchingLocation = () => {
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your browser.');
      return;
    }

    setLocationError(null);

    watchIdRef.current = navigator.geolocation.watchPosition(
      (geo) => {
        setPosition([geo.coords.latitude, geo.coords.longitude]);
        setPermissionState('granted');
      },
      (err) => {
        if (err.code === err.PERMISSION_DENIED) {
          setPermissionState('denied');
          setLocationError('Location access was denied. Please allow location access in your browser settings.');
        } else {
          setLocationError(`Unable to retrieve your location: ${err.message}`);
        }
      },
      { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
    );
  };

  // On mount, check if permission was already granted so we can start tracking
  // immediately without requiring a button tap.
  useEffect(() => {
    if (navigator.permissions) {
      navigator.permissions.query({ name: 'geolocation' }).then((result) => {
        setPermissionState(result.state);
        if (result.state === 'granted') {
          startWatchingLocation();
        }
        result.onchange = () => {
          setPermissionState(result.state);
          if (result.state === 'granted') {
            startWatchingLocation();
          }
        };
      });
    }

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const mapCenter = position || DEFAULT_CENTER;

  return (
    <div className="map-wrapper">
      {/* Geolocation permission / error banner */}
      {permissionState !== 'granted' && (
        <div className="location-banner">
          {permissionState === 'denied' ? (
            <p className="location-error">
              {locationError || 'Location access denied. Enable it in browser settings to play.'}
            </p>
          ) : (
            <>
              <p>Allow location access to see your position on the map.</p>
              <button className="location-btn" onClick={startWatchingLocation}>
                📍 Enable My Location
              </button>
            </>
          )}
        </div>
      )}

      {locationError && permissionState === 'granted' && (
        <div className="location-banner">
          <p className="location-error">{locationError}</p>
        </div>
      )}

      <MapContainer
        center={mapCenter}
        zoom={DEFAULT_ZOOM}
        className="leaflet-map"
        zoomControl={true}
      >
        {/* OpenStreetMap tile layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Re-center the map whenever position updates */}
        <RecenterMap position={position} />

        {/* Player location marker */}
        {position && (
          <Marker position={position} icon={playerIcon}>
            <Popup>You are here!</Popup>
          </Marker>
        )}

        {/*
         * TODO: Render creature spawn markers here.
         * Example:
         * spawns.map(spawn => (
         *   <Marker key={spawn.id} position={[spawn.lat, spawn.lng]} icon={creatureIcon}>
         *     <Popup>{spawn.name}</Popup>
         *   </Marker>
         * ))
         */}
      </MapContainer>
    </div>
  );
}

export default MapView;
