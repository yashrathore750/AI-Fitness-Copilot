# 🧠 AI Fitness Copilot (Senior-Level System)

## 📌 Overview

AI Fitness Copilot is a **hybrid intelligence system** that combines:

* Deterministic nutrition & activity computation
* LLM-based reasoning for insights and recommendations

This is **NOT a calorie tracker**.
This system answers:

> “What am I missing today, and what should I do about it?”

---

## 🎯 Goals

* Track food, activity, and health metrics
* Compute accurate macros + micronutrients (deterministic)
* Identify nutrient deficiencies (rule-based, NOT AI)
* Generate personalized insights (LLM)
* Provide actionable recommendations

---

## 🚫 Non-Goals

* No heavy computer vision (no food image recognition in V1)
* No full wearable integrations (mock data initially)
* No over-reliance on LLMs for calculations

---

## 🧱 High-Level Architecture

```
[User Input]
   ↓
[API Layer - FastAPI]
   ↓
[Deterministic Engine]
   ↓
[Deficiency Detection]
   ↓
[Context Builder]
   ↓
[LLM Insight Engine]
   ↓
[Response + Storage]
```

---

## ⚙️ Tech Stack

### Backend

* FastAPI (async)
* PostgreSQL (primary DB)
* Redis (caching)

### AI Layer

* OpenAI / LLM provider
* Embeddings (for future RAG)
* Optional: LangGraph (workflow orchestration)

### Frontend (optional V1)

* React / Next.js

---

## 🧩 Core Modules

---

### 1. Data Models (PostgreSQL)

#### User

* id
* weight
* height
* goal (fat_loss / maintenance / muscle_gain/ recomposition)
* diet_type (veg / eggetarian / non-veg/ vegan)

#### FoodLog

* id
* user_id
* food_name
* quantity
* timestamp

#### ActivityLog

* id
* user_id
* steps
* workout_type
* duration
* calories_burned (estimated)

#### NutritionEntry

* food_id
* calories
* protein
* carbs
* fats
* fiber
* vitamins (JSON)
* minerals (JSON)

---

### 2. Deterministic Engine

#### Responsibilities:

* Calculate total calories intake
* Calculate macro totals
* Aggregate micronutrients
* Estimate calories burned:

  * Steps → formula
  * Workout → MET-based estimation

#### Output:

```
{
  "calories_in": 1800,
  "calories_out": 2200,
  "protein": 120g,
  "fiber": 18g,
  "magnesium": 220mg
}
```

---

### 3. Deficiency Detection Engine (RULE-BASED)

Compare against RDA:

Example:

```
if fiber < 25g:
    mark "fiber_deficient"

if magnesium < threshold:
    mark "magnesium_deficient"
```

#### Output:

```
{
  "deficiencies": [
    {"name": "fiber", "severity": "medium"},
    {"name": "magnesium", "severity": "high"}
  ]
}
```

---

### 4. Context Builder

Construct structured input for LLM:

```
{
  "user_goal": "fat_loss",
  "activity": {
    "steps": 10000,
    "workout": "leg_day"
  },
  "nutrition_summary": {...},
  "deficiencies": [...],
  "diet_type": "vegetarian"
}
```

---

### 5. LLM Insight Engine

#### Responsibilities:

* Explain deficiencies
* Provide actionable suggestions
* Personalize recommendations

#### Example Prompt:

```
You are a fitness nutrition coach.

User goal: fat loss
Diet: vegetarian

Deficiencies:
- Magnesium (high)
- Fiber (medium)

Workout: leg day

Generate:
1. Summary of the day
2. Why deficiencies matter
3. 2-3 actionable food suggestions (Indian vegetarian)
4. Keep it concise
```

---

### 6. API Endpoints (FastAPI)

#### Food Logging

* POST /food-log
* GET /food-log

#### Activity Logging

* POST /activity
* GET /activity

#### Daily Analysis

* GET /analysis/today

Returns:

* nutrition summary
* deficiencies
* AI insights

---

## 🔁 Workflow (End-to-End)

1. User logs food + activity
2. Backend aggregates data
3. Deterministic engine computes totals
4. Deficiency engine flags gaps
5. Context builder prepares LLM input
6. LLM generates insights
7. Response returned + cached

---

## 🧠 Advanced Features (V2)

* Semantic caching (avoid repeated LLM calls)
* Weekly trend analysis
* Habit detection:

  * “Low fiber on weekends”
* Dynamic model selection (cheap vs expensive LLM)
* LangGraph workflow orchestration

---

## ⚠️ Engineering Principles

### 1. Separation of Concerns

* Math ≠ AI
* AI only for reasoning

### 2. Determinism First

* All calculations must be reproducible

### 3. Cost Awareness

* Cache LLM responses
* Avoid unnecessary calls

### 4. Observability

* Log:

  * inputs
  * LLM prompts
  * outputs

---

## 🧪 Testing Strategy

* Unit tests:

  * calorie calculations
  * deficiency detection

* Integration tests:

  * full pipeline

* Evaluation:

  * compare AI suggestions vs expected

---

## 🚀 Implementation Plan (Step-by-Step)

### Phase 1: Setup

* Setup FastAPI project
* Setup PostgreSQL schema
* Create basic models
* Add .github folder update it incrementally with prompts, project knowledge, agents, skills, and architecture

---

### Phase 2: Deterministic Core

* Implement nutrition aggregation
* Implement calorie calculations
* Implement activity burn estimation

---

### Phase 3: Deficiency Engine

* Add RDA reference data
* Implement deficiency detection logic

---

### Phase 4: LLM Integration (I want to code this out so I we should use Ask mode for this)

* Create prompt templates
* Build insight generation service
* Add caching

---

### Phase 5: API Layer

* Build endpoints
* Connect full pipeline

---

### Phase 6: Polish

* Logging
* Error handling
* Performance improvements

---

## 💡 Example Output

```
Summary:
You maintained a calorie deficit today, which aligns with your fat loss goal.

Insights:
Protein intake is adequate for recovery after your leg workout.
However, low magnesium may affect muscle recovery and energy levels.

Suggestions:
- Add pumpkin seeds or spinach to your next meal
- Include a fruit like banana for better recovery
```

---

## 🏁 Final Note

This project demonstrates:

* System design thinking
* Hybrid AI architecture
* Practical LLM usage
* Backend engineering depth

This is NOT a demo project.
This should feel like a **real product system**.
