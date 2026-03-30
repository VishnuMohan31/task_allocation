import { useState } from 'react'
import { ClipboardList } from 'lucide-react'
import { clsx } from 'clsx'
import type { Task } from '../types'
import { TaskCard } from './TaskCard'

type Filter = 'all' | 'pending' | 'completed'
type SortKey = 'priority' | 'deadline' | 'created_at'

interface TaskListProps {
  tasks: Task[]
  highlightedTaskId?: string | null
  onComplete: (id: string) => void
  onEdit: (task: Task) => void
  onDelete: (id: string) => void
  completingId?: string | null
  deletingId?: string | null
}

export function TaskList({
  tasks,
  highlightedTaskId,
  onComplete,
  onEdit,
  onDelete,
  completingId,
  deletingId,
}: TaskListProps) {
  const [filter, setFilter] = useState<Filter>('all')
  const [sort, setSort] = useState<SortKey>('priority')

  const filtered = tasks.filter((t) => {
    if (filter === 'pending') return !t.completed
    if (filter === 'completed') return t.completed
    return true
  })

  const sorted = [...filtered].sort((a, b) => {
    if (sort === 'priority') return b.priority - a.priority
    if (sort === 'deadline') {
      if (!a.deadline) return 1
      if (!b.deadline) return -1
      return new Date(a.deadline).getTime() - new Date(b.deadline).getTime()
    }
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  const filterTabs: { key: Filter; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'pending', label: 'Pending' },
    { key: 'completed', label: 'Completed' },
  ]

  return (
    <div>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4 gap-3 flex-wrap">
        {/* Filter tabs */}
        <div className="flex items-center gap-1 bg-slate-100 rounded-xl p-1">
          {filterTabs.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={clsx(
                'px-3 py-1.5 text-xs font-medium rounded-lg transition-colors',
                filter === key
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              )}
            >
              {label}
              <span className="ml-1.5 text-slate-400">
                {key === 'all'
                  ? tasks.length
                  : key === 'pending'
                  ? tasks.filter((t) => !t.completed).length
                  : tasks.filter((t) => t.completed).length}
              </span>
            </button>
          ))}
        </div>

        {/* Sort */}
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortKey)}
          className="text-xs text-slate-600 border border-slate-200 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-violet-500"
          aria-label="Sort tasks"
        >
          <option value="priority">Sort: Priority</option>
          <option value="deadline">Sort: Deadline</option>
          <option value="created_at">Sort: Newest</option>
        </select>
      </div>

      {/* List */}
      {sorted.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="p-5 bg-slate-100 rounded-2xl mb-4">
            <ClipboardList size={32} className="text-slate-400" />
          </div>
          <p className="text-sm font-medium text-slate-600">No tasks here</p>
          <p className="text-xs text-slate-400 mt-1">
            {filter === 'all'
              ? 'Create your first task to get started'
              : `No ${filter} tasks`}
          </p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {sorted.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              highlighted={task.id === highlightedTaskId}
              onComplete={onComplete}
              onEdit={onEdit}
              onDelete={onDelete}
              isCompleting={completingId === task.id}
              isDeleting={deletingId === task.id}
            />
          ))}
        </div>
      )}
    </div>
  )
}
