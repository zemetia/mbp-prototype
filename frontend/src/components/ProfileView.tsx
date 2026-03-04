import { useState, useEffect } from 'react'
import { ArrowLeft, Download, Share2, AlertCircle } from 'lucide-react'

interface ProfileViewProps {
  sessionId: string
  onBack: () => void
}

interface Profile {
  core_fear?: { primary: string; confidence: number }
  core_drive?: { primary: string; confidence: number }
  defense_mechanism?: { dominant: string; sophistication: string }
  structural_summary?: string
  persona_core_gap?: { claimed_identity: string; operating_structure: string }
  adaptation_to_potential?: { survival_pattern: string; converted_strength: string }
  integration_assessment?: { type: string; description: string }
  key_contradictions?: Array<{ dimensions: string[]; explanation: string }>
  overall_confidence?: number
  core_summary?: string
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function ProfileView({ sessionId, onBack }: ProfileViewProps) {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchProfile()
  }, [sessionId])

  const fetchProfile = async () => {
    try {
      const response = await fetch(`${API_URL}/api/sessions/${sessionId}/profile`)
      const data = await response.json()
      
      if (data.status === 'complete') {
        setProfile(data.profile)
      } else {
        setError('Profile belum selesai dibuat')
      }
    } catch (err) {
      setError('Gagal memuat profile')
    } finally {
      setLoading(false)
    }
  }

  const downloadProfile = () => {
    if (!profile) return
    
    const content = JSON.stringify(profile, null, 2)
    const blob = new Blob([content], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `mbp-profile-${sessionId}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-slate-500">Memuat profile...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-slate-600">{error}</p>
          <button
            onClick={onBack}
            className="mt-4 px-4 py-2 bg-slate-900 text-white rounded-lg"
          >
            Kembali
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft className="w-5 h-5" />
          Kembali ke Chat
        </button>
        
        <div className="flex gap-2">
          <button
            onClick={downloadProfile}
            className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition"
          >
            <Download className="w-4 h-4" />
            Download JSON
          </button>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="bg-slate-900 text-white p-8">
          <h1 className="text-3xl font-bold mb-2">Structural Profile</h1>
          <p className="text-slate-300">MirrorBreak Protocol • Session: {sessionId}</p>
          
          <div className="mt-4 flex items-center gap-4">
            <div className="px-3 py-1 bg-white/10 rounded-full text-sm">
              Confidence: {profile?.overall_confidence || 0}%
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 space-y-8">
          {/* Core Summary */}
          {profile?.core_summary && (
            <section>
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Ringkasan Utama</h2>
              <p className="text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-xl">
                {profile.core_summary}
              </p>
            </section>
          )}

          {/* Core Fear & Drive */}
          <div className="grid md:grid-cols-2 gap-6">
            {profile?.core_fear && (
              <section className="bg-red-50 p-6 rounded-xl">
                <h3 className="font-semibold text-red-900 mb-2">Core Fear</h3>
                <p className="text-red-800">{profile.core_fear.primary}</p>
                <p className="text-sm text-red-600 mt-2">
                  Confidence: {profile.core_fear.confidence}%
                </p>
              </section>
            )}
            
            {profile?.core_drive && (
              <section className="bg-emerald-50 p-6 rounded-xl">
                <h3 className="font-semibold text-emerald-900 mb-2">Core Drive</h3>
                <p className="text-emerald-800">{profile.core_drive.primary}</p>
                <p className="text-sm text-emerald-600 mt-2">
                  Confidence: {profile.core_drive.confidence}%
                </p>
              </section>
            )}
          </div>

          {/* Defense Mechanism */}
          {profile?.defense_mechanism && (
            <section>
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Defense Mechanism</h2>
              <div className="bg-amber-50 p-6 rounded-xl">
                <p className="font-medium text-amber-900">{profile.defense_mechanism.dominant}</p>
                <p className="text-sm text-amber-700 mt-1">
                  Sophistication: {profile.defense_mechanism.sophistication}
                </p>
              </div>
            </section>
          )}

          {/* Persona-Core Gap */}
          {profile?.persona_core_gap && (
            <section>
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Persona-Core Gap</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 border border-slate-200 rounded-xl">
                  <p className="text-sm text-slate-500 mb-1">Claimed Identity</p>
                  <p className="text-slate-800">{profile.persona_core_gap.claimed_identity}</p>
                </div>
                <div className="p-4 border border-slate-200 rounded-xl">
                  <p className="text-sm text-slate-500 mb-1">Operating Structure</p>
                  <p className="text-slate-800">{profile.persona_core_gap.operating_structure}</p>
                </div>
              </div>
            </section>
          )}

          {/* Adaptation to Potential */}
          {profile?.adaptation_to_potential && (
            <section>
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Adaptation → Potential</h2>
              <div className="bg-purple-50 p-6 rounded-xl">
                <div className="mb-4">
                  <p className="text-sm text-purple-600 mb-1">Survival Pattern</p>
                  <p className="text-purple-900">{profile.adaptation_to_potential.survival_pattern}</p>
                </div>
                <div className="flex items-center gap-2 text-purple-400 my-2">↓</div>
                <div>
                  <p className="text-sm text-purple-600 mb-1">Converted Strength</p>
                  <p className="text-purple-900 font-medium">{profile.adaptation_to_potential.converted_strength}</p>
                </div>
              </div>
            </section>
          )}

          {/* Integration Assessment */}
          {profile?.integration_assessment && (
            <section>
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Integration Pattern</h2>
              <div className="p-4 bg-slate-50 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-1 bg-slate-200 rounded text-sm font-medium">
                    Type {profile.integration_assessment.type}
                  </span>
                </div>
                <p className="text-slate-700">{profile.integration_assessment.description}</p>
              </div>
            </section>
          )}

          {/* Key Contradictions */}
          {profile?.key_contradictions && profile.key_contradictions.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Key Tensions</h2>
              <div className="space-y-3">
                {profile.key_contradictions.map((contradiction, idx) => (
                  <div key={idx} className="p-4 border-l-4 border-indigo-500 bg-indigo-50 rounded-r-xl">
                    <p className="text-sm font-medium text-indigo-900 mb-1">
                      {contradiction.dimensions.join(' × ')}
                    </p>
                    <p className="text-indigo-700">{contradiction.explanation}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Disclaimer */}
          <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-xl">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-amber-900">Penting</p>
                <p className="text-sm text-amber-800 mt-1">
                  Profile ini adalah interpretasi struktural berdasarkan pola empiris, bukan diagnosis klinis. 
                  Confidence level menunjukkan ketidakpastian dalam interpretasi, bukan validitas. 
                  Untuk kebutuhan mental health, konsultasikan dengan professional.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
