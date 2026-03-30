import { clsx } from 'clsx'

interface BadgeProps {
  className?: string
  children: React.ReactNode
}

export function Badge({ className, children }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium',
        className
      )}
    >
      {children}
    </span>
  )
}
