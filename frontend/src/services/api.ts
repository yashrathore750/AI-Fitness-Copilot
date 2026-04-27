const API_BASE = '/api'

export interface User {
  id: number
  weight_kg: number
  height_cm: number
  goal: 'fat_loss' | 'maintenance' | 'muscle_gain' | 'recomposition'
  diet_type: 'veg' | 'eggetarian' | 'non_veg' | 'vegan'
  created_at: string
}

export interface Deficiency {
  name: string
  actual: number
  target: number
  unit: string
  severity: 'high' | 'medium' | 'low'
}

export interface NutritionSummary {
  date: string
  calories_in: number
  calories_out: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g: number
  vitamins: Record<string, number>
  minerals: Record<string, number>
  steps: number
  workout_minutes: number
  foods_missing_from_catalog: string[]
}

export interface InsightPayload {
  summary: string
  why_it_matters: string[]
  suggestions: string[]
  source: string
}

export interface DailyAnalysisResponse {
  user_id: number
  nutrition_summary: NutritionSummary
  deficiencies: Deficiency[]
  insights: InsightPayload
}

export const api = {
  // Users
  createUser: async (data: Omit<User, 'id' | 'created_at'>) => {
    const res = await fetch(`${API_BASE}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to create user')
    return res.json() as Promise<User>
  },

  getUser: async (userId: number) => {
    const res = await fetch(`${API_BASE}/users/${userId}`)
    if (!res.ok) throw new Error('Failed to fetch user')
    return res.json() as Promise<User>
  },

  // Food Logs
  addFoodLog: async (userId: number, foodName: string, servings: number) => {
    const res = await fetch(`${API_BASE}/food-log`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        food_name: foodName,
        servings,
      }),
    })
    if (!res.ok) throw new Error('Failed to log food')
    return res.json()
  },

  getFoodLogs: async (userId: number, targetDate?: string) => {
    const url = new URL(`${API_BASE}/food-log`, window.location.origin)
    url.searchParams.append('user_id', userId.toString())
    if (targetDate) url.searchParams.append('target_date', targetDate)
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error('Failed to fetch food logs')
    return res.json()
  },

  // Activity Logs
  addActivityLog: async (
    userId: number,
    steps: number,
    workoutType?: string,
    durationMinutes?: number
  ) => {
    const res = await fetch(`${API_BASE}/activity`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        steps,
        workout_type: workoutType,
        duration_minutes: durationMinutes || 0,
      }),
    })
    if (!res.ok) throw new Error('Failed to log activity')
    return res.json()
  },

  getActivityLogs: async (userId: number, targetDate?: string) => {
    const url = new URL(`${API_BASE}/activity`, window.location.origin)
    url.searchParams.append('user_id', userId.toString())
    if (targetDate) url.searchParams.append('target_date', targetDate)
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error('Failed to fetch activity logs')
    return res.json()
  },

  // Analysis
  getDailyAnalysis: async (userId: number, targetDate?: string) => {
    const url = new URL(`${API_BASE}/analysis/today`, window.location.origin)
    url.searchParams.append('user_id', userId.toString())
    if (targetDate) url.searchParams.append('target_date', targetDate)
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error('Failed to fetch analysis')
    return res.json() as Promise<DailyAnalysisResponse>
  },
}
