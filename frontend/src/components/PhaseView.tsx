import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Loader2, CheckCircle } from 'lucide-react'
import { useMBPStore } from '../stores/mbpStore'
import { ProgressBar } from './ProgressBar'
import { QuestionCard } from './QuestionCard'
import { PhaseTransition } from './PhaseTransition'

export function PhaseView() {
  const navigate = useNavigate()
  const { sessionId: urlSessionId } = useParams<{ sessionId: string }>()
  
  const { 
    sessionId: currentSessionId,
    currentPhase,
    currentPhaseNumber,
    currentQuestion,
    isLoading,
    isProcessing,
    answers,
    submitAnswer,
    loadCurrentQuestion,
    getPhaseProgress,
    getCurrentPhaseInfo,
    resetSession
  } = useMBPStore()

  const sessionId = urlSessionId || currentSessionId
  const phaseInfo = getCurrentPhaseInfo()
  const phaseProgress = getPhaseProgress()

  // Load question on mount if we have a session
  useEffect(() => {
    if (sessionId && !currentQuestion && !isProcessing) {
      loadCurrentQuestion()
    }
  }, [sessionId, currentQuestion, isProcessing, loadCurrentQuestion])

  // Monitor completion
  useEffect(() => {
    if (currentPhase === 'complete' && sessionId) {
      const timer = setTimeout(() => {
        navigate(`/results/${sessionId}`)
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [currentPhase, sessionId, navigate])

  const handleBack = () => {
    resetSession()
    navigate('/')
  }

  const handleSubmitAnswer = async (answer: string) => {
    await submitAnswer(answer)
  }

  // Loading state
  if (isLoading && !currentQuestion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-slate-400 mx-auto mb-4" />
          <p className="text-slate-600">Memuat pertanyaan...</p>
        </div>
      </div>
    )
  }

  // Processing/transition state
  if (isProcessing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
          <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={handleBack}
                className="p-2 hover:bg-slate-100 rounded-lg transition"
              >
                <ArrowLeft className="w-5 h-5 text-slate-600" />
              </button>
              <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">MB</span>
              </div>
              <div>
                <h1 className="font-semibold text-slate-900">MirrorBreak Protocol</h1>
                <p className="text-xs text-slate-500">Session: {sessionId?.slice(0, 8)}...</p>
              </div>
            </div>
          </div>
          <ProgressBar currentPhase={currentPhaseNumber} />
        </header>

        <main className="max-w-4xl mx-auto px-4 py-6">
          <PhaseTransition 
            fromPhase={currentPhase}
            toPhase={phaseInfo ? PHASES[Math.min(phaseInfo.number + 1, 6)].name.toLowerCase() : 'core'}
            progress={50}
          />
        </main>
      </div>
    )
  }

  // Complete state
  if (currentPhase === 'complete') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center p-8">
          <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-emerald-600" />
          </div>
          <h2 className="text-2xl font-semibold text-slate-900 mb-2">
            Analisis Selesai!
          </h2>
          <p className="text-slate-600 mb-4">
            Mengalihkan ke halaman hasil...
          </p>
        </div>
      </div>
    )
  }

  // No question state (should not happen normally)
  if (!currentQuestion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center p-8">
          <p className="text-slate-600 mb-4">Tidak ada pertanyaan tersedia.</p>
          <button
            onClick={handleBack}
            className="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition"
          >
            Kembali ke Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={handleBack}
              className="p-2 hover:bg-slate-100 rounded-lg transition"
            >
              <ArrowLeft className="w-5 h-5 text-slate-600" />
            </button>
            <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">MB</span>
            </div>
            <div>
              <h1 className="font-semibold text-slate-900">MirrorBreak Protocol</h1>
              <p className="text-xs text-slate-500">Session: {sessionId?.slice(0, 8)}...</p>
            </div>
          </div>
          
          {/* Overall Progress */}
          <div className="hidden sm:flex items-center gap-3">
            <span className="text-xs text-slate-500">
              Progress: {answers.length} jawaban
            </span>
            <ProgressBar currentPhase={currentPhaseNumber} compact />
          </div>
        </div>
        
        <ProgressBar currentPhase={currentPhaseNumber} />
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Phase Info */}
        <div className="mb-6 text-center">
          <h2 className="text-lg font-medium text-slate-800">
            Fase {currentPhaseNumber}: {phaseInfo?.name}
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            {phaseInfo?.description}
          </p>
        </div>

        {/* Question Card */}
        <QuestionCard
          question={currentQuestion}
          onSubmit={handleSubmitAnswer}
          isLoading={isLoading}
          currentNumber={phaseProgress.current}
          totalInPhase={phaseProgress.total}
        />

        {/* Help Text */}
        <div className="mt-6 text-center">
          <p className="text-xs text-slate-400">
            Jawablah dengan jujur dan spontan. Tidak ada jawaban yang benar atau salah.
          </p>
        </div>
      </main>
    </div>
  )
}

// Phase configuration for transition
const PHASES = [
  { name: 'Safety', number: 0 },
  { name: 'Core', number: 1 },
  { name: 'Adaptive', number: 2 },
  { name: 'Mining', number: 3 },
  { name: 'Validation', number: 4 },
  { name: 'Synthesis', number: 5 },
  { name: 'Closure', number: 6 },
]
