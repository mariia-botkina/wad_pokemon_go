/**
 * CollectionPage – displays the user's caught creatures (gallery).
 *
 * Fetches data from GET /users/me/collection (JWT required).
 * Items are shown in a responsive card grid ordered newest-to-oldest.
 *
 * Each card shows:
 *   - Creature type emoji and name
 *   - Type badge
 *   - Base power stat
 *   - Description
 *   - Catch timestamp (formatted for readability)
 *
 * Navigation:
 *   - Navbar provides links back to the Map and to this page.
 *   - "Back to Map" button at the top of the page for quick access.
 *
 * TODOs (for future sprints):
 * TODO: Add sort controls (by name A-Z, by type, by power, by catch date).
 * TODO: Add filter controls (by creature type).
 * TODO: Add pagination or infinite scroll for large collections.
 * TODO: Display rarity badge once rarity field is added to the creature model.
 * TODO: Add "trade" button per card once creature trading is implemented.
 * TODO: Show catch location on a mini-map thumbnail per card.
 */

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getMyCollection } from '../api/client'
import styles from './CollectionPage.module.css'

/** Emoji per creature type – mirrors the MapPage helper. */
const TYPE_EMOJI = {
  fire:     '🔥',
  water:    '💧',
  grass:    '🌿',
  electric: '⚡',
  rock:     '🪨',
  ghost:    '👻',
  ice:      '❄️',
  psychic:  '🔮',
}

/** Format an ISO timestamp as a human-readable relative or absolute string. */
function formatDate(iso) {
  const date = new Date(iso)
  // If less than 24 h ago, show relative time; otherwise show full date
  const diffMs = Date.now() - date.getTime()
  const diffHours = diffMs / (1000 * 60 * 60)
  if (diffHours < 1) {
    const mins = Math.round(diffMs / 60_000)
    return `${mins} min${mins !== 1 ? 's' : ''} ago`
  }
  if (diffHours < 24) {
    const hrs = Math.round(diffHours)
    return `${hrs} hour${hrs !== 1 ? 's' : ''} ago`
  }
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

export default function CollectionPage() {
  const [collection, setCollection] = useState(null)  // null = loading
  const [error, setError]           = useState('')

  useEffect(() => {
    getMyCollection()
      .then(setCollection)
      .catch((err) => setError(err.message))
  }, [])

  // ── Loading state ──────────────────────────────────────────────────────────
  if (!collection && !error) {
    return (
      <div className={styles.centered}>
        <div className="spinner" />
        <p>Loading your collection…</p>
      </div>
    )
  }

  // ── Error state ────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className={styles.centered}>
        <p className={styles.errorMsg}>⚠️ {error}</p>
        <Link to="/map" className="btn btn-primary">Back to Map</Link>
      </div>
    )
  }

  // ── Empty collection ───────────────────────────────────────────────────────
  if (collection.total === 0) {
    return (
      <div className={styles.centered}>
        <div className={styles.emptyEmoji}>🎒</div>
        <h2 className={styles.emptyTitle}>Your collection is empty</h2>
        <p className={styles.emptyMsg}>
          Head to the map and catch your first creature!
        </p>
        <Link to="/map" className="btn btn-primary">🗺️ Go to Map</Link>
      </div>
    )
  }

  // ── Collection grid ────────────────────────────────────────────────────────
  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>🎒 My Collection</h1>
          <p className={styles.subtitle}>
            {collection.total} creature{collection.total !== 1 ? 's' : ''} caught
          </p>
        </div>
        <Link to="/map" className="btn btn-ghost">🗺️ Map</Link>
      </div>

      {/* TODO: Add sort/filter controls here once the backend supports them. */}
      {/* Example: <SortFilterBar onSort={...} onFilter={...} /> */}

      {/* Card grid – newest first (ordering is done server-side) */}
      <div className={styles.grid}>
        {collection.items.map((entry) => (
          <CreatureCard key={entry.id} entry={entry} />
        ))}
      </div>
    </div>
  )
}

/**
 * CreatureCard – a single card in the collection gallery.
 *
 * @param {{ entry: CaughtCreature }} props
 */
function CreatureCard({ entry }) {
  const { creature, caught_at } = entry
  const emoji = TYPE_EMOJI[creature.creature_type] ?? '❓'

  return (
    <div className={styles.card}>
      {/* Large type emoji */}
      <div className={styles.cardEmoji}>{emoji}</div>

      {/* Name + type badge */}
      <h3 className={styles.cardName}>{creature.name}</h3>
      <span className={`badge badge-${creature.creature_type}`}>
        {creature.creature_type}
      </span>

      {/* Stats */}
      <p className={styles.cardPower}>⚔️ {creature.base_power} power</p>

      {/* Description */}
      <p className={styles.cardDesc}>{creature.description}</p>

      {/* Catch timestamp */}
      <p className={styles.cardDate}>
        🕐 Caught {formatDate(caught_at)}
      </p>

      {/*
        TODO: Add rarity display once creature.rarity is available.
              e.g. <span className={`badge badge-rarity-${creature.rarity}`}>{creature.rarity}</span>
        TODO: Add trade button once creature trading feature is built.
              e.g. <button className="btn btn-ghost">🤝 Trade</button>
      */}
    </div>
  )
}
