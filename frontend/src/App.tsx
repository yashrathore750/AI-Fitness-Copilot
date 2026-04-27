import { useState } from 'react'
import { User } from './services/api'
import { Onboarding } from './components/Onboarding'
import { Dashboard } from './components/Dashboard'

function App() {
  const [user, setUser] = useState<User | null>(null)

  const handleUserCreated = (newUser: User) => {
    setUser(newUser)
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('userId')
  }

  return (
    <>
      {!user ? (
        <Onboarding onUserCreated={handleUserCreated} />
      ) : (
        <Dashboard user={user} onLogout={handleLogout} />
      )}
    </>
  )
}

export default App
