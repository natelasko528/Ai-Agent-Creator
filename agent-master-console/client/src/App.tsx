import React, { useEffect } from 'react'
import AgentSidebar from './components/AgentSidebar'
import ChatWindow from './components/ChatWindow'
import CreateAgentModal from './components/CreateAgentModal'
import { useAgentStore } from './state/agentStore'

export default function App() {
  const load = useAgentStore((s) => s.loadAgents)
  useEffect(() => {
    load()
  }, [])

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <CreateAgentModal />
      <AgentSidebar />
      <ChatWindow />
    </div>
  )
}