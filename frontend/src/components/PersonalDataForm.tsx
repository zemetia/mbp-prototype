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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition"
          >
            <ArrowLeft className="w-5 h-5" />
            Kembali
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-8 h-8 text-slate-600" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mb-2">
              Data Pribadi
            </h1>
            <p className="text-slate-600">
              Masukkan informasi dasar untuk memulai analisis
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="nama" className="block text-sm font-medium text-slate-700 mb-2">
                Nama
              </label>
              <input
                type="text"
                id="nama"
                value={formData.nama}
                onChange={(e) => handleChange('nama', e.target.value)}
                className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:border-slate-500 transition"
                placeholder="Masukkan nama lengkap"
              />
              {errors.nama && (
                <p className="mt-1 text-sm text-red-600">{errors.nama}</p>
              )}
            </div>

            <div>
              <label htmlFor="tanggal_lahir" className="block text-sm font-medium text-slate-700 mb-2">
                Tanggal Lahir
              </label>
              <input
                type="text"
                id="tanggal_lahir"
                value={formData.tanggal_lahir}
                onChange={(e) => handleChange('tanggal_lahir', e.target.value)}
                className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:border-slate-500 transition"
                placeholder="DD/MM/YYYY"
              />
              {errors.tanggal_lahir && (
                <p className="mt-1 text-sm text-red-600">{errors.tanggal_lahir}</p>
              )}
            </div>

            <div>
              <label htmlFor="tempat_lahir" className="block text-sm font-medium text-slate-700 mb-2">
                Tempat Lahir
              </label>
              <input
                type="text"
                id="tempat_lahir"
                value={formData.tempat_lahir}
                onChange={(e) => handleChange('tempat_lahir', e.target.value)}
                className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:border-slate-500 transition"
                placeholder="Masukkan tempat lahir"
              />
              {errors.tempat_lahir && (
                <p className="mt-1 text-sm text-red-600">{errors.tempat_lahir}</p>
              )}
            </div>

            <div>
              <label htmlFor="agama" className="block text-sm font-medium text-slate-700 mb-2">
                Agama
              </label>
              <input
                type="text"
                id="agama"
                value={formData.agama}
                onChange={(e) => handleChange('agama', e.target.value)}
                className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:border-slate-500 transition"
                placeholder="Masukkan agama"
              />
              {errors.agama && (
                <p className="mt-1 text-sm text-red-600">{errors.agama}</p>
              )}
            </div>

            {errors.submit && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                <p className="text-sm text-red-600">{errors.submit}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-4 bg-slate-900 text-white rounded-xl font-medium hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Memulai...
                </>
              ) : (
                'Lanjutkan'
              )}
            </button>
          </form>

          <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-xl">
            <p className="text-sm text-amber-800">
              <strong>Privasi:</strong> Data pribadi Anda digunakan hanya untuk konteks analisis. 
              Informasi ini tidak dibagikan ke pihak ketiga.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
