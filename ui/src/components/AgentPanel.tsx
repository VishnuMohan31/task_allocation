import { Brain, RefreshCw, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import { RadialBarChart, RadialBar, PolarAngleAxis } from 'recharts'
import type { AgentDecision } from '../types'
import { Button } from './ui/Button'
import { Card } from './ui/Card'
import { Spinner } from './ui/Spinner'
import { PRIORITY_COLORS, PRIORITY_LABELS } from '../utils/priority'
import { Badge } from './ui/Badge'

interface AgentPanelProps {
  decision: AgentDecision | undefined
  isLoading: boolean
  isFetching: boolean
  onAsk: () => void
  hasAsked: boolean
}

function ScoreGauge({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const data = [{ value: pct }]

  const color =
    pct >= 75 ? '#22c55e' : pct >= 40 ? '#f59e0b' : '#ef4444'

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <RadialBarChart
          width={120}
          height={120}
          cx={60}
          cy={60}
          innerRadius={42}
          outerRadius={56}
          barSize={12}
          data={data}
          startAngle={90}
          endAngle={-270}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar
            background={{ fill: '#f1f5f9' }}
            dataKey="value"
            cornerRadius={6}
            fill={color}
          />
        </RadialBarChart>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold text-slate-900">{pct}%</span>
        </div>
      </div>
      <span className="text-xs text-slate-500 mt-1">Productivity</span>
    </div>
  )
}

export function AgentPanel({ decision, isLoading, isFetching, onAsk, hasAsked }: AgentPanelProps) {
  const [showReasoning, setShowReasoning] = useState(false)

  return (
    <Card className="overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-gradient-to-r from-violet-50 to-white">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-violet-100 rounded-xl">
            <Brain size={18} className="text-violet-600" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-900">AI Agent</h2>
            <p className="text-xs text-slate-500">Powered by GPT-4o-mini</p>
          </div>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={onAsk}
          loading={isLoading || isFetching}
          disabled={isLoading || isFetching}
        >
          <RefreshCw size={13} />
          {hasAsked ? 'Refresh' : 'Ask Agent'}
        </Button>
      </div>

      {/* Body */}
      <div className="p-5">
        {!hasAsked && !isLoading && (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="p-4 bg-violet-50 rounded-2xl mb-3">
              <Brain size={28} className="text-violet-400" />
            </div>
            <p className="text-sm font-medium text-slate-700">Ready to analyse your tasks</p>
            <p className="text-xs text-slate-400 mt-1">
              Click "Ask Agent" to get your next recommended task
            </p>
          </div>
        )}

        {(isLoading || isFetching) && (
          <div className="flex flex-col items-center justify-center py-8 gap-3">
            <Spinner size="lg" />
            <p className="text-sm text-slate-500">Analysing your tasks...</p>
            <p className="text-xs text-slate-400">This may take a few seconds</p>
          </div>
        )}

        {decision && !isLoading && !isFetching && (
          <div className="space-y-4">
            {/* Score + suggestion row */}
            <div className="flex items-center gap-5">
              <ScoreGauge score={decision.productivity_score} />
              <div className="flex-1">
                <div className="flex items-start gap-2">
                  <Lightbulb size={15} className="text-amber-500 mt-0.5 shrink-0" />
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {decision.suggestion}
                  </p>
                </div>
              </div>
            </div>

            {/* Recommended task */}
            {decision.next_task ? (
              <div className="rounded-xl border border-violet-200 bg-violet-50 p-4">
                <p className="text-xs font-semibold text-violet-600 uppercase tracking-wide mb-2">
                  Recommended Next Task
                </p>
                <p className="text-sm font-semibold text-slate-900">
                  {decision.next_task.title}
                </p>
                {decision.next_task.description && (
                  <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                    {decision.next_task.description}
                  </p>
                )}
                <div className="mt-2 flex flex-wrap gap-2">
                  <Badge className={PRIORITY_COLORS[decision.next_task.priority]}>
                    {PRIORITY_LABELS[decision.next_task.priority]}
                  </Badge>
                  {decision.next_task.duration_hours && (
                    <Badge className="bg-slate-100 text-slate-600">
                      {decision.next_task.duration_hours}h
                    </Badge>
                  )}
                </div>
              </div>
            ) : (
              <div className="rounded-xl border border-green-200 bg-green-50 p-4 text-center">
                <p className="text-sm font-semibold text-green-700">All tasks complete!</p>
                <p className="text-xs text-green-600 mt-0.5">Great work. Nothing pending.</p>
              </div>
            )}

            {/* Reasoning toggle */}
            {decision.reasoning && (
              <div>
                <button
                  onClick={() => setShowReasoning((v) => !v)}
                  className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 transition-colors"
                >
                  {showReasoning ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                  {showReasoning ? 'Hide reasoning' : 'Show reasoning'}
                </button>
                {showReasoning && (
                  <div className="mt-2 rounded-xl bg-slate-50 border border-slate-200 p-3">
                    <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-wrap">
                      {decision.reasoning}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  )
}
