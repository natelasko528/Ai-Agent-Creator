import React from 'react'
import { useAgentStore } from '../state/agentStore'

export default function AgentSidebar() {
  const agents = useAgentStore((s) => s.agents)
  const selectAgent = useAgentStore((s) => s.selectAgent)
  const selectedAgent = useAgentStore((s) => s.selectedAgent)
  const setModal = useAgentStore((s) => s.setModal)
  return (
    <aside className="w-64 bg-gray-800 p-4 flex flex-col border-r border-gray-700">
      <button
        onClick={() => setModal(true)}
        className="mb-4 bg-blue-500 hover:bg-blue-600 transition-colors p-2 rounded font-semibold"
      >
        + New Agent
      </button>
      {agents.length === 0 && (
        <p className="text-sm text-gray-400">No agents yet. Create one to start chatting.</p>
      )}
      {agents.map((a) => (
        <button
          key={a.id}
          onClick={() => selectAgent(a)}
          className={`text-left cursor-pointer p-2 rounded mb-2 border border-transparent focus:outline-none focus:ring-2 focus:ring-blue-400 ${
            selectedAgent?.id === a.id ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
          }`}
        >
          <div className="font-medium">{a.name}</div>
          <div className="text-xs text-gray-300">{a.model}</div>
        </button>
      ))}
    </aside>
  )
}