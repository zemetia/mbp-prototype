import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Sparkles } from 'lucide-react'
import { useMBPStore } from '../stores/mbpStore'

export function ChatInterface() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { messages, sendMessage, isLoading, phase } = useMBPStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      sendMessage(input.trim())
      setInput('')
    }
  }

  const getPhaseColor = (p: number) => {
    const colors = [
      'bg-red-100 text-red-700',
      'bg-blue-100 text-blue-700',
      'bg-purple-100 text-purple-700',
      'bg-amber-100 text-amber-700',
      'bg-indigo-100 text-indigo-700',
      'bg-emerald-100 text-emerald-700',
      'bg-slate-100 text-slate-700'
    ]
    return colors[p] || colors[0]
  }

  const getPhaseName = (p: number) => {
    const names = ['Safety', 'Core', 'Adaptive', 'Mining', 'Validation', 'Synthesis', 'Debrief']
    return names[p] || 'Unknown'
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Messages */}
      <div className="h-[60vh] overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12 text-slate-400">
            <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Menunggu koneksi...</p>
          </div>
        )}
        
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-slate-900 text-white'
                  : message.role === 'system'
                  ? 'bg-slate-100 text-slate-700'
                  : 'bg-slate-50 border border-slate-200 text-slate-800'
              }`}
            >
              {message.role === 'system' ? (
                <div className="whitespace-pre-line text-sm">{message.content}</div>
              ) : (
                <>
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  
                  {message.metadata?.tension_target && (
                    <div className="mt-2 pt-2 border-t border-slate-200/50">
                      <span className="text-xs text-slate-500">
                        Tension: {message.metadata.tension_target}
                      </span>
                    </div>
                  )}
                  
                  {message.metadata?.context && (
                    <div className="mt-1">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full ${getPhaseColor(message.phase)}`}>
                        {getPhaseName(message.phase)}
                      </span>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3">
              <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-slate-200 p-4 bg-slate-50">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              phase === 0 ? 'Jawab dengan jujur untuk keselamatanmu...' :
              phase === 6 ? 'Assessment selesai. Terima kasih.' :
              'Ketik responsmu...'
            }
            disabled={isLoading || phase >= 6}
            className="flex-1 px-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-900 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || phase >= 6}
            className="px-4 py-3 bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        <p className="mt-2 text-xs text-slate-500 text-center">
          {phase === 0 && 'Phase 0: Safety Screening — Jawabanmu akan dianalisis untuk keselamatan'}
          {phase === 1 && 'Phase 1: Core Questions — Fixed tension generators'}
          {phase === 2 && 'Phase 2: Adaptive Probing — Hypothesis-driven questioning'}
          {phase === 3 && 'Phase 3: Adaptation Mining — Exploring survival patterns'}
          {phase === 4 && 'Phase 4: Cross-Validation — 12D Matrix tension testing'}
          {phase === 5 && 'Phase 5: Synthesis — Generating structural profile'}
          {phase >= 6 && 'Phase 6: Debriefing — Assessment complete'}
        </p>
      </form>
    </div>
  )
}
