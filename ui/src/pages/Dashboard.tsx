import { useState } from 'react'
import { Plus } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import { useTasks, useCreateTask, useCompleteTask, useDeleteTask } from '../hooks/useTasks'
import { useAgentDecision, AGENT_KEY } from '../hooks/useAgent'
import { AgentPanel } from '../components/AgentPanel'
import { StatsBar } from '../components/StatsBar'
import { TaskList } from '../components/TaskList'
import { TaskForm } from '../components/TaskForm'
import { Modal } from '../components/ui/Modal'
import { Button } from '../components/ui/Button'
import { useToast } from '../components/ui/Toast'
import type { Task, TaskCreate } from '../types'

export function Dashboard() {
  const { toast } = useToast()
  const qc = useQueryClient()

  const { data: tasks = [], isLoading: tasksLoading } = useTasks()
  const [agentEnabled, setAgentEnabled] = useState(false)
  const { data: decision, isLoading: agentLoading, isFetching: agentFetching } =
    useAgentDecision(agentEnabled)

  const createTask = useCreateTask()
  const completeTask = useCompleteTask()
  const deleteTask = useDeleteTask()

  const [createOpen, setCreateOpen] = useState(false)
  const [editTask, setEditTask] = useState<Task | null>(null)
  const [completingId, setCompletingId] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleAskAgent = () => {
    if (agentEnabled) {
      qc.invalidateQueries({ queryKey: AGENT_KEY })
    } else {
      setAgentEnabled(true)
    }
  }

  const handleCreate = (data: TaskCreate) => {
    createTask.mutate(data, {
      onSuccess: () => {
        toast('Task created successfully')
        setCreateOpen(false)
      },
      onError: (err) => toast(err.message, 'error'),
    })
  }

  const handleComplete = (id: string) => {
    setCompletingId(id)
    completeTask.mutate(id, {
      onSuccess: () => toast('Task marked complete'),
      onError: (err) => toast(err.message, 'error'),
      onSettled: () => setCompletingId(null),
    })
  }

  const handleDelete = (id: string) => {
    setDeletingId(id)
    deleteTask.mutate(id, {
      onSuccess: () => toast('Task deleted'),
      onError: (err) => toast(err.message, 'error'),
      onSettled: () => setDeletingId(null),
    })
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5">Your productivity overview</p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus size={16} />
          New Task
        </Button>
      </div>

      {/* Stats */}
      {!tasksLoading && <StatsBar tasks={tasks} />}

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent panel — left column */}
        <div className="lg:col-span-1">
          <AgentPanel
            decision={decision}
            isLoading={agentLoading}
            isFetching={agentFetching}
            onAsk={handleAskAgent}
            hasAsked={agentEnabled}
          />
        </div>

        {/* Task list — right columns */}
        <div className="lg:col-span-2">
          {tasksLoading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-pulse text-slate-400 text-sm">Loading tasks...</div>
            </div>
          ) : (
            <TaskList
              tasks={tasks}
              highlightedTaskId={decision?.next_task?.id}
              onComplete={handleComplete}
              onEdit={setEditTask}
              onDelete={handleDelete}
              completingId={completingId}
              deletingId={deletingId}
            />
          )}
        </div>
      </div>

      {/* Create modal */}
      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="New Task">
        <TaskForm
          onSubmit={handleCreate}
          isLoading={createTask.isPending}
          submitLabel="Create Task"
        />
      </Modal>

      {/* Edit modal */}
      <Modal
        open={!!editTask}
        onClose={() => setEditTask(null)}
        title="Edit Task"
      >
        {editTask && (
          <TaskForm
            defaultValues={editTask}
            onSubmit={(data) => {
              createTask.mutate(data, {
                onSuccess: () => {
                  toast('Task updated')
                  setEditTask(null)
                },
                onError: (err) => toast(err.message, 'error'),
              })
            }}
            isLoading={createTask.isPending}
            submitLabel="Update Task"
          />
        )}
      </Modal>
    </div>
  )
}
