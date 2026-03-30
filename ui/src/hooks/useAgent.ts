import { useQuery } from '@tanstack/react-query'
import { agentApi } from '../api/agent'

export const AGENT_KEY = ['agent-decision'] as const

export function useAgentDecision(enabled = false) {
  return useQuery({
    queryKey: AGENT_KEY,
    queryFn: agentApi.getDecision,
    enabled,
    staleTime: Infinity,
    retry: 1,
  })
}
