/**
 * Navbar component – displayed on all authenticated pages.
 *
 * Contains:
 *   - App title (links to /map)
 *   - Link to the Map page
 *   - Link to the Collection/Gallery page
 *   - Logout button
 */

import { Link, useLocation } from 'react-router-dom'
import styles from './Navbar.module.css'

export default function Navbar({ onLogout }) {
  const { pathname } = useLocation()

  return (
    <nav className={styles.navbar}>
      {/* App branding */}
      <Link to="/map" className={styles.brand}>
        🐾 PokéGo
      </Link>

      {/* Navigation links */}
      <div className={styles.links}>
        <Link
          to="/map"
          className={`${styles.link} ${pathname === '/map' ? styles.active : ''}`}
        >
          🗺️ Map
        </Link>
        <Link
          to="/collection"
          className={`${styles.link} ${pathname === '/collection' ? styles.active : ''}`}
        >
          🎒 Collection
        </Link>
      </div>

      {/* Logout */}
      <button className={styles.logoutBtn} onClick={onLogout} aria-label="Log out">
        Logout
      </button>
    </nav>
  )
}
