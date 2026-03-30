import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import type { Task, TaskCreate } from '../types'
import { Button } from './ui/Button'

interface TaskFormProps {
  defaultValues?: Partial<Task>
  onSubmit: (data: TaskCreate) => void
  isLoading?: boolean
  submitLabel?: string
}

interface FormValues {
  title: string
  description: string
  priority: number
  tags: string
  duration_hours: string
  deadline: string
}

export function TaskForm({
  defaultValues,
  onSubmit,
  isLoading,
  submitLabel = 'Save Task',
}: TaskFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormValues>({
    defaultValues: {
      title: defaultValues?.title ?? '',
      description: defaultValues?.description ?? '',
      priority: defaultValues?.priority ?? 3,
      tags: defaultValues?.tags?.join(', ') ?? '',
      duration_hours: defaultValues?.duration_hours?.toString() ?? '',
      deadline: defaultValues?.deadline
        ? new Date(defaultValues.deadline).toISOString().slice(0, 16)
        : '',
    },
  })

  useEffect(() => {
    reset({
      title: defaultValues?.title ?? '',
      description: defaultValues?.description ?? '',
      priority: defaultValues?.priority ?? 3,
      tags: defaultValues?.tags?.join(', ') ?? '',
      duration_hours: defaultValues?.duration_hours?.toString() ?? '',
      deadline: defaultValues?.deadline
        ? new Date(defaultValues.deadline).toISOString().slice(0, 16)
        : '',
    })
  }, [defaultValues, reset])

  const submit = (values: FormValues) => {
    const tags = values.tags
      ? values.tags.split(',').map((t) => t.trim()).filter(Boolean)
      : []
    const duration_hours = values.duration_hours
      ? parseFloat(values.duration_hours)
      : null
    const deadline = values.deadline
      ? new Date(values.deadline).toISOString()
      : null

    onSubmit({
      title: values.title,
      description: values.description,
      priority: Number(values.priority),
      tags,
      duration_hours,
      deadline,
    })
  }

  const inputClass =
    'w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition'

  const labelClass = 'block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wide'

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-4" noValidate>
      {/* Title */}
      <div>
        <label className={labelClass} htmlFor="title">Title *</label>
        <input
          id="title"
          className={inputClass}
          placeholder="What needs to be done?"
          {...register('title', { required: 'Title is required', maxLength: { value: 200, message: 'Max 200 characters' } })}
        />
        {errors.title && (
          <p className="mt-1 text-xs text-red-500">{errors.title.message}</p>
        )}
      </div>

      {/* Description */}
      <div>
        <label className={labelClass} htmlFor="description">Description</label>
        <textarea
          id="description"
          rows={3}
          className={inputClass}
          placeholder="Optional details..."
          {...register('description')}
        />
      </div>

      {/* Priority */}
      <div>
        <label className={labelClass} htmlFor="priority">Priority *</label>
        <select
          id="priority"
          className={inputClass}
          {...register('priority', { required: true })}
        >
          <option value={1}>1 — Lowest</option>
          <option value={2}>2 — Low</option>
          <option value={3}>3 — Medium</option>
          <option value={4}>4 — High</option>
          <option value={5}>5 — Critical</option>
        </select>
      </div>

      {/* Duration + Deadline side by side */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass} htmlFor="duration_hours">Duration (hours)</label>
          <input
            id="duration_hours"
            type="number"
            step="0.25"
            min="0.25"
            className={inputClass}
            placeholder="e.g. 1.5"
            {...register('duration_hours', {
              min: { value: 0.25, message: 'Min 0.25h (15 min)' },
            })}
          />
          {errors.duration_hours && (
            <p className="mt-1 text-xs text-red-500">{errors.duration_hours.message}</p>
          )}
        </div>
        <div>
          <label className={labelClass} htmlFor="deadline">Deadline</label>
          <input
            id="deadline"
            type="datetime-local"
            className={inputClass}
            {...register('deadline')}
          />
        </div>
      </div>

      {/* Tags */}
      <div>
        <label className={labelClass} htmlFor="tags">Tags</label>
        <input
          id="tags"
          className={inputClass}
          placeholder="work, urgent, design (comma separated)"
          {...register('tags')}
        />
      </div>

      <Button type="submit" loading={isLoading} className="w-full mt-2" size="lg">
        {submitLabel}
      </Button>
    </form>
  )
}
