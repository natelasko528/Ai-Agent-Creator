import { create } from 'zustand'

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
    const res = await fetch('http://localhost:8000/agents')
    const agents: Agent[] = await res.json()
    set({ agents })
  },

  createAgent: async (data) => {
    await fetch('http://localhost:8000/agents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    get().loadAgents()
  },

  selectAgent: (a) => set({ selectedAgent: a }),
  setModal: (v) => set({ modal: v }),
}))