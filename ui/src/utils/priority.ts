export const PRIORITY_LABELS: Record<number, string> = {
  1: 'Lowest',
  2: 'Low',
  3: 'Medium',
  4: 'High',
  5: 'Critical',
}

export const PRIORITY_COLORS: Record<number, string> = {
  1: 'bg-slate-100 text-slate-600',
  2: 'bg-blue-100 text-blue-700',
  3: 'bg-yellow-100 text-yellow-700',
  4: 'bg-orange-100 text-orange-700',
  5: 'bg-red-100 text-red-700',
}

export const PRIORITY_DOT: Record<number, string> = {
  1: 'bg-slate-400',
  2: 'bg-blue-500',
  3: 'bg-yellow-500',
  4: 'bg-orange-500',
  5: 'bg-red-500',
}

export function isDeadlineSoon(deadline: string | null): boolean {
  if (!deadline) return false
  const diff = new Date(deadline).getTime() - Date.now()
  return diff > 0 && diff < 24 * 60 * 60 * 1000
}

export function isDeadlineOverdue(deadline: string | null): boolean {
  if (!deadline) return false
  return new Date(deadline).getTime() < Date.now()
}

export function formatDeadline(deadline: string): string {
  return new Date(deadline).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDuration(hours: number): string {
  if (hours < 1) return `${Math.round(hours * 60)}m`
  if (hours === 1) return '1h'
  return `${hours}h`
}
