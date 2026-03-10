import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Loader2 } from 'lucide-react'
import { useMBPStore } from '../../stores/mbpStore'
import { Header } from './Header'
import { EmptyState } from './EmptyState'
import { AnalysisCard } from './AnalysisCard'

export function Dashboard() {
  const navigate = useNavigate()
  const { analyses, isLoadingAnalyses, loadAnalyses, resetSession } = useMBPStore()

  useEffect(() => {
    loadAnalyses()
    resetSession()
  }, [loadAnalyses, resetSession])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Header />
      
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Daftar Analisis</h2>
            <p className="text-slate-600 mt-1">
              Kelola dan tinjau profil struktural yang telah dibuat
            </p>
          </div>
          <button
            onClick={() => navigate('/new-analysis')}
            className="hidden sm:inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-lg font-medium hover:bg-slate-800 transition"
          >
            <Plus className="w-5 h-5" />
            Tambah Baru
          </button>
        </div>

        {isLoadingAnalyses ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
          </div>
        ) : analyses.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200">
            <EmptyState />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analyses.map((analysis) => (
              <AnalysisCard key={analysis.id} analysis={analysis} />
            ))}
          </div>
        )}
      </main>

      {/* Mobile FAB */}
      <button
        onClick={() => navigate('/new-analysis')}
        className="sm:hidden fixed bottom-6 right-6 w-14 h-14 bg-slate-900 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-slate-800 transition"
      >
        <Plus className="w-6 h-6" />
      </button>
    </div>
  )
}
