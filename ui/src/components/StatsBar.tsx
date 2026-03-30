import { ListTodo, CheckCircle2, Clock } from 'lucide-react'
import type { Task } from '../types'

interface StatsBarProps {
  tasks: Task[]
}

export function StatsBar({ tasks }: StatsBarProps) {
  const total = tasks.length
  const completed = tasks.filter((t) => t.completed).length
  const pending = total - completed

  const stats = [
    {
      label: 'Total Tasks',
      value: total,
      icon: ListTodo,
      color: 'text-slate-600',
      bg: 'bg-slate-100',
    },
    {
      label: 'Pending',
      value: pending,
      icon: Clock,
      color: 'text-orange-600',
      bg: 'bg-orange-100',
    },
    {
      label: 'Completed',
      value: completed,
      icon: CheckCircle2,
      color: 'text-green-600',
      bg: 'bg-green-100',
    },
  ]

  return (
    <div className="grid grid-cols-3 gap-3">
      {stats.map(({ label, value, icon: Icon, color, bg }) => (
        <div
          key={label}
          className="bg-white rounded-2xl border border-slate-200 p-4 flex items-center gap-3"
        >
          <div className={`p-2.5 rounded-xl ${bg}`}>
            <Icon size={18} className={color} />
          </div>
          <div>
            <p className="text-xl font-bold text-slate-900">{value}</p>
            <p className="text-xs text-slate-500">{label}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
