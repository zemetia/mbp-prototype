import { useState, useEffect, useRef } from 'react'
import { ChatInterface } from './components/ChatInterface'
import { PhaseIndicator } from './components/PhaseIndicator'
import { StartScreen } from './components/StartScreen'
import { ProfileView } from './components/ProfileView'
import { useMBPStore } from './stores/mbpStore'

function App() {
  const [showProfile, setShowProfile] = useState(false)
  const { sessionId, phase, connect, disconnect } = useMBPStore()

  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  const handleStart = async () => {
    await connect()
  }

  if (showProfile && sessionId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <ProfileView 
          sessionId={sessionId}
          onBack={() => setShowProfile(false)}
        />
      </div>
    )
  }

  if (!sessionId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <StartScreen onStart={handleStart} />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">MB</span>
            </div>
            <div>
              <h1 className="font-semibold text-slate-900">MirrorBreak Protocol</h1>
              <p className="text-xs text-slate-500">Session: {sessionId}</p>
            </div>
          </div>
          
          {phase >= 6 && (
            <button
              onClick={() => setShowProfile(true)}
              className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm hover:bg-slate-800 transition"
            >
              View Profile
            </button>
          )}
        </div>
        
        <PhaseIndicator currentPhase={phase} />
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6">
        <ChatInterface />
      </main>
    </div>
  )
}

export default App
