import { useState } from 'react'
import { CheckCircle2, Clock, Calendar, Tag, Pencil, Trash2, AlertTriangle } from 'lucide-react'
import { clsx } from 'clsx'
import type { Task } from '../types'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import {
  PRIORITY_LABELS,
  PRIORITY_COLORS,
  PRIORITY_DOT,
  isDeadlineSoon,
  isDeadlineOverdue,
  formatDeadline,
  formatDuration,
} from '../utils/priority'

interface TaskCardProps {
  task: Task
  highlighted?: boolean
  onComplete: (id: string) => void
  onEdit: (task: Task) => void
  onDelete: (id: string) => void
  isCompleting?: boolean
  isDeleting?: boolean
}

export function TaskCard({
  task,
  highlighted,
  onComplete,
  onEdit,
  onDelete,
  isCompleting,
  isDeleting,
}: TaskCardProps) {
  const [confirmDelete, setConfirmDelete] = useState(false)

  const deadlineSoon = isDeadlineSoon(task.deadline)
  const deadlineOverdue = isDeadlineOverdue(task.deadline)

  return (
    <div
      className={clsx(
        'group relative rounded-2xl border p-4 transition-all duration-200',
        task.completed
          ? 'bg-slate-50 border-slate-200 opacity-70'
          : highlighted
          ? 'bg-violet-50 border-violet-300 shadow-md shadow-violet-100'
          : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm'
      )}
    >
      {/* Highlighted ribbon */}
      {highlighted && !task.completed && (
        <div className="absolute -top-px left-4 right-4 h-0.5 rounded-full bg-violet-500" />
      )}

      <div className="flex items-start gap-3">
        {/* Priority dot */}
        <div className="mt-1 shrink-0">
          <span
            className={clsx(
              'block h-2.5 w-2.5 rounded-full',
              PRIORITY_DOT[task.priority]
            )}
          />
        </div>

        {/* Main content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3
              className={clsx(
                'text-sm font-semibold leading-snug',
                task.completed ? 'line-through text-slate-400' : 'text-slate-900'
              )}
            >
              {task.title}
              {highlighted && !task.completed && (
                <span className="ml-2 text-xs font-medium text-violet-600 bg-violet-100 px-1.5 py-0.5 rounded-md">
                  AI Pick
                </span>
              )}
            </h3>

            {/* Actions */}
            <div className="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
              {!task.completed && (
                <button
                  onClick={() => onEdit(task)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                  aria-label="Edit task"
                >
                  <Pencil size={13} />
                </button>
              )}
              {confirmDelete ? (
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => onDelete(task.id)}
                    className="px-2 py-1 text-xs font-medium text-white bg-red-500 rounded-lg hover:bg-red-600 transition-colors"
                    disabled={isDeleting}
                  >
                    {isDeleting ? '...' : 'Yes'}
                  </button>
                  <button
                    onClick={() => setConfirmDelete(false)}
                    className="px-2 py-1 text-xs font-medium text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
                  >
                    No
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmDelete(true)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                  aria-label="Delete task"
                >
                  <Trash2 size={13} />
                </button>
              )}
            </div>
          </div>

          {/* Description */}
          {task.description && (
            <p className="mt-1 text-xs text-slate-500 line-clamp-2">{task.description}</p>
          )}

          {/* Meta row */}
          <div className="mt-2.5 flex flex-wrap items-center gap-2">
            <Badge className={PRIORITY_COLORS[task.priority]}>
              {PRIORITY_LABELS[task.priority]}
            </Badge>

            {task.duration_hours && (
              <span className="inline-flex items-center gap-1 text-xs text-slate-500">
                <Clock size={11} />
                {formatDuration(task.duration_hours)}
              </span>
            )}

            {task.deadline && (
              <span
                className={clsx(
                  'inline-flex items-center gap-1 text-xs font-medium',
                  deadlineOverdue && !task.completed
                    ? 'text-red-600'
                    : deadlineSoon && !task.completed
                    ? 'text-orange-600'
                    : 'text-slate-500'
                )}
              >
                {(deadlineSoon || deadlineOverdue) && !task.completed ? (
                  <AlertTriangle size={11} />
                ) : (
                  <Calendar size={11} />
                )}
                {formatDeadline(task.deadline)}
              </span>
            )}

            {task.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 text-xs text-slate-500"
              >
                <Tag size={10} />
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Complete button */}
      {!task.completed && (
        <div className="mt-3 pt-3 border-t border-slate-100">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onComplete(task.id)}
            loading={isCompleting}
            className="w-full"
          >
            <CheckCircle2 size={14} />
            Mark Complete
          </Button>
        </div>
      )}

      {task.completed && task.completed_at && (
        <p className="mt-2 text-xs text-slate-400">
          Completed {formatDeadline(task.completed_at)}
        </p>
      )}
    </div>
  )
}
