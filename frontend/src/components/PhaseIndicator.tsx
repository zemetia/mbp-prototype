import { Brain, Shield, Search, Pickaxe, GitCompare, FileText, CheckCircle } from 'lucide-react'

const phases = [
  { num: 0, name: 'Safety', icon: Shield, desc: 'Pre-screening' },
  { num: 1, name: 'Core', icon: Brain, desc: 'Tension generators' },
  { num: 2, name: 'Adaptive', icon: Search, desc: 'Hypothesis testing' },
  { num: 3, name: 'Mining', icon: Pickaxe, desc: 'Pattern exploration' },
  { num: 4, name: 'Validation', icon: GitCompare, desc: 'Cross-dimension test' },
  { num: 5, name: 'Synthesis', icon: FileText, desc: 'Profile generation' },
  { num: 6, name: 'Debrief', icon: CheckCircle, desc: 'Closure' },
]

interface PhaseIndicatorProps {
  currentPhase: number
}

export function PhaseIndicator({ currentPhase }: PhaseIndicatorProps) {
  return (
    <div className="bg-slate-50 border-b border-slate-200">
      <div className="max-w-4xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {phases.map((phase, index) => {
            const Icon = phase.icon
            const isActive = phase.num === currentPhase
            const isCompleted = phase.num < currentPhase
            
            return (
              <div key={phase.num} className="flex items-center">
                <div className={`flex flex-col items-center gap-1 ${
                  isActive ? 'text-slate-900' : 
                  isCompleted ? 'text-emerald-600' : 'text-slate-400'
                }`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    isActive ? 'bg-slate-900 text-white' :
                    isCompleted ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-200'
                  }`}>
                    <Icon size={14} />
                  </div>
                  <span className="text-[10px] font-medium hidden sm:block">{phase.name}</span>
                </div>
                
                {index < phases.length - 1 && (
                  <div className={`w-8 sm:w-12 h-0.5 mx-1 ${
                    isCompleted ? 'bg-emerald-300' : 'bg-slate-200'
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
