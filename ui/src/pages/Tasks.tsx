import { useState } from 'react'
import { Plus } from 'lucide-react'
import {
  useTasks,
  useCreateTask,
  useUpdateTask,
  useCompleteTask,
  useDeleteTask,
} from '../hooks/useTasks'
import { TaskList } from '../components/TaskList'
import { TaskForm } from '../components/TaskForm'
import { Modal } from '../components/ui/Modal'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import { useToast } from '../components/ui/Toast'
import type { Task, TaskCreate } from '../types'

export function Tasks() {
  const { toast } = useToast()
  const { data: tasks = [], isLoading } = useTasks()

  const createTask = useCreateTask()
  const updateTask = useUpdateTask()
  const completeTask = useCompleteTask()
  const deleteTask = useDeleteTask()

  const [createOpen, setCreateOpen] = useState(false)
  const [editTask, setEditTask] = useState<Task | null>(null)
  const [completingId, setCompletingId] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleCreate = (data: TaskCreate) => {
    createTask.mutate(data, {
      onSuccess: () => {
        toast('Task created')
        setCreateOpen(false)
      },
      onError: (err) => toast(err.message, 'error'),
    })
  }

  const handleUpdate = (data: TaskCreate) => {
    if (!editTask) return
    updateTask.mutate(
      { id: editTask.id, payload: data },
      {
        onSuccess: () => {
          toast('Task updated')
          setEditTask(null)
        },
        onError: (err) => toast(err.message, 'error'),
      }
    )
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Tasks</h1>
          <p className="text-sm text-slate-500 mt-0.5">Manage all your tasks</p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus size={16} />
          New Task
        </Button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-24">
          <Spinner size="lg" />
        </div>
      ) : (
        <TaskList
          tasks={tasks}
          onComplete={handleComplete}
          onEdit={setEditTask}
          onDelete={handleDelete}
          completingId={completingId}
          deletingId={deletingId}
        />
      )}

      {/* Create modal */}
      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="New Task">
        <TaskForm
          onSubmit={handleCreate}
          isLoading={createTask.isPending}
          submitLabel="Create Task"
        />
      </Modal>

      {/* Edit modal */}
      <Modal open={!!editTask} onClose={() => setEditTask(null)} title="Edit Task">
        {editTask && (
          <TaskForm
            defaultValues={editTask}
            onSubmit={handleUpdate}
            isLoading={updateTask.isPending}
            submitLabel="Update Task"
          />
        )}
      </Modal>
    </div>
  )
}
