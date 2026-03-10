import { Sparkles } from 'lucide-react'

interface StartScreenProps {
  onStart: () => void
}

export function StartScreen({ onStart }: StartScreenProps) {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        <div className="mb-8">
          <div className="w-20 h-20 bg-slate-900 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-4">
            MirrorBreak Protocol
          </h1>
          <p className="text-lg text-slate-600">
            Sistem profiling struktural berbasis pola empiris
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 mb-8 text-left">
          <h2 className="font-semibold text-slate-900 mb-4">Apa yang akan terjadi:</h2>
          <ul className="space-y-3 text-slate-600">
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 bg-slate-100 rounded-full flex items-center justify-center text-sm font-medium text-slate-700 shrink-0">1</span>
              <span>Safety screening untuk memastikan kondisi aman</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 bg-slate-100 rounded-full flex items-center justify-center text-sm font-medium text-slate-700 shrink-0">2</span>
              <span>Wawancara mendalam (6 fase) dengan AI agents</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 bg-slate-100 rounded-full flex items-center justify-center text-sm font-medium text-slate-700 shrink-0">3</span>
              <span>Profil struktural dengan confidence intervals</span>
            </li>
          </ul>

          <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-sm text-amber-800">
              <strong>Perhatian:</strong> Ini bukan diagnosis klinis atau therapy. 
              Untuk kebutuhan mental health, konsultasikan dengan professional.
            </p>
          </div>
        </div>

        <button
          onClick={onStart}
          className="w-full sm:w-auto px-8 py-4 bg-slate-900 text-white rounded-xl font-medium hover:bg-slate-800 transition flex items-center justify-center gap-2 mx-auto"
        >
          Mulai Assessment
        </button>

        <p className="mt-6 text-sm text-slate-500">
          Anonymous • No login required • Data disimpan untuk review
        </p>
      </div>
    </div>
  )
}
