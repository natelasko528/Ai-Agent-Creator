import React from 'react'
import { useAgentStore } from '../state/agentStore'

export default function AgentSidebar() {
  const { agents, selectAgent, selectedAgent, setModal } = useAgentStore()
  return (
    <div className="w-64 bg-gray-800 p-4 flex flex-col border-r border-gray-700">
      <button
        data-testid="new-agent-button"
        onClick={() => setModal(true)}
        className="mb-4 bg-blue-500 p-2 rounded"
      >
        + New Agent
      </button>
      {agents.map((a) => (
        <div
          key={a.id}
          onClick={() => selectAgent(a)}
          data-testid={`agent-item-${a.id}`}
          className={`cursor-pointer p-2 rounded mb-2 ${selectedAgent?.id === a.id ? 'bg-blue-600' : 'bg-gray-700'}`}
        >
          {a.name}
        </div>
      ))}
    </div>
  )
}