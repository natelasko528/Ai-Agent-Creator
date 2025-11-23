import { create } from 'zustand'
import { API_BASE_URL } from '../config'

interface Agent {
  id: string
  name: string
  model: string
  system_prompt: string
  tools: string[]
}

interface AgentState {
  agents: Agent[]
  selectedAgent: Agent | null
  modal: boolean
  loadAgents: () => Promise<void>
  createAgent: (data: Partial<Agent>) => Promise<void>
  selectAgent: (a: Agent) => void
  setModal: (v: boolean) => void
}

export const useAgentStore = create<AgentState>((set, get) => ({
  agents: [],
  selectedAgent: null,
  modal: false,

  loadAgents: async () => {
    const res = await fetch(`${API_BASE_URL}/agents`)
    const agents: Agent[] = await res.json()
    set((state) => ({
      agents,
      selectedAgent:
        state.selectedAgent && agents.some((a) => a.id === state.selectedAgent?.id)
          ? agents.find((a) => a.id === state.selectedAgent?.id) ?? null
          : agents[0] ?? null,
    }))
  },

  createAgent: async (data) => {
    const res = await fetch(`${API_BASE_URL}/agents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const payload = await res.json().catch(() => ({}))
      const detail = (payload as { detail?: string }).detail
      throw new Error(detail || 'Failed to create agent')
    }
    const created: Agent = await res.json()
    set((state) => ({
      agents: [...state.agents, created],
      selectedAgent: created,
    }))
  },

  selectAgent: (a) => set({ selectedAgent: a }),
  setModal: (v) => set({ modal: v }),
}))