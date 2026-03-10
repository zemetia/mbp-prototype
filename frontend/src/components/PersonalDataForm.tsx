import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2, User } from 'lucide-react'
import { useMBPStore } from '../stores/mbpStore'

export function PersonalDataForm() {
  const navigate = useNavigate()
  const { savePersonalData, createSession } = useMBPStore()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [formData, setFormData] = useState({
    nama: '',
    tanggal_lahir: '',
    tempat_lahir: '',
    agama: ''
  })

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.nama.trim()) {
      newErrors.nama = 'Nama wajib diisi'
    }
    if (!formData.tanggal_lahir.trim()) {
      newErrors.tanggal_lahir = 'Tanggal lahir wajib diisi'
    }
    if (!formData.tempat_lahir.trim()) {
      newErrors.tempat_lahir = 'Tempat lahir wajib diisi'
    }
    if (!formData.agama.trim()) {
      newErrors.agama = 'Agama wajib diisi'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setIsSubmitting(true)
    try {
      // Save personal data and get ID
      const personalDataId = await savePersonalData(formData)
      
      // Create session with personal data (HTTP, no WebSocket)
      await createSession(personalDataId)
      
      // Navigate to analysis flow
      navigate('/analysis/current')
    } catch (error) {
      console.error('Error starting analysis:', error)
      setErrors({ submit: 'Gagal memulai analisis. Silakan coba lagi.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 relative overflow-hidden">
      {/* Background decoration elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-100 blur-3xl opacity-50 mix-blend-multiply transition-all duration-1000 ease-in-out"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-100 blur-3xl opacity-50 mix-blend-multiply transition-all duration-1000 ease-in-out"></div>
      </div>

      <header className="bg-white/80 backdrop-blur-md border-b border-indigo-100 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4 md:py-5">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-3 py-2 text-indigo-600 hover:bg-indigo-50 hover:text-indigo-900 rounded-lg transition-all duration-200 group"
          >
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
            <span className="font-medium">Kembali</span>
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-10 md:py-16 relative z-10">
        <div className="bg-white/90 backdrop-blur-xl rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white p-8 md:p-10 transition-all duration-300 hover:shadow-[0_8px_40px_rgb(0,0,0,0.08)]">
          <div className="text-center mb-10">
            <div className="w-20 h-20 bg-gradient-to-tr from-indigo-100 to-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-6 transform rotate-3 transition-transform hover:rotate-6">
              <User className="w-10 h-10 text-indigo-600" />
            </div>
            <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-900 to-purple-900 mb-3 tracking-tight">
              Data Pribadi
            </h1>
            <p className="text-slate-500 text-lg">
              Masukkan informasi dasar untuk memulai analisis mendalam Anda
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-1">
              <label htmlFor="nama" className="block text-sm font-semibold text-slate-700 ml-1">
                Nama Lengkap
              </label>
              <input
                type="text"
                id="nama"
                value={formData.nama}
                onChange={(e) => handleChange('nama', e.target.value)}
                className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all text-slate-800 placeholder:text-slate-400 font-medium"
                placeholder="Misal: Budi Santoso"
              />
              {errors.nama && (
                <p className="mt-2 text-sm text-red-500 font-medium ml-1 animate-pulse">{errors.nama}</p>
              )}
            </div>

            <div className="space-y-1">
              <label htmlFor="tanggal_lahir" className="block text-sm font-semibold text-slate-700 ml-1">
                Tanggal Lahir (DD/MM/YYYY)
              </label>
              <input
                type="text"
                id="tanggal_lahir"
                value={formData.tanggal_lahir}
                onChange={(e) => handleChange('tanggal_lahir', e.target.value)}
                className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all text-slate-800 placeholder:text-slate-400 font-medium"
                placeholder="Misal: 15/08/1995"
              />
              {errors.tanggal_lahir && (
                <p className="mt-2 text-sm text-red-500 font-medium ml-1 animate-pulse">{errors.tanggal_lahir}</p>
              )}
            </div>

            <div className="space-y-1">
              <label htmlFor="tempat_lahir" className="block text-sm font-semibold text-slate-700 ml-1">
                Tempat Lahir
              </label>
              <input
                type="text"
                id="tempat_lahir"
                value={formData.tempat_lahir}
                onChange={(e) => handleChange('tempat_lahir', e.target.value)}
                className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all text-slate-800 placeholder:text-slate-400 font-medium"
                placeholder="Misal: Jakarta"
              />
              {errors.tempat_lahir && (
                <p className="mt-2 text-sm text-red-500 font-medium ml-1 animate-pulse">{errors.tempat_lahir}</p>
              )}
            </div>

            <div className="space-y-1">
              <label htmlFor="agama" className="block text-sm font-semibold text-slate-700 ml-1">
                Agama / Kepercayaan
              </label>
              <input
                type="text"
                id="agama"
                value={formData.agama}
                onChange={(e) => handleChange('agama', e.target.value)}
                className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all text-slate-800 placeholder:text-slate-400 font-medium"
                placeholder="Sebutkan agama atau kepercayaan"
              />
              {errors.agama && (
                <p className="mt-2 text-sm text-red-500 font-medium ml-1 animate-pulse">{errors.agama}</p>
              )}
            </div>

            {errors.submit && (
              <div className="p-4 bg-red-50/80 backdrop-blur-sm border border-red-200 rounded-2xl flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-red-500 animate-ping"></div>
                <p className="text-sm text-red-600 font-medium">{errors.submit}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-4 mt-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-2xl font-bold text-lg shadow-lg shadow-indigo-500/30 transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-3"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  Memproses Data...
                </>
              ) : (
                'Mulai Analisis'
              )}
            </button>
          </form>

          <div className="mt-8 p-5 bg-indigo-50/50 border border-indigo-100/50 rounded-2xl text-center">
            <p className="text-sm text-indigo-800/80 leading-relaxed font-medium">
              Data pribadi Anda diproses secara khusus untuk personalisasi hasil analisis. 
              <br className="hidden sm:block"/> Kami menjaga tingkat keamanan privasi tertinggi.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
