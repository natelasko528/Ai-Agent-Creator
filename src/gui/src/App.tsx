import React, { useState, useEffect, useRef, useCallback } from 'react'
import {
  Bot,
  Send,
  Settings,
  Code,
  FileText,
  Terminal,
  Plus,
  X,
  ChevronRight,
  Cpu,
  Zap,
  Layers,
  Play,
  Square,
  RotateCcw,
} from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  agent?: string
}

interface Agent {
  name: string
  description: string
  model: string
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgent, setSelectedAgent] = useState('assistant')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showSettings, setShowSettings] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Fetch agents on mount
  useEffect(() => {
    fetchAgents()
    connectWebSocket()
    return () => ws?.close()
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchAgents = async () => {
    try {
      const res = await fetch('/api/agents')
      const data = await res.json()
      setAgents(data.map((name: string) => ({ name, description: '', model: '' })))
    } catch (err) {
      console.error('Failed to fetch agents:', err)
    }
  }

  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/default`
    const socket = new WebSocket(wsUrl)

    socket.onopen = () => console.log('WebSocket connected')
    socket.onclose = () => setTimeout(connectWebSocket, 3000)
    socket.onerror = (err) => console.error('WebSocket error:', err)
    socket.onmessage = handleWebSocketMessage

    setWs(socket)
  }

  const handleWebSocketMessage = (event: MessageEvent) => {
    const data = JSON.parse(event.data)

    if (data.type === 'event' && data.content) {
      setMessages((prev) => {
        const lastMsg = prev[prev.length - 1]
        if (lastMsg?.role === 'assistant' && lastMsg.agent === selectedAgent) {
          return [
            ...prev.slice(0, -1),
            { ...lastMsg, content: lastMsg.content + data.content },
          ]
        }
        return [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: data.content,
            timestamp: new Date(),
            agent: selectedAgent,
          },
        ]
      })
    }

    if (data.type === 'session') {
      setSessionId(data.session_id)
    }

    if (data.type === 'complete') {
      setIsLoading(false)
    }

    if (data.type === 'error') {
      setIsLoading(false)
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'system',
          content: `Error: ${data.message}`,
          timestamp: new Date(),
        },
      ])
    }
  }

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(
        JSON.stringify({
          type: 'chat',
          agent: selectedAgent,
          message: input,
          session_id: sessionId,
        })
      )
    } else {
      // Fallback to REST API
      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: input,
            agent: selectedAgent,
            session_id: sessionId,
          }),
        })
        const data = await res.json()

        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: data.response,
            timestamp: new Date(),
            agent: selectedAgent,
          },
        ])
        setSessionId(data.session_id)
      } catch (err) {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'system',
            content: 'Failed to send message. Please try again.',
            timestamp: new Date(),
          },
        ])
      }
      setIsLoading(false)
    }
  }, [input, isLoading, selectedAgent, sessionId, ws])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([])
    setSessionId(null)
  }

  return (
    <div className="flex h-screen bg-slate-900">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-72' : 'w-0'
        } bg-slate-800 border-r border-slate-700 transition-all duration-300 overflow-hidden flex flex-col`}
      >
        <div className="p-4 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <Bot className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <h1 className="font-bold text-lg">AI Assistant</h1>
              <p className="text-xs text-slate-400">Gemini ADK Powered</p>
            </div>
          </div>
        </div>

        {/* Agent Selector */}
        <div className="p-4 border-b border-slate-700">
          <h2 className="text-xs font-semibold text-slate-400 uppercase mb-3">
            Agents
          </h2>
          <div className="space-y-2">
            {agents.map((agent) => (
              <button
                key={agent.name}
                onClick={() => setSelectedAgent(agent.name)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                  selectedAgent === agent.name
                    ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                    : 'hover:bg-slate-700 text-slate-300'
                }`}
              >
                <Cpu className="w-4 h-4" />
                <span className="text-sm font-medium">{agent.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tools */}
        <div className="p-4 flex-1">
          <h2 className="text-xs font-semibold text-slate-400 uppercase mb-3">
            Tools
          </h2>
          <div className="space-y-2">
            <button className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-700 text-slate-300 transition-colors">
              <Code className="w-4 h-4" />
              <span className="text-sm">Code Editor</span>
            </button>
            <button className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-700 text-slate-300 transition-colors">
              <Terminal className="w-4 h-4" />
              <span className="text-sm">Terminal</span>
            </button>
            <button className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-700 text-slate-300 transition-colors">
              <FileText className="w-4 h-4" />
              <span className="text-sm">File Browser</span>
            </button>
          </div>
        </div>

        {/* Settings Button */}
        <div className="p-4 border-t border-slate-700">
          <button
            onClick={() => setShowSettings(true)}
            className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-700 text-slate-300 transition-colors"
          >
            <Settings className="w-4 h-4" />
            <span className="text-sm">Settings</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-14 border-b border-slate-700 flex items-center justify-between px-4 bg-slate-800/50">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <ChevronRight
                className={`w-5 h-5 transition-transform ${
                  sidebarOpen ? 'rotate-180' : ''
                }`}
              />
            </button>
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  ws?.readyState === WebSocket.OPEN
                    ? 'bg-green-500'
                    : 'bg-yellow-500'
                }`}
              />
              <span className="text-sm text-slate-400">
                {selectedAgent} agent
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={clearChat}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors text-slate-400 hover:text-slate-200"
              title="Clear chat"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Bot className="w-16 h-16 mb-4 opacity-50" />
              <p className="text-lg font-medium">Start a conversation</p>
              <p className="text-sm">
                Select an agent and send a message to begin
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              } message-enter`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-primary-500 text-white'
                    : msg.role === 'system'
                    ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                    : 'bg-slate-700 text-slate-100'
                }`}
              >
                {msg.role === 'assistant' && (
                  <div className="flex items-center gap-2 mb-1">
                    <Bot className="w-4 h-4 text-primary-400" />
                    <span className="text-xs text-primary-400 font-medium">
                      {msg.agent || 'assistant'}
                    </span>
                  </div>
                )}
                <p className="whitespace-pre-wrap">{msg.content}</p>
                <p className="text-xs opacity-50 mt-1">
                  {msg.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-700 rounded-2xl px-4 py-3">
                <div className="typing-indicator flex gap-1">
                  <span className="w-2 h-2 bg-slate-400 rounded-full" />
                  <span className="w-2 h-2 bg-slate-400 rounded-full" />
                  <span className="w-2 h-2 bg-slate-400 rounded-full" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-slate-700 bg-slate-800/50">
          <div className="flex items-end gap-3 max-w-4xl mx-auto">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                rows={1}
                className="w-full bg-slate-700 border border-slate-600 rounded-xl px-4 py-3 pr-12 text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                style={{ minHeight: '48px', maxHeight: '200px' }}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="p-3 bg-primary-500 hover:bg-primary-600 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-xl transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </main>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-2xl p-6 w-full max-w-md border border-slate-700">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Settings</h2>
              <button
                onClick={() => setShowSettings(false)}
                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  placeholder="Enter your Gemini API key"
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Default Model
                </label>
                <select className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                  <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                </select>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowSettings(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowSettings(false)}
                className="px-4 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg transition-colors"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
