import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Dashboard } from './components/dashboard/Dashboard'
import { PersonalDataForm } from './components/PersonalDataForm'
import { PhaseView } from './components/PhaseView'
import { ResultsView } from './components/ResultsView'
import { ProfileView } from './components/ProfileView'
import { useMBPStore } from './stores/mbpStore'

// Wrapper to handle current session routing
function CurrentAnalysisRoute() {
  const { sessionId } = useMBPStore()
  
  if (!sessionId) {
    return <Navigate to="/new-analysis" replace />
  }
  
  return <PhaseView />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/new-analysis" element={<PersonalDataForm />} />
        <Route path="/analysis/current" element={<CurrentAnalysisRoute />} />
        <Route path="/analysis/:sessionId" element={<PhaseView />} />
        <Route path="/results/:analysisId" element={<ResultsView />} />
        <Route path="/profile/:sessionId" element={<ProfileView />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
