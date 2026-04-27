import { useState, useEffect } from 'react'
import { api, DailyAnalysisResponse } from '../services/api'

interface AnalysisDisplayProps {
  userId: number
}

export const AnalysisDisplay: React.FC<AnalysisDisplayProps> = ({ userId }) => {
  const [analysis, setAnalysis] = useState<DailyAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true)
        const data = await api.getDailyAnalysis(userId)
        setAnalysis(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analysis')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalysis()
  }, [userId])

  if (loading) {
    return <div className="text-center py-8">Loading analysis...</div>
  }

  if (error) {
    return <div className="text-center py-8 text-danger-600">{error}</div>
  }

  if (!analysis) return null

  const { nutrition_summary, deficiencies, insights } = analysis

  return (
    <div className="space-y-6">
      {/* Nutrition Summary */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Daily Nutrition Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">
              {nutrition_summary.calories_in.toFixed(0)}
            </div>
            <div className="text-sm text-gray-600">Calories In</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-warning-600">
              {nutrition_summary.calories_out.toFixed(0)}
            </div>
            <div className="text-sm text-gray-600">Calories Out</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-success-600">
              {nutrition_summary.protein_g.toFixed(0)}g
            </div>
            <div className="text-sm text-gray-600">Protein</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">
              {nutrition_summary.fiber_g.toFixed(1)}g
            </div>
            <div className="text-sm text-gray-600">Fiber</div>
          </div>
        </div>
      </div>

      {/* Activity */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Activity Summary</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">
              {nutrition_summary.steps.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Steps</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">
              {nutrition_summary.workout_minutes}
            </div>
            <div className="text-sm text-gray-600">Workout Minutes</div>
          </div>
        </div>
      </div>

      {/* Deficiencies */}
      {deficiencies.length > 0 && (
        <div className="card border-l-4 border-warning-500 bg-warning-50">
          <h3 className="text-lg font-bold mb-4">Nutrient Gaps</h3>
          <div className="space-y-3">
            {deficiencies.map((def) => (
              <div key={def.name} className="flex justify-between items-center">
                <div>
                  <div className={`font-semibold capitalize deficiency-${def.severity}`}>
                    {def.name}
                  </div>
                  <div className="text-sm text-gray-600">
                    {def.actual}{def.unit} / {def.target}{def.unit}
                  </div>
                </div>
                <span className={`text-xs px-3 py-1 rounded-full font-bold deficiency-${def.severity}`}>
                  {def.severity.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Insights */}
      <div className="card bg-gradient-to-br from-primary-50 to-blue-50 border-l-4 border-primary-500">
        <h3 className="text-lg font-bold mb-4">AI Coaching Insights</h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-primary-700 mb-2">Summary</h4>
            <p className="text-gray-700">{insights.summary}</p>
          </div>

          {insights.why_it_matters.length > 0 && (
            <div>
              <h4 className="font-semibold text-primary-700 mb-2">Why It Matters</h4>
              <ul className="space-y-1">
                {insights.why_it_matters.map((matter, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start">
                    <span className="text-primary-600 mr-2">•</span>
                    {matter}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {insights.suggestions.length > 0 && (
            <div>
              <h4 className="font-semibold text-primary-700 mb-2">Suggestions</h4>
              <ul className="space-y-2">
                {insights.suggestions.map((suggestion, idx) => (
                  <li key={idx} className="text-sm bg-white bg-opacity-60 p-3 rounded border-l-4 border-success-500">
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="text-xs text-gray-500 pt-2">
            Powered by {insights.source}
          </div>
        </div>
      </div>
    </div>
  )
}
