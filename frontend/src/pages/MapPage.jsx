/**
 * MapPage – the main gameplay screen.
 *
 * Features:
 *   - Leaflet map centered on the user's GPS location.
 *   - Fetches nearby spawned creatures and shows them as markers.
 *   - Click a creature marker → catch dialog with confirmation.
 *   - "Spawn creature here" button (debug/demo helper).
 *   - Link to the Collection page via the Navbar.
 *
 * TODO: Replace manual spawn button with automatic server-driven spawning.
 * TODO: Add real-time refresh (WebSocket or polling) for new spawns.
 * TODO: Show creature rarity icons on markers once rarity field is added.
 */

import { useEffect, useRef, useState, useCallback } from 'react'
import L from 'leaflet'
import { getNearbyCreatures, spawnCreature, catchCreature } from '../api/client'
import styles from './MapPage.module.css'

// Fix Leaflet's default icon path when bundled with Vite/webpack
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png'

const DefaultIcon = L.icon({
  iconUrl,
  iconRetinaUrl: iconRetina,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})
L.Marker.prototype.options.icon = DefaultIcon

/** Creature emoji per type for a colourful marker label. */
const TYPE_EMOJI = {
  fire: '🔥',
  water: '💧',
  grass: '🌿',
  electric: '⚡',
  rock: '🪨',
  ghost: '👻',
  ice: '❄️',
  psychic: '🔮',
}

/** Build a colourful div-icon for spawned creatures. */
function makeCreatureIcon(type) {
  const emoji = TYPE_EMOJI[type] ?? '❓'
  return L.divIcon({
    html: `<div class="${styles.creatureIcon}">${emoji}</div>`,
    className: '',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  })
}

export default function MapPage() {
  const mapRef    = useRef(null)  // DOM element
  const leafletRef = useRef(null) // Leaflet map instance
  const markersRef = useRef({})   // spawnId → Leaflet Marker

  const [position, setPosition]       = useState(null)   // [lat, lon]
  const [geoError, setGeoError]       = useState('')
  const [creatures, setCreatures]     = useState([])
  const [selected, setSelected]       = useState(null)   // spawned creature for catch dialog
  const [catchMsg, setCatchMsg]       = useState('')
  const [spawning, setSpawning]       = useState(false)
  const [catching, setCatching]       = useState(false)
  const [loading, setLoading]         = useState(true)

  // ── Initialise Leaflet map ─────────────────────────────────────────────────
  useEffect(() => {
    if (leafletRef.current) return  // already initialised

    const map = L.map(mapRef.current, { zoomControl: true }).setView([51.5074, -0.1278], 15)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map)

    leafletRef.current = map

    return () => {
      map.remove()
      leafletRef.current = null
    }
  }, [])

  // ── Geolocation ────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!navigator.geolocation) {
      setGeoError('Geolocation is not supported by your browser.')
      setLoading(false)
      return
    }
    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords
        setPosition([latitude, longitude])
        setGeoError('')
        if (leafletRef.current) {
          leafletRef.current.setView([latitude, longitude], leafletRef.current.getZoom())
        }
        setLoading(false)
      },
      (err) => {
        setGeoError(`Location error: ${err.message}`)
        setLoading(false)
      },
      { enableHighAccuracy: true }
    )
    return () => navigator.geolocation.clearWatch(watchId)
  }, [])

  // ── Fetch nearby creatures ─────────────────────────────────────────────────
  const fetchCreatures = useCallback(async (lat, lon) => {
    try {
      const data = await getNearbyCreatures(lat, lon)
      setCreatures(data)
    } catch {
      // Silently fail – creatures will just not show (no auth needed for listing)
    }
  }, [])

  useEffect(() => {
    if (!position) return
    fetchCreatures(position[0], position[1])
    // Refresh every 15 seconds to pick up new spawns
    // TODO: Replace with a WebSocket subscription once real-time backend is available.
    const interval = setInterval(() => fetchCreatures(position[0], position[1]), 15_000)
    return () => clearInterval(interval)
  }, [position, fetchCreatures])

  // ── Sync Leaflet markers with creature list ────────────────────────────────
  useEffect(() => {
    if (!leafletRef.current) return
    const map = leafletRef.current
    const currentIds = new Set(creatures.map((c) => c.id))

    // Remove markers for despawned creatures
    Object.keys(markersRef.current).forEach((id) => {
      if (!currentIds.has(Number(id))) {
        markersRef.current[id].remove()
        delete markersRef.current[id]
      }
    })

    // Add markers for new creatures
    creatures.forEach((spawn) => {
      if (markersRef.current[spawn.id]) return  // already on map
      const marker = L.marker([spawn.latitude, spawn.longitude], {
        icon: makeCreatureIcon(spawn.creature.creature_type),
      })
        .addTo(map)
        .bindTooltip(spawn.creature.name, { permanent: false, direction: 'top' })
        .on('click', () => {
          setSelected(spawn)
          setCatchMsg('')
        })
      markersRef.current[spawn.id] = marker
    })
  }, [creatures])

  // ── Spawn a creature at current position (demo helper) ────────────────────
  async function handleSpawn() {
    if (!position) return
    setSpawning(true)
    try {
      await spawnCreature(position[0], position[1])
      await fetchCreatures(position[0], position[1])
    } catch (err) {
      alert(`Spawn failed: ${err.message}`)
    } finally {
      setSpawning(false)
    }
  }

  // ── Attempt to catch the selected creature ────────────────────────────────
  async function handleCatch() {
    if (!selected || !position) return
    setCatching(true)
    setCatchMsg('')
    try {
      const result = await catchCreature(selected.id, position[0], position[1])
      setCatchMsg(result.message)
      if (result.success) {
        // Remove the caught creature from local state and close dialog after 1.5 s
        setCreatures((prev) => prev.filter((c) => c.id !== selected.id))
        setTimeout(() => setSelected(null), 1500)
      }
    } catch (err) {
      setCatchMsg(`Error: ${err.message}`)
    } finally {
      setCatching(false)
    }
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className={styles.page}>
      {/* Map container */}
      <div ref={mapRef} className={styles.map} />

      {/* Status bar */}
      <div className={styles.statusBar}>
        {loading && <span className={styles.statusMsg}>📡 Getting your location…</span>}
        {geoError && <span className={styles.statusError}>{geoError}</span>}
        {!loading && !geoError && (
          <span className={styles.statusMsg}>
            🐾 {creatures.length} creature{creatures.length !== 1 ? 's' : ''} nearby
          </span>
        )}

        {/* Spawn button (demo / debug) */}
        <button
          className="btn btn-primary"
          onClick={handleSpawn}
          disabled={spawning || !position}
          title="Spawn a random creature at your location"
        >
          {spawning ? '…' : '✨ Spawn'}
        </button>
      </div>

      {/* Catch dialog – shown when user taps a creature marker */}
      {selected && (
        <div className={styles.overlay} onClick={() => setSelected(null)}>
          <div className={styles.dialog} onClick={(e) => e.stopPropagation()}>
            <div className={styles.dialogEmoji}>
              {TYPE_EMOJI[selected.creature.creature_type] ?? '❓'}
            </div>
            <h2 className={styles.dialogTitle}>{selected.creature.name}</h2>
            <span className={`badge badge-${selected.creature.creature_type}`}>
              {selected.creature.creature_type}
            </span>
            <p className={styles.dialogDesc}>{selected.creature.description}</p>
            <p className={styles.dialogPower}>⚔️ Base Power: {selected.creature.base_power}</p>

            {catchMsg && (
              <p className={catchMsg.startsWith('Error') ? styles.catchError : styles.catchSuccess}>
                {catchMsg}
              </p>
            )}

            <div className={styles.dialogActions}>
              <button
                className="btn btn-primary"
                onClick={handleCatch}
                disabled={catching || !!catchMsg}
              >
                {catching ? 'Catching…' : '🎯 Catch!'}
              </button>
              <button className="btn btn-ghost" onClick={() => setSelected(null)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
