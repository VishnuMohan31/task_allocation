import client from './client'
import type { Task, TaskCreate, TaskUpdate } from '../types'

export const tasksApi = {
  list: async (): Promise<Task[]> => {
    const { data } = await client.get<Task[]>('/tasks/')
    return data
  },

  get: async (id: string): Promise<Task> => {
    const { data } = await client.get<Task>(`/tasks/${id}`)
    return data
  },

  create: async (payload: TaskCreate): Promise<Task> => {
    const { data } = await client.post<Task>('/tasks/', payload)
    return data
  },

  update: async (id: string, payload: TaskUpdate): Promise<Task> => {
    const { data } = await client.patch<Task>(`/tasks/${id}`, payload)
    return data
  },

  complete: async (id: string): Promise<Task> => {
    const { data } = await client.post<Task>(`/tasks/${id}/complete`)
    return data
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/tasks/${id}`)
  },
}
