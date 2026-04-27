import { useState, useEffect } from 'react'
import { api, User } from '../services/api'

interface OnboardingProps {
  onUserCreated: (user: User) => void
}

const GOALS = ['fat_loss', 'maintenance', 'muscle_gain', 'recomposition'] as const
const DIET_TYPES = ['veg', 'eggetarian', 'non_veg', 'vegan'] as const

export const Onboarding: React.FC<OnboardingProps> = ({ onUserCreated }) => {
  const [weight, setWeight] = useState(75)
  const [height, setHeight] = useState(175)
  const [goal, setGoal] = useState<typeof GOALS[number]>('fat_loss')
  const [dietType, setDietType] = useState<typeof DIET_TYPES[number]>('veg')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Check localStorage for existing user
  useEffect(() => {
    const savedUserId = localStorage.getItem('userId')
    if (savedUserId) {
      const loadUser = async () => {
        try {
          const user = await api.getUser(parseInt(savedUserId))
          onUserCreated(user)
        } catch (err) {
          localStorage.removeItem('userId')
        }
      }
      loadUser()
    }
  }, [onUserCreated])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setLoading(true)
      const user = await api.createUser({
        weight_kg: weight,
        height_cm: height,
        goal,
        diet_type: dietType,
      })
      localStorage.setItem('userId', user.id.toString())
      onUserCreated(user)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create user')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-100 flex items-center justify-center p-4">
      <div className="card max-w-md w-full">
        <h1 className="text-3xl font-bold text-center mb-2 text-primary-600">
          AI Fitness Copilot
        </h1>
        <p className="text-center text-gray-600 mb-6">
          Your personal fitness companion
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Weight (kg)</label>
            <input
              type="number"
              className="input-field"
              min="30"
              max="300"
              value={weight}
              onChange={(e) => setWeight(parseInt(e.target.value) || 0)}
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Height (cm)</label>
            <input
              type="number"
              className="input-field"
              min="100"
              max="250"
              value={height}
              onChange={(e) => setHeight(parseInt(e.target.value) || 0)}
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Fitness Goal</label>
            <select
              className="input-field"
              value={goal}
              onChange={(e) => setGoal(e.target.value as typeof GOALS[number])}
              disabled={loading}
            >
              {GOALS.map((g) => (
                <option key={g} value={g}>
                  {g.replace('_', ' ').toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Diet Type</label>
            <select
              className="input-field"
              value={dietType}
              onChange={(e) => setDietType(e.target.value as typeof DIET_TYPES[number])}
              disabled={loading}
            >
              {DIET_TYPES.map((d) => (
                <option key={d} value={d}>
                  {d.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          {error && <div className="text-danger-600 text-sm text-center">{error}</div>}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full disabled:opacity-50"
          >
            {loading ? 'Creating Profile...' : 'Get Started'}
          </button>
        </form>
      </div>
    </div>
  )
}
