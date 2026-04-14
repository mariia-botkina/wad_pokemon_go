/**
 * MapView.js – Interactive map component with creature markers.
 *
 * Responsibilities:
 *   1. Request the user's GPS location via the browser Geolocation API.
 *   2. Display an interactive Leaflet map centred on the user's position.
 *   3. Show a pulsing "you are here" marker for the user.
 *   4. Periodically fetch nearby creatures from the backend API.
 *   5. Render a marker for each nearby creature with a popup showing its
 *      name, type, and a placeholder "Catch!" button.
 *
 * TODO: Implement the catch action (POST /creatures/{id}/catch) with
 *       proximity validation once that endpoint is available.
 * TODO: Replace polling with a WebSocket connection for real-time updates.
 * TODO: Show different marker icons per creature type (fire, water, etc.).
 * TODO: Display a loading spinner while the first location fix is obtained.
 */

import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  Circle,
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import { fetchNearbyCreatures, spawnCreatures } from "../api/creatures";

// ---------------------------------------------------------------------------
// Fix Leaflet's default icon paths when bundled by Create React App.
// https://github.com/Leaflet/Leaflet/issues/4968
// ---------------------------------------------------------------------------
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

/** Custom red marker icon used for the player's location. */
const playerIcon = new L.Icon({
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  className: "player-marker",
});

// How often (ms) to re-fetch nearby creatures.
const FETCH_INTERVAL_MS = 15_000;

// ---------------------------------------------------------------------------
// Inner component: keeps the map centred on the user's location.
// ---------------------------------------------------------------------------
function MapCenterer({ position }) {
  const map = useMap();
  useEffect(() => {
    if (position) {
      map.setView(position, map.getZoom());
    }
  }, [map, position]);
  return null;
}

// ---------------------------------------------------------------------------
// Main MapView component
// ---------------------------------------------------------------------------
/**
 * MapView renders a full-screen interactive map.
 *
 * @param {object}   props
 * @param {number}   [props.radiusKm=0.5]  - Creature search radius in km
 * @param {Function} [props.onError]       - Optional error callback
 */
export default function MapView({ radiusKm = 0.5, onError }) {
  const [userPos, setUserPos] = useState(null);          // [lat, lon]
  const [creatures, setCreatures] = useState([]);
  const [locationError, setLocationError] = useState(null);
  const [loading, setLoading] = useState(true);
  const watchIdRef = useRef(null);
  const fetchTimerRef = useRef(null);

  // ------------------------------------------------------------------
  // Geolocation: watch position continuously while the map is mounted.
  // ------------------------------------------------------------------
  useEffect(() => {
    if (!navigator.geolocation) {
      const msg = "Geolocation is not supported by your browser.";
      setLocationError(msg);
      setLoading(false);
      onError && onError(msg);
      return;
    }

    watchIdRef.current = navigator.geolocation.watchPosition(
      (position) => {
        setUserPos([position.coords.latitude, position.coords.longitude]);
        setLoading(false);
        setLocationError(null);
      },
      (err) => {
        const msg = `Location error: ${err.message}`;
        setLocationError(msg);
        setLoading(false);
        onError && onError(msg);
      },
      { enableHighAccuracy: true, maximumAge: 5000 }
    );

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, [onError]);

  // ------------------------------------------------------------------
  // Periodic creature fetch when the user position is known.
  // ------------------------------------------------------------------
  const loadCreatures = useCallback(async () => {
    if (!userPos) return;
    try {
      const data = await fetchNearbyCreatures(userPos[0], userPos[1], radiusKm);
      setCreatures(data);
    } catch (err) {
      console.error("Failed to load creatures:", err);
    }
  }, [userPos, radiusKm]);

  useEffect(() => {
    loadCreatures(); // immediate fetch on location change
    fetchTimerRef.current = setInterval(loadCreatures, FETCH_INTERVAL_MS);
    return () => clearInterval(fetchTimerRef.current);
  }, [loadCreatures]);


  // ------------------------------------------------------------------
  // TODO: Implement catch action
  // ------------------------------------------------------------------
  const handleCatch = (creature) => {
    // TODO: Call POST /creatures/{creature.id}/catch
    // TODO: Check proximity (distance < 30 m) before allowing the catch.
    // TODO: Update creature list / show catch animation on success.
    alert(`Catch functionality coming soon! (${creature.name})`);
  };

  // ------------------------------------------------------------------
  // Spawn creatures near the user (for debug/demo)
  // ------------------------------------------------------------------
  const [spawning, setSpawning] = useState(false);
  const handleSpawn = async () => {
    if (!userPos) return;
    setSpawning(true);
    try {
      await spawnCreatures(userPos[0], userPos[1], 5, radiusKm);
      await loadCreatures(); // обновить список существ
    } catch (err) {
      alert("Failed to spawn creatures: " + err.message);
    } finally {
      setSpawning(false);
    }
  };

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------
  if (loading) {
    return (
      <div style={styles.loading}>
        <p>📍 Waiting for your location…</p>
        <p style={{ fontSize: "0.8rem", color: "#888" }}>
          Please allow location access when prompted.
        </p>
      </div>
    );
  }

  if (locationError && !userPos) {
    return (
      <div style={styles.error}>
        <p>⚠️ {locationError}</p>
      </div>
    );
  }

  // Default fallback centre (Paris) if position is somehow still null.
  const centre = userPos || [48.8566, 2.3522];

  return (
    <div style={styles.container}>
      {locationError && (
        <div style={styles.banner}>⚠️ {locationError}</div>
      )}

      {/* Кнопка спауна покемонов */}
      <button
        style={styles.spawnButton}
        onClick={handleSpawn}
        disabled={!userPos || spawning}
      >
        {spawning ? "Spawning..." : "Spawn creatures here"}
      </button>

      <MapContainer
        center={centre}
        zoom={15}
        style={styles.map}
        zoomControl
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Keep the map centred on the user. */}
        <MapCenterer position={centre} />

        {/* Player marker + accuracy circle. */}
        {userPos && (
          <>
            <Marker position={userPos} icon={playerIcon}>
              <Popup>
                <strong>You are here</strong>
                <br />
                {userPos[0].toFixed(5)}, {userPos[1].toFixed(5)}
              </Popup>
            </Marker>
            <Circle
              center={userPos}
              radius={radiusKm * 1000}
              pathOptions={{ color: "#1976d2", fillOpacity: 0.05 }}
            />
          </>
        )}

        {/* Creature markers */}
        {creatures.map((creature) => (
          <Marker
            key={creature.id}
            position={[creature.latitude, creature.longitude]}
          >
            <Popup>
              <div style={styles.popup}>
                <strong>{creature.name}</strong>
                <br />
                <span style={styles.type}>{creature.type}</span>
                <br />
                {/* TODO: Show proximity warning if user is too far away. */}
                <button
                  style={styles.catchButton}
                  onClick={() => handleCatch(creature)}
                >
                  Catch!
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Creature count badge */}
      <div style={styles.badge}>
        {creatures.length} creature{creatures.length !== 1 ? "s" : ""} nearby
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Inline styles (keep minimal – full CSS theming is a future task)
// ---------------------------------------------------------------------------
const styles = {
  container: { position: "relative", width: "100%", height: "100vh" },
  map: { width: "100%", height: "100%" },
  spawnButton: {
    position: "absolute",
    top: 20,
    left: "50%",
    transform: "translateX(-50%)",
    zIndex: 1100,
    background: "#43a047",
    color: "#fff",
    border: "none",
    borderRadius: 20,
    padding: "10px 24px",
    fontSize: "1rem",
    fontWeight: "bold",
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
    cursor: "pointer",
    opacity: 1,
    transition: "opacity 0.2s",
    marginBottom: 8,
    outline: "none",
    pointerEvents: "auto",
  },
  loading: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    fontFamily: "sans-serif",
  },
  error: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    fontFamily: "sans-serif",
    color: "#c62828",
  },
  banner: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    background: "#fff3cd",
    color: "#856404",
    padding: "8px 16px",
    zIndex: 1000,
    fontSize: "0.85rem",
  },
  badge: {
    position: "absolute",
    bottom: 20,
    left: "50%",
    transform: "translateX(-50%)",
    background: "rgba(0,0,0,0.7)",
    color: "#fff",
    borderRadius: 20,
    padding: "6px 16px",
    fontSize: "0.85rem",
    zIndex: 1000,
    pointerEvents: "none",
  },
  popup: { fontFamily: "sans-serif", textAlign: "center" },
  type: {
    display: "inline-block",
    background: "#e0f2f1",
    borderRadius: 4,
    padding: "2px 6px",
    fontSize: "0.75rem",
    marginBottom: 6,
    textTransform: "capitalize",
  },
  catchButton: {
    background: "#e53935",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "6px 14px",
    cursor: "pointer",
    fontWeight: "bold",
    marginTop: 4,
  },
};
