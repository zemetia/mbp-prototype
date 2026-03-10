import { FileSearch, Plus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function EmptyState() {
  const navigate = useNavigate()

  return (
    <div className="text-center py-16 px-4">
      <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <FileSearch className="w-10 h-10 text-slate-400" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">
        Belum ada analisis
      </h3>
      <p className="text-slate-600 mb-6 max-w-sm mx-auto">
        Mulai analisis baru untuk membuat profil struktural pertama Anda.
      </p>
      <button
        onClick={() => navigate('/new-analysis')}
        className="inline-flex items-center gap-2 px-6 py-3 bg-slate-900 text-white rounded-xl font-medium hover:bg-slate-800 transition"
      >
        <Plus className="w-5 h-5" />
        Tambah Baru
      </button>
    </div>
  )
}
