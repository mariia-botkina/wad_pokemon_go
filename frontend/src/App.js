/**
 * App.js – Root application component.
 *
 * Currently renders the MapView directly.  As the app grows this component
 * will host routing (React Router) and global context providers such as the
 * authentication context.
 *
 * TODO: Add React Router with routes for /map, /collection, /login, /profile.
 * TODO: Add AuthContext provider and ProtectedRoute wrapper.
 * TODO: Display a top navigation bar with user avatar and collection count.
 */

import React, { useState } from "react";
import MapView from "./components/MapView";

export default function App() {
  const [errorMsg, setErrorMsg] = useState(null);

  return (
    <div>
      {errorMsg && (
        <div style={styles.globalError}>
          ⚠️ {errorMsg}
        </div>
      )}
      {/*
        MapView handles all map rendering, geolocation, and creature display.
        onError receives location or network errors to surface in the UI.
      */}
      <MapView radiusKm={0.5} onError={setErrorMsg} />
    </div>
  );
}

const styles = {
  globalError: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    background: "#ffcdd2",
    color: "#b71c1c",
    padding: "8px 16px",
    textAlign: "center",
    zIndex: 9999,
    fontSize: "0.9rem",
  },
};
