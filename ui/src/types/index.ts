export interface Task {
  id: string
  title: string
  description: string
  priority: 1 | 2 | 3 | 4 | 5
  tags: string[]
  duration_hours: number | null
  deadline: string | null
  completed: boolean
  created_at: string
  completed_at: string | null
}

export interface TaskCreate {
  title: string
  description?: string
  priority: number
  tags?: string[]
  duration_hours?: number | null
  deadline?: string | null
}

export interface TaskUpdate {
  title?: string
  description?: string
  priority?: number
  tags?: string[]
  duration_hours?: number | null
  deadline?: string | null
}

export interface AgentDecision {
  next_task: Task | null
  productivity_score: number
  suggestion: string
  reasoning: string
}

export interface ErrorResponse {
  error_code: string
  message: string
  details: Record<string, unknown>
}
