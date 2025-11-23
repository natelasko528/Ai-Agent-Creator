import React, { useState } from 'react'
import { useAgentStore } from '../state/agentStore'

export default function CreateAgentModal() {
  const { modal, setModal, createAgent } = useAgentStore()
const AVAILABLE_TOOLS = [
  { id: 'web_search', label: 'Web search' },
]

export default function CreateAgentModal() {
  const modal = useAgentStore((s) => s.modal)
  const setModal = useAgentStore((s) => s.setModal)
  const createAgent = useAgentStore((s) => s.createAgent)
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
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const toggleTool = (tool: string) => {
    setForm((prev) => ({
      ...prev,
      tools: prev.tools.includes(tool)
        ? prev.tools.filter((t) => t !== tool)
        : [...prev.tools, tool],
    }))
  }

  const submit = async () => {
    if (!form.name.trim()) return
    setSaving(true)
    try {
      await createAgent(form)
      setForm({ name: '', model: 'gpt-4.1-mini', system_prompt: '', tools: [] })
      setError('')
      setModal(false)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create agent'
      setError(message)
    } finally {
      setSaving(false)
    }
  }

  if (!modal) return null
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
      <div className="bg-gray-800 p-6 rounded w-96 shadow-xl">
        <h2 className="text-xl font-semibold mb-4">Create a New Agent</h2>
        <div className="space-y-3">
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Name</label>
            <input
              value={form.name}
              placeholder="Agent Name"
              className="w-full bg-gray-900 p-2 rounded"
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Model</label>
            <select
              value={form.model}
              onChange={(e) => setForm({ ...form, model: e.target.value })}
              className="w-full bg-gray-900 p-2 rounded"
            >
              <option value="gpt-4.1-mini">gpt-4.1-mini</option>
              <option value="gpt-4o-mini">gpt-4o-mini</option>
              <option value="gpt-4.1">gpt-4.1</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">System prompt</label>
            <textarea
              value={form.system_prompt}
              placeholder="Describe how the agent should behave"
              className="w-full bg-gray-900 p-2 h-32 rounded"
              onChange={(e) => setForm({ ...form, system_prompt: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Tools</label>
            <div className="flex flex-col gap-2">
              {AVAILABLE_TOOLS.map((tool) => (
                <label key={tool.id} className="inline-flex items-center gap-2 text-sm text-gray-300">
                  <input
                    type="checkbox"
                    checked={form.tools.includes(tool.id)}
                    onChange={() => toggleTool(tool.id)}
                  />
                  {tool.label}
                </label>
              ))}
            </div>
          </div>
        </div>
        <div className="mt-6 flex gap-2">
          <button
            onClick={() => setModal(false)}
            className="flex-1 bg-gray-700 hover:bg-gray-600 p-2 rounded"
          >
            Cancel
          </button>
          <button
            onClick={submit}
            disabled={saving || !form.name.trim()}
            className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:opacity-40 p-2 rounded"
          >
            {saving ? 'Creating…' : 'Create'}
          </button>
        </div>
      </div>
    </div>
  )
}