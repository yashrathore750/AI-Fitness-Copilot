import { useState } from 'react'
import { api } from '../services/api'

interface ActivityLoggerProps {
  userId: number
  onActivityAdded?: () => void
}

const WORKOUT_TYPES = ['leg_day', 'push_day', 'pull_day', 'run', 'cycling', 'yoga']

export const ActivityLogger: React.FC<ActivityLoggerProps> = ({ userId, onActivityAdded }) => {
  const [steps, setSteps] = useState(0)
  const [workoutType, setWorkoutType] = useState('')
  const [durationMinutes, setDurationMinutes] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      setLoading(true)
      await api.addActivityLog(userId, steps, workoutType || undefined, durationMinutes || undefined)
      setSuccess(true)
      setSteps(0)
      setWorkoutType('')
      setDurationMinutes(0)
      setError(null)
      onActivityAdded?.()

      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log activity')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-bold mb-4">Log Activity</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Steps</label>
          <input
            type="number"
            className="input-field"
            min="0"
            value={steps}
            onChange={(e) => setSteps(parseInt(e.target.value) || 0)}
            disabled={loading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Workout Type (optional)</label>
          <select
            className="input-field"
            value={workoutType}
            onChange={(e) => setWorkoutType(e.target.value)}
            disabled={loading}
          >
            <option value="">Select a workout</option>
            {WORKOUT_TYPES.map((type) => (
              <option key={type} value={type}>
                {type.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {workoutType && (
          <div>
            <label className="block text-sm font-medium mb-2">Duration (minutes)</label>
            <input
              type="number"
              className="input-field"
              min="0"
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(parseInt(e.target.value) || 0)}
              disabled={loading}
            />
          </div>
        )}

        {error && <div className="text-danger-600 text-sm">{error}</div>}
        {success && <div className="text-success-600 text-sm">✓ Activity logged successfully</div>}

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full disabled:opacity-50"
        >
          {loading ? 'Logging...' : 'Log Activity'}
        </button>
      </form>
    </div>
  )
}
