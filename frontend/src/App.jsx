/**
 * Root application component.
 *
 * Manages authentication state (JWT stored in localStorage) and provides
 * top-level routing between Login, Map, and Collection pages.
 *
 * Authentication flow:
 *   1. If no token → redirect to /login.
 *   2. After login/register → store token, navigate to /map.
 *   3. Logout → clear token, navigate to /login.
 */

import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useState, useCallback } from 'react'
import LoginPage from './pages/LoginPage'
import MapPage from './pages/MapPage'
import CollectionPage from './pages/CollectionPage'
import Navbar from './components/Navbar'

export default function App() {
  // Token is read from localStorage on mount so the user stays logged in
  // across page refreshes.
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const navigate = useNavigate()

  /** Called after a successful login/register to persist the token. */
  const handleLogin = useCallback((newToken) => {
    localStorage.setItem('token', newToken)
    setToken(newToken)
    navigate('/map')
  }, [navigate])

  /** Clear auth state and redirect to login. */
  const handleLogout = useCallback(() => {
    localStorage.removeItem('token')
    setToken(null)
    navigate('/login')
  }, [navigate])

  return (
    <>
      {/* Show the navbar on all authenticated routes */}
      {token && <Navbar onLogout={handleLogout} />}

      <Routes>
        {/* Public route */}
        <Route
          path="/login"
          element={
            token
              ? <Navigate to="/map" replace />
              : <LoginPage onLogin={handleLogin} />
          }
        />

        {/* Protected routes – redirect to login if not authenticated */}
        <Route
          path="/map"
          element={token ? <MapPage token={token} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/collection"
          element={token ? <CollectionPage token={token} /> : <Navigate to="/login" replace />}
        />

        {/* Default redirect */}
        <Route path="*" element={<Navigate to={token ? '/map' : '/login'} replace />} />
      </Routes>
    </>
  )
}
