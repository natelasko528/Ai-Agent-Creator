import React, { useState } from 'react'
import { useAgentStore } from '../state/agentStore'

export default function ChatWindow() {
  const selected = useAgentStore((s) => s.selectedAgent)
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([])
  const [input, setInput] = useState('')

  const send = () => {
    if (!selected || !input) return
    const ws = new WebSocket(`ws://localhost:8000/ws/${selected.id}`)
    ws.onopen = () => ws.send(input)
    let buffer = ''
    ws.onmessage = (e) => {
      buffer += e.data
      setMessages((prev) => [...prev, { role: 'assistant', content: buffer }])
    }
    setMessages((prev) => [...prev, { role: 'user', content: input }])
    setInput('')
  }

  return (
    <div className="flex-1 flex flex-col p-6">
      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-blue-300' : 'text-gray-200'}>
            {m.content}
          </div>
        ))}
      </div>
      <div className="mt-4 flex">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          data-testid="chat-input"
          className="flex-1 bg-gray-800 p-2 rounded"
        />
        <button onClick={send} data-testid="send-message-button" className="ml-2 bg-green-500 p-2 rounded">
          Send
        </button>
      </div>
    </div>
  )
}