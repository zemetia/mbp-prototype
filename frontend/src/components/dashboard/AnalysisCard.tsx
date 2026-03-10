import { useNavigate } from 'react-router-dom'
import { Calendar, User, ChevronRight } from 'lucide-react'
import type { Analysis } from '../../types'

interface AnalysisCardProps {
  analysis: Analysis
}

export function AnalysisCard({ analysis }: AnalysisCardProps) {
  const navigate = useNavigate()

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    })
  }

  return (
    <div
      onClick={() => navigate(`/profile/${analysis.sessionId}`)}
      className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md hover:border-slate-300 transition cursor-pointer group"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-slate-600" />
          </div>
          <h3 className="font-semibold text-slate-900">{analysis.nama}</h3>
        </div>
        <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-slate-600 transition" />
      </div>
      
      <div className="flex items-center gap-2 text-sm text-slate-500 mb-3">
        <Calendar className="w-4 h-4" />
        <span>{formatDate(analysis.completedAt)}</span>
      </div>

      {analysis.overallConfidence && (
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-slate-100 rounded-full h-2">
            <div
              className="bg-emerald-500 h-2 rounded-full"
              style={{ width: `${analysis.overallConfidence}%` }}
            />
          </div>
          <span className="text-xs font-medium text-slate-600">
            {analysis.overallConfidence}%
          </span>
        </div>
      )}

      {analysis.profileSummary && (
        <p className="mt-3 text-sm text-slate-600 line-clamp-2">
          {analysis.profileSummary}
        </p>
      )}
    </div>
  )
}
