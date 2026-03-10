import { Brain, Sparkles, Loader2 } from 'lucide-react'

interface PhaseTransitionProps {
  fromPhase: string
  toPhase: string
  progress?: number
}

export function PhaseTransition({ fromPhase, toPhase, progress = 0 }: PhaseTransitionProps) {
  const getPhaseName = (phase: string) => {
    const names: Record<string, string> = {
      'safety': 'Keamanan & Konteks',
      'core': 'Pertanyaan Inti',
      'adaptive': 'Probing Adaptif',
      'mining': 'Pola Adaptasi',
      'validation': 'Validasi Silang',
      'synthesis': 'Sintesis Struktural',
      'closure': 'Debriefing & Penutup'
    }
    return names[phase.toLowerCase()] || phase
  }

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="max-w-md w-full mx-auto text-center p-8">
        {/* Animated Icon */}
        <div className="relative w-24 h-24 mx-auto mb-8">
          <div className="absolute inset-0 bg-slate-200 rounded-full animate-ping opacity-20" />
          <div className="absolute inset-2 bg-slate-100 rounded-full animate-pulse" />
          <div className="absolute inset-0 flex items-center justify-center">
            <Brain className="w-10 h-10 text-slate-700 animate-pulse" />
          </div>
          <div className="absolute -top-1 -right-1">
            <Sparkles className="w-6 h-6 text-amber-400 animate-pulse" />
          </div>
          <div className="absolute -bottom-1 -left-1">
            <Sparkles className="w-5 h-5 text-slate-400 animate-pulse delay-150" />
          </div>
        </div>

        {/* Text Content */}
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">
          AI Sedang Menganalisis
        </h2>
        <p className="text-slate-600 mb-6">
          Mempersiapkan pertanyaan untuk fase berikutnya berdasarkan jawaban Anda...
        </p>

        {/* Phase Indicator */}
        <div className="bg-slate-50 rounded-xl p-4 mb-6">
          <div className="flex items-center justify-center gap-3 text-sm">
            <span className="text-slate-500 line-through">
              {getPhaseName(fromPhase)}
            </span>
            <Loader2 className="w-4 h-4 text-slate-400 animate-spin" />
            <span className="text-slate-900 font-medium">
              {getPhaseName(toPhase)}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="relative h-2 bg-slate-200 rounded-full overflow-hidden">
          <div 
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-slate-700 to-slate-900 rounded-full transition-all duration-500"
            style={{ 
              width: `${Math.max(15, progress)}%`,
              animation: 'shimmer 2s infinite'
            }}
          />
        </div>
        <p className="text-xs text-slate-400 mt-3">
          Proses ini memerlukan waktu beberapa detik
        </p>
      </div>
    </div>
  )
}
