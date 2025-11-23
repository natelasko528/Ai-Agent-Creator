import React, { useState } from 'react'
import { useAgentStore } from '../state/agentStore'

export default function CreateAgentModal() {
  const { modal, setModal, createAgent } = useAgentStore()
  const [form, setForm] = useState({
    name: '',
    model: 'gpt-4.1-mini',
    system_prompt: '',
    tools: [] as string[],
  })

  if (!modal) return null
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-gray-800 p-6 rounded w-96">
        <h2 className="text-xl mb-4">Create a New Agent</h2>
        <input
          placeholder="Agent Name"
          className="w-full bg-gray-900 p-2 mb-2"
          data-testid="agent-name-input"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <textarea
          placeholder="System Prompt"
          className="w-full bg-gray-900 p-2 h-32 mb-2"
          data-testid="agent-prompt-input"
          value={form.system_prompt}
          onChange={(e) => setForm({ ...form, system_prompt: e.target.value })}
        />
        <button
          onClick={() => {
            createAgent(form)
            setModal(false)
          }}
          data-testid="create-agent-button"
          className="w-full bg-blue-500 p-2 rounded"
        >
          Create
        </button>
      </div>
    </div>
  )
}