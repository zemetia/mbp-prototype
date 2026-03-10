import { Shield, Brain, Search, Hammer, GitCompare, FileText, CheckCircle } from 'lucide-react'

const phases = [
  { num: 0, name: 'Safety', icon: Shield },
  { num: 1, name: 'Core', icon: Brain },
  { num: 2, name: 'Adaptive', icon: Search },
  { num: 3, name: 'Mining', icon: Hammer },
  { num: 4, name: 'Validation', icon: GitCompare },
  { num: 5, name: 'Synthesis', icon: FileText },
  { num: 6, name: 'Closure', icon: CheckCircle },
]

interface ProgressBarProps {
  currentPhase: number
  compact?: boolean
}

export function ProgressBar({ currentPhase, compact = false }: ProgressBarProps) {
  if (compact) {
    return (
      <div className="flex items-center justify-center gap-1">
        {phases.map((phase) => {
          const isActive = phase.num === currentPhase
          const isCompleted = phase.num < currentPhase
          
          return (
            <div
              key={phase.num}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                isActive ? 'bg-slate-900 w-4' :
                isCompleted ? 'bg-emerald-500' : 'bg-slate-200'
              }`}
              title={`Phase ${phase.num}: ${phase.name}`}
            />
          )
        })}
      </div>
    )
  }

  return (
    <div className="bg-white border-b border-slate-200">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {phases.map((phase, index) => {
            const Icon = phase.icon
            const isActive = phase.num === currentPhase
            const isCompleted = phase.num < currentPhase
            
            return (
              <div key={phase.num} className="flex items-center">
                <div className={`flex flex-col items-center gap-2 ${
                  isActive ? 'text-slate-900' : 
                  isCompleted ? 'text-emerald-600' : 'text-slate-400'
                }`}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${
                    isActive ? 'bg-slate-900 text-white shadow-lg scale-110' :
                    isCompleted ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100'
                  }`}>
                    <Icon size={18} />
                  </div>
                  <span className="text-xs font-medium hidden sm:block">{phase.name}</span>
                </div>
                
                {index < phases.length - 1 && (
                  <div className={`w-8 sm:w-12 h-0.5 mx-2 transition-colors duration-300 ${
                    isCompleted ? 'bg-emerald-400' : 'bg-slate-200'
                  }`} />
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
