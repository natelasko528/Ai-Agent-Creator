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
  const [selectedAgent, setSelectedAgent] = useState('')
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
      const parsed = (data as Agent[]).map((agent) => ({
        ...agent,
        description: agent.description || 'High-velocity Gemini agent',
        model: agent.model || 'gemini-3.0-pro',
      }))
      setAgents(parsed)
      if (!selectedAgent && parsed.length) {
        setSelectedAgent(parsed[0].name)
      }
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
        if (lastMsg?.role === 'assistant' && lastMsg.agent === activeAgent) {
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
            agent: activeAgent,
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

    const agentName = selectedAgent || agents[0]?.name || 'assistant'

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
          agent: agentName,
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
            agent: agentName,
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
            agent: agentName,
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
  }, [input, isLoading, selectedAgent, sessionId, ws, agents])

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

  const activeAgent = selectedAgent || agents[0]?.name || 'assistant'
  const activeAgentMeta = agents.find((a) => a.name === activeAgent)

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
                className={`w-full text-left p-3 rounded-lg transition-all border ${
                  activeAgent === agent.name
                    ? 'bg-gradient-to-r from-primary-500/20 to-primary-400/10 text-primary-100 border-primary-500/40 shadow-lg shadow-primary-900/40'
                    : 'hover:bg-slate-700/60 text-slate-300 border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-slate-800/80">
                      <Cpu className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold">{agent.name}</p>
                      <p className="text-xs text-slate-400 line-clamp-2">
                        {agent.description}
                      </p>
                    </div>
                  </div>
                  <span className="text-[10px] font-semibold uppercase px-2 py-1 rounded-full bg-slate-900/60 border border-slate-700 text-slate-200">
                    {agent.model}
                  </span>
                </div>
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
        <header className="h-14 border-b border-slate-700 flex items-center justify-between px-4 bg-slate-800/60 backdrop-blur">
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
              <div>
                <p className="text-sm text-slate-300 font-semibold">
                  {activeAgent}
                </p>
                <p className="text-[11px] text-slate-400">
                  {activeAgentMeta?.model || 'gemini'} · {activeAgentMeta?.description || 'Adaptive Gemini agent'}
                </p>
              </div>
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

        {/* Hero banner */}
        <div className="px-4 pt-4">
          <div className="rounded-2xl border border-primary-500/30 bg-gradient-to-r from-primary-500/20 via-slate-800/80 to-slate-900 shadow-xl shadow-primary-900/40 p-4 md:p-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-primary-200">Gemini Control Room</p>
                <h2 className="text-2xl md:text-3xl font-bold mt-1">Multi-agent command deck</h2>
                <p className="text-sm text-slate-300 mt-2 max-w-2xl">
                  Planner (Gemini 3.0 Pro), Executor (Gemini 2.5 Pro), and Research Flash (Gemini 2.5 Flash) collaborate with the full Gemini tool stack for flawless delivery.
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-right text-xs text-slate-200">
                <div className="px-3 py-2 rounded-lg bg-slate-900/50 border border-slate-700">
                  <p className="text-slate-400">Current agent</p>
                  <p className="font-semibold">{activeAgent}</p>
                </div>
                <div className="px-3 py-2 rounded-lg bg-slate-900/50 border border-slate-700">
                  <p className="text-slate-400">Model</p>
                  <p className="font-semibold">{activeAgentMeta?.model || 'gemini'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Agent summary grid */}
        <div className="px-4 mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
          {agents.map((agent) => (
            <div
              key={agent.name}
              className={`rounded-xl border p-3 bg-slate-800/60 backdrop-blur ${
                activeAgent === agent.name
                  ? 'border-primary-500/50 shadow-lg shadow-primary-900/40'
                  : 'border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-slate-900/70">
                    <Layers className="w-4 h-4 text-primary-300" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{agent.name}</p>
                    <p className="text-xs text-slate-400 line-clamp-2">{agent.description}</p>
                  </div>
                </div>
                <span className="text-[10px] px-2 py-1 rounded-full bg-primary-500/20 border border-primary-500/40 text-primary-100">
                  {agent.model}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-3 text-[11px] text-slate-300">
                <Zap className="w-3 h-3" />
                <span>Gemini HEK/AGK toolchain ready</span>
              </div>
            </div>
          ))}
        </div>

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
