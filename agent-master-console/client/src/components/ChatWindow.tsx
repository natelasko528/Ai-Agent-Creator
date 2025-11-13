import React, { useEffect, useRef, useState } from 'react'
import { WS_BASE_URL } from '../config'
import { useAgentStore } from '../state/agentStore'

type Message = {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatWindow() {
  const selectedAgent = useAgentStore((s) => s.selectedAgent)
  const setModal = useAgentStore((s) => s.setModal)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    setMessages([])
    if (!selectedAgent) {
      if (wsRef.current) {
        wsRef.current.close()
      }
      wsRef.current = null
      setConnected(false)
      return
    }

    const socket = new WebSocket(`${WS_BASE_URL}/ws/${selectedAgent.id}`)
    socket.onopen = () => setConnected(true)
    socket.onclose = () => setConnected(false)
    socket.onerror = () => setConnected(false)
    socket.onmessage = (event) => {
      const chunk = event.data as string
      setMessages((prev) => {
        if (prev.length === 0 || prev[prev.length - 1].role !== 'assistant') {
          return [...prev, { role: 'assistant', content: chunk }]
        }
        const next = [...prev]
        next[next.length - 1] = {
          ...next[next.length - 1],
          content: next[next.length - 1].content + chunk,
        }
        return next
      })
    }
    wsRef.current = socket
    return () => {
      socket.close()
      wsRef.current = null
    }
  }, [selectedAgent])

  const send = () => {
    const text = input.trim()
    if (!selectedAgent || !text || wsRef.current?.readyState !== WebSocket.OPEN) return
    setMessages((prev) => [...prev, { role: 'user', content: text }, { role: 'assistant', content: '' }])
    wsRef.current.send(text)
    setInput('')
  }

  if (!selectedAgent) {
    return (
      <section className="flex-1 flex flex-col items-center justify-center text-center text-gray-300 p-6">
        <p className="mb-4 text-lg">Create an agent to start chatting.</p>
        <button onClick={() => setModal(true)} className="bg-blue-500 px-4 py-2 rounded">
          Create your first agent
        </button>
      </section>
    )
  }

  return (
    <section className="flex-1 flex flex-col p-6">
      <div className="flex items-center justify-between border-b border-gray-700 pb-3 mb-4">
        <div>
          <h2 className="text-xl font-semibold">{selectedAgent.name}</h2>
          <p className="text-sm text-gray-400">Model: {selectedAgent.model}</p>
        </div>
        <span className={`text-sm ${connected ? 'text-green-400' : 'text-red-400'}`}>
          {connected ? 'Connected' : 'Offline'}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto space-y-4 bg-gray-800/40 rounded p-4">
        {messages.length === 0 && (
          <p className="text-gray-500">Send a message to begin the conversation.</p>
        )}
        {messages.map((m, i) => (
          <div
            key={`${m.role}-${i}`}
            className={`whitespace-pre-wrap ${m.role === 'user' ? 'text-blue-300' : 'text-gray-100'}`}
          >
            {m.content}
          </div>
        ))}
      </div>
      <div className="mt-4 flex">
        <input
          value={input}
          disabled={!connected}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              send()
            }
          }}
          className="flex-1 bg-gray-800 p-3 rounded disabled:opacity-50"
          placeholder={connected ? 'Send a message' : 'Connecting...'}
        />
        <button
          onClick={send}
          disabled={!connected || !input.trim()}
          className="ml-2 bg-green-500 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-green-600 px-4 rounded"
        >
          Send
        </button>
      </div>
    </section>
  )
}