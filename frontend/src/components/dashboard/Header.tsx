import { Sparkles } from 'lucide-react'

export function Header() {
  return (
    <header className="bg-white border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center gap-3">
        <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-semibold text-slate-900">MirrorBreak Protocol</h1>
          <p className="text-xs text-slate-500">Dashboard</p>
        </div>
      </div>
    </header>
  )
}
