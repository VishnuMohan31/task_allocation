import { clsx } from 'clsx'

interface CardProps {
  className?: string
  children: React.ReactNode
}

export function Card({ className, children }: CardProps) {
  return (
    <div
      className={clsx(
        'bg-white rounded-2xl border border-slate-200 shadow-sm',
        className
      )}
    >
      {children}
    </div>
  )
}
