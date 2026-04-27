import { useState } from 'react'
import { api } from '../services/api'

interface FoodLoggerProps {
  userId: number
  onFoodAdded?: () => void
}

export const FoodLogger: React.FC<FoodLoggerProps> = ({ userId, onFoodAdded }) => {
  const [foodName, setFoodName] = useState('')
  const [servings, setServings] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!foodName.trim()) {
      setError('Food name is required')
      return
    }

    try {
      setLoading(true)
      await api.addFoodLog(userId, foodName, servings)
      setSuccess(true)
      setFoodName('')
      setServings(1)
      setError(null)
      onFoodAdded?.()

      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log food')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-bold mb-4">Log Food</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Food Name</label>
          <input
            type="text"
            className="input-field"
            placeholder="e.g., oats, spinach, chicken"
            value={foodName}
            onChange={(e) => setFoodName(e.target.value)}
            disabled={loading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Servings</label>
          <input
            type="number"
            className="input-field"
            min="0.5"
            step="0.5"
            value={servings}
            onChange={(e) => setServings(parseFloat(e.target.value))}
            disabled={loading}
          />
        </div>

        {error && <div className="text-danger-600 text-sm">{error}</div>}
        {success && <div className="text-success-600 text-sm">✓ Food logged successfully</div>}

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full disabled:opacity-50"
        >
          {loading ? 'Logging...' : 'Log Food'}
        </button>
      </form>
    </div>
  )
}
