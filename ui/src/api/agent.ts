import client from './client'
import type { AgentDecision } from '../types'

export const agentApi = {
  getDecision: async (): Promise<AgentDecision> => {
    const { data } = await client.get<AgentDecision>('/agent/decision')
    return data
  },
}
