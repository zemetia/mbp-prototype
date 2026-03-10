import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { useMBPStore } from '../stores/mbpStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Profile {
  core_summary?: string
  overall_confidence?: number
  core_fear?: { primary: string; confidence: number }
  core_drive?: { primary: string; confidence: number }
}

export function ResultsView() {
  const { analysisId } = useParams<{ analysisId: string }>()
  const navigate = useNavigate()
  const { saveAnalysis } = useMBPStore()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchProfile()
  }, [analysisId])

  const fetchProfile = async () => {
    try {
      const response = await fetch(`${API_URL}/api/sessions/${analysisId}/profile`)
      const data = await response.json()
      
      if (data.status === 'complete') {
        setProfile(data.profile)
      } else {
        setError('Profile belum selesai dibuat')
      }
    } catch (err) {
      setError('Gagal memuat profile')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveAnalysis = async () => {
    if (!analysisId || !profile) return
    
    setIsSaving(true)
    try {
      await saveAnalysis(analysisId, { final_profile: profile })
      setIsSaved(true)
      // Navigate to dashboard after short delay
      setTimeout(() => {
        navigate('/')
      }, 1500)
    } catch (err) {
      setError('Gagal menyimpan analisis')
    } finally {
      setIsSaving(false)
    }
  }

  const handleViewDetail = () => {
    navigate(`/profile/${analysisId}`)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-slate-400 mx-auto mb-4" />
          <p className="text-slate-600">Memuat hasil analisis...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-slate-600">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-6 py-2 bg-slate-900 text-white rounded-lg"
          >
            Kembali ke Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition"
          >
            <ArrowLeft className="w-5 h-5" />
            Kembali ke Dashboard
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          {/* Header */}
          <div className="bg-slate-900 text-white p-8">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle className="w-8 h-8 text-emerald-400" />
              <span className="text-emerald-400 font-medium">Analisis Selesai</span>
            </div>
            <h1 className="text-3xl font-bold mb-2">Hasil Analisis</h1>
            <p className="text-slate-300">
              Berikut adalah ringkasan profil struktural Anda
            </p>
            
            {profile?.overall_confidence && (
              <div className="mt-4 flex items-center gap-4">
                <div className="px-3 py-1 bg-white/10 rounded-full text-sm">
                  Confidence: {profile.overall_confidence}%
                </div>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="p-8 space-y-6">
            {profile?.core_summary && (
              <section>
                <h2 className="text-lg font-semibold text-slate-900 mb-3">Ringkasan Utama</h2>
                <p className="text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-xl">
                  {profile.core_summary}
                </p>
              </section>
            )}

            {/* Core Fear & Drive Preview */}
            <div className="grid md:grid-cols-2 gap-4">
              {profile?.core_fear && (
                <section className="bg-red-50 p-5 rounded-xl">
                  <h3 className="font-semibold text-red-900 mb-2">Core Fear</h3>
                  <p className="text-red-800 text-sm">{profile.core_fear.primary}</p>
                </section>
              )}
              
              {profile?.core_drive && (
                <section className="bg-emerald-50 p-5 rounded-xl">
                  <h3 className="font-semibold text-emerald-900 mb-2">Core Drive</h3>
                  <p className="text-emerald-800 text-sm">{profile.core_drive.primary}</p>
                </section>
              )}
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-slate-200">
              <button
                onClick={handleSaveAnalysis}
                disabled={isSaving || isSaved}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-slate-900 text-white rounded-xl font-medium hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Menyimpan...
                  </>
                ) : isSaved ? (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Tersimpan
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5" />
                    Simpan Analisis
                  </>
                )}
              </button>
              
              <button
                onClick={handleViewDetail}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-white border border-slate-300 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition"
              >
                <FileText className="w-5 h-5" />
                Lihat Detail
              </button>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-xl">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-amber-900">Penting</p>
              <p className="text-sm text-amber-800 mt-1">
                Profile ini adalah interpretasi struktural berdasarkan pola empiris, bukan diagnosis klinis. 
                Untuk kebutuhan mental health, konsultasikan dengan professional.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
