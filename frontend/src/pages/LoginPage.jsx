/**
 * LoginPage – handles both login and registration.
 *
 * Toggles between two modes with a single button.
 * On success, calls onLogin(token) which is provided by the parent App.
 */

import { useState } from 'react'
import { register, login } from '../api/client'
import styles from './LoginPage.module.css'

export default function LoginPage({ onLogin }) {
  // Toggle between "login" and "register" modes
  const [mode, setMode] = useState('login')

  const [username, setUsername] = useState('')
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      let data
      if (mode === 'register') {
        data = await register(username, email, password)
      } else {
        data = await login(username, password)
      }
      onLogin(data.access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {/* Logo / branding */}
        <div className={styles.logo}>🐾</div>
        <h1 className={styles.title}>PokéGo</h1>
        <p className={styles.subtitle}>
          {mode === 'login' ? 'Welcome back!' : 'Create your account'}
        </p>

        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Username */}
          <label className={styles.label} htmlFor="username">Username</label>
          <input
            id="username"
            className={styles.input}
            type="text"
            required
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="trainer123"
          />

          {/* Email – only shown in register mode */}
          {mode === 'register' && (
            <>
              <label className={styles.label} htmlFor="email">Email</label>
              <input
                id="email"
                className={styles.input}
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="trainer@example.com"
              />
            </>
          )}

          {/* Password */}
          <label className={styles.label} htmlFor="password">Password</label>
          <input
            id="password"
            className={styles.input}
            type="password"
            required
            autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />

          {/* Error message */}
          {error && <p className={styles.error}>{error}</p>}

          {/* Submit */}
          <button
            type="submit"
            className={`btn btn-primary ${styles.submitBtn}`}
            disabled={loading}
          >
            {loading
              ? 'Please wait…'
              : mode === 'login' ? 'Log in' : 'Create account'}
          </button>
        </form>

        {/* Toggle mode */}
        <p className={styles.toggle}>
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            className={styles.toggleBtn}
            onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}
          >
            {mode === 'login' ? 'Register' : 'Log in'}
          </button>
        </p>
      </div>
    </div>
  )
}
