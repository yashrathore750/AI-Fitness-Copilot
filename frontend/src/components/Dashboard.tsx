import { useState } from 'react'
import { User } from '../services/api'
import { FoodLogger } from './FoodLogger'
import { ActivityLogger } from './ActivityLogger'
import { AnalysisDisplay } from './AnalysisDisplay'

interface DashboardProps {
  user: User
  onLogout: () => void
}

export const Dashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const [refreshKey, setRefreshKey] = useState(0)

  const handleDataAdded = () => {
    setRefreshKey((prev) => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-primary-600">
                AI Fitness Copilot
              </h1>
              <p className="text-gray-600 mt-1">
                {user.weight_kg}kg • {user.height_cm}cm • {user.goal.replace('_', ' ')} • {user.diet_type.toUpperCase()}
              </p>
            </div>
            <button
              onClick={onLogout}
              className="btn-secondary"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Logging Section */}
          <div className="md:col-span-1 space-y-6">
            <FoodLogger userId={user.id} onFoodAdded={handleDataAdded} />
            <ActivityLogger userId={user.id} onActivityAdded={handleDataAdded} />
          </div>

          {/* Analysis Section */}
          <div className="md:col-span-2">
            <AnalysisDisplay key={refreshKey} userId={user.id} />
          </div>
        </div>
      </main>
    </div>
  )
}
