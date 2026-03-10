import { useState } from 'react'
import { ChevronRight, ChevronLeft, Info } from 'lucide-react'
import type { Question } from '../types'

interface QuestionCardProps {
  question: Question
  onSubmit: (answer: string) => void
  onPrevious?: () => void
  isLoading?: boolean
  canGoBack?: boolean
  currentNumber: number
  totalInPhase: number
}

export function QuestionCard({
  question,
  onSubmit,
  onPrevious,
  isLoading = false,
  canGoBack = false,
  currentNumber,
  totalInPhase
}: QuestionCardProps) {
  const [answer, setAnswer] = useState('')
  const [showDimensions, setShowDimensions] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (answer.trim() && !isLoading) {
      onSubmit(answer.trim())
      setAnswer('')
    }
  }

  const getPhaseLabel = (phase: string) => {
    const labels: Record<string, string> = {
      'safety': 'Fase 0: Keamanan',
      'core': 'Fase 1: Inti',
      'adaptive': 'Fase 2: Adaptif',
      'mining': 'Fase 3: Eksplorasi',
      'validation': 'Fase 4: Validasi',
      'synthesis': 'Fase 5: Sintesis',
      'closure': 'Fase 6: Penutup'
    }
    return labels[phase.toLowerCase()] || phase
  }

  const getDimensionLabel = (dim: string) => {
    const labels: Record<string, string> = {
      'CFV': 'Core Fear Vector',
      'CRF': 'Core Response Fabric',
      'ASC': 'Adaptive Self-Concept',
      'COI': 'Control Orientation Index',
      'CDI': 'Conflict Dynamics Index',
      'RSI': 'Relational Strategy Index',
      'ARP': 'Authority Response Pattern',
      'EG': 'Emotional Granularity',
      'VB': 'Vulnerability Bandwidth',
      'AB': 'Authenticity Baseline',
      'SR': 'Stress Response',
      'ES': 'Emotional Structure'
    }
    return labels[dim] || dim
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="bg-slate-50 border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
              {getPhaseLabel(question.phase)}
            </span>
            <p className="text-sm text-slate-600 mt-1">
              Pertanyaan {currentNumber} dari {totalInPhase}
            </p>
          </div>
          <button
            onClick={() => setShowDimensions(!showDimensions)}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600 transition"
          >
            <Info size={14} />
            <span className="hidden sm:inline">
              {showDimensions ? 'Sembunyikan dimensi' : 'Lihat dimensi'}
            </span>
          </button>
        </div>
      </div>

      {/* Question Text */}
      <div className="p-6 sm:p-8">
        <h2 className="text-xl sm:text-2xl text-slate-800 leading-relaxed font-light">
          {question.text}
        </h2>

        {/* Dimensions (collapsible) */}
        {showDimensions && question.dimensions.length > 0 && (
          <div className="mt-6 p-4 bg-slate-50 rounded-xl border border-slate-100">
            <p className="text-xs text-slate-500 mb-2">Dimensi yang dieksplorasi:</p>
            <div className="flex flex-wrap gap-2">
              {question.dimensions.map((dim) => (
                <span
                  key={dim}
                  className="text-xs px-3 py-1.5 bg-white border border-slate-200 rounded-full text-slate-600"
                  title={getDimensionLabel(dim)}
                >
                  {dim}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Answer Input */}
      <form onSubmit={handleSubmit} className="border-t border-slate-200 p-6">
        <div className="space-y-4">
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Ketik jawabanmu di sini..."
            rows={4}
            disabled={isLoading}
            className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-900 focus:bg-white disabled:opacity-50 disabled:cursor-not-allowed resize-none transition"
          />
          
          <div className="flex items-center justify-between gap-4">
            {canGoBack && onPrevious ? (
              <button
                type="button"
                onClick={onPrevious}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-3 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition disabled:opacity-50"
              >
                <ChevronLeft size={18} />
                <span className="hidden sm:inline">Sebelumnya</span>
              </button>
            ) : (
              <div />
            )}
            
            <button
              type="submit"
              disabled={isLoading || !answer.trim()}
              className="flex items-center gap-2 px-6 py-3 bg-slate-900 text-white rounded-xl font-medium hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Mengirim...
                </>
              ) : (
                <>
                  Lanjut
                  <ChevronRight size={18} />
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
