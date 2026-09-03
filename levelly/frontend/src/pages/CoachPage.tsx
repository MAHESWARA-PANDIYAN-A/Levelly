import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { ArrowLeft, Send, MessageCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { coachAPI } from '../lib/api'
import { useAuthStore } from '../store/authStore'
import { v4 as uuidv4 } from 'uuid'

interface Message {
  id: string
  role: 'user' | 'coach'
  text: string
  time: Date
}

const STARTER_QUESTIONS = [
  "Why did my credit recommendation change?",
  "How does Save-at-Pay work?",
  "My income dropped this week — what should I do?",
  "When will investment options open for me?",
]

export default function CoachPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [sessionId] = useState(() => uuidv4())
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'coach',
      text: `Hi ${user?.full_name?.split(' ')[0] || 'there'}! I'm Levelly Coach. I can help you understand your financial situation, explain how your Safety Wallet works, and guide you through this period. What would you like to know?`,
      time: new Date(),
    }
  ])
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  const sendMutation = useMutation({
    mutationFn: (message: string) => coachAPI.sendMessage(message, sessionId),
    onSuccess: (res) => {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString() + '-coach',
          role: 'coach',
          text: res.data.response,
          time: new Date(),
        }
      ])
    },
    onError: () => {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString() + '-coach',
          role: 'coach',
          text: "I'm having trouble connecting right now. Please try again in a moment.",
          time: new Date(),
        }
      ])
    }
  })

  const handleSend = (text?: string) => {
    const message = text || input.trim()
    if (!message || sendMutation.isPending) return

    setMessages(prev => [
      ...prev,
      { id: Date.now().toString(), role: 'user', text: message, time: new Date() }
    ])
    setInput('')
    sendMutation.mutate(message)
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex flex-col h-dvh bg-levelly-bg">
      {/* Header */}
      <div className="px-5 pt-12 pb-4 bg-levelly-bg border-b border-gray-100 flex-shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-gray-500 p-1">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 bg-emerald-600 rounded-full flex items-center justify-center">
              <MessageCircle className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-bold text-gray-900">Levelly Coach</p>
              <p className="text-xs text-gray-400">Your financial guide</p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
              msg.role === 'user'
                ? 'bg-emerald-600 text-white rounded-br-sm'
                : 'bg-white text-gray-800 shadow-card rounded-bl-sm'
            }`}>
              <p className="text-sm leading-relaxed">{msg.text}</p>
              <p className={`text-[10px] mt-1.5 ${msg.role === 'user' ? 'text-emerald-200' : 'text-gray-400'}`}>
                {msg.time.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}

        {sendMutation.isPending && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-card">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        {/* Starter questions */}
        {messages.length === 1 && (
          <div className="space-y-2">
            <p className="text-xs text-gray-400 text-center">Common questions</p>
            {STARTER_QUESTIONS.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSend(q)}
                className="w-full text-left p-3 bg-white rounded-xl text-sm text-gray-700 shadow-card hover:bg-emerald-50 hover:text-emerald-700 transition-all"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-5 py-3 bg-white border-t border-gray-100 flex-shrink-0 pb-safe">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder="Ask Levelly Coach..."
            className="flex-1 input-field resize-none min-h-[44px] max-h-[120px]"
            rows={1}
          />
          <button
            id="btn-coach-send"
            onClick={() => handleSend()}
            disabled={!input.trim() || sendMutation.isPending}
            className="w-11 h-11 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-200 rounded-xl flex items-center justify-center flex-shrink-0 transition-all"
          >
            <Send className="w-4 h-4 text-white" />
          </button>
        </div>
        <p className="text-[10px] text-gray-400 text-center mt-2">
          Levelly Coach provides general financial guidance, not regulated advice.
        </p>
      </div>
    </div>
  )
}
