import { create } from 'zustand'
import type { Question, Answer, PhaseInfo, PersonalData, PersonalDataInput, Analysis } from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Phase mapping according to MBP Protocol
const PHASES: PhaseInfo[] = [
  { name: 'Safety', number: 0, description: 'Safety & Context Screening', totalQuestions: 7 },
  { name: 'Core', number: 1, description: 'Core Questioning', totalQuestions: 11 },
  { name: 'Adaptive', number: 2, description: 'Adaptive Probing', totalQuestions: 5 },
  { name: 'Mining', number: 3, description: 'Adaptation Pattern Mining', totalQuestions: 8 },
  { name: 'Validation', number: 4, description: 'Cross-Validation', totalQuestions: 6 },
  { name: 'Synthesis', number: 5, description: 'Structural Synthesis', totalQuestions: 0 },
  { name: 'Closure', number: 6, description: 'Debriefing & Closure', totalQuestions: 6 },
]

interface MBPState {
  // Session
  sessionId: string | null
  
  // Question-based flow
  currentPhase: string
  currentPhaseNumber: number
  currentQuestion: Question | null
  questions: Question[]
  answers: Answer[]
  isLoading: boolean
  isProcessing: boolean // For phase transition
  error: string | null
  
  // Personal Data
  personalData: PersonalData
  personalDataId: string | null
  
  // Analyses
  analyses: Analysis[]
  isLoadingAnalyses: boolean
  
  // Actions
  createSession: (personalDataId?: string) => Promise<void>
  loadCurrentQuestion: () => Promise<void>
  submitAnswer: (answer: string) => Promise<void>
  nextQuestion: () => Promise<void>
  nextPhase: () => Promise<void>
  
  // Personal Data Actions
  savePersonalData: (data: PersonalDataInput) => Promise<string>
  loadAnalyses: () => Promise<void>
  saveAnalysis: (sessionId: string, data: any) => Promise<void>
  setPersonalDataId: (id: string | null) => void
  resetSession: () => void
  
  // Getters
  getCurrentPhaseInfo: () => PhaseInfo | undefined
  getPhaseProgress: () => { current: number; total: number }
  getOverallProgress: () => { current: number; total: number }
}

const initialPersonalData: PersonalData = {
  id: null,
  nama: '',
  tanggal_lahir: '',
  tempat_lahir: '',
  agama: ''
}

export const useMBPStore = create<MBPState>((set, get) => ({
  // Initial State
  sessionId: null,
  currentPhase: 'safety',
  currentPhaseNumber: 0,
  currentQuestion: null,
  questions: [],
  answers: [],
  isLoading: false,
  isProcessing: false,
  error: null,
  personalData: initialPersonalData,
  personalDataId: null,
  analyses: [],
  isLoadingAnalyses: false,

  // Create session
  createSession: async (personalDataId?: string) => {
    try {
      let sessionId: string
      
      console.log('[MBP Store] Creating session, personalDataId:', personalDataId)
      
      if (personalDataId) {
        const url = `${API_URL}/api/sessions/with-personal-data`
        console.log('[MBP Store] POST', url)
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ personal_data_id: personalDataId })
        })
        if (!response.ok) {
          const errorText = await response.text()
          console.error('[MBP Store] Create session error:', response.status, errorText)
          throw new Error('Failed to create session')
        }
        const data = await response.json()
        console.log('[MBP Store] Session created:', data)
        sessionId = data.session_id
      } else {
        const response = await fetch(`${API_URL}/api/sessions`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        })
        const data = await response.json()
        sessionId = data.session_id
      }

      set({ 
        sessionId, 
        currentPhase: 'safety',
        currentPhaseNumber: 0,
        questions: [],
        answers: [],
        error: null
      })
      
      console.log('[MBP Store] Session set, loading first question...')
      // Load first question
      await get().loadCurrentQuestion()

    } catch (error) {
      console.error('[MBP Store] Connection error:', error)
      set({ error: 'Failed to create session', isLoading: false })
    }
  },

  // Load current question from backend
  loadCurrentQuestion: async () => {
    const { sessionId } = get()
    if (!sessionId) {
      console.error('[MBP Store] No sessionId available')
      return
    }
    
    set({ isLoading: true, error: null })
    
    try {
      const url = `${API_URL}/api/sessions/${sessionId}/questions`
      console.log('[MBP Store] Fetching questions from:', url)
      
      const response = await fetch(url)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('[MBP Store] HTTP error:', response.status, errorText)
        throw new Error(`Failed to load question: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('[MBP Store] Response:', data)
      
      if (data.question) {
        console.log('[MBP Store] Setting current question:', data.question.id)
        set({ 
          currentQuestion: data.question,
          currentPhase: data.phase || get().currentPhase,
          currentPhaseNumber: data.phase_number ?? get().currentPhaseNumber,
          isLoading: false 
        })
      } else if (data.phase_complete) {
        console.log('[MBP Store] Phase complete, advancing...')
        set({ isLoading: false })
        await get().nextPhase()
      } else if (data.analysis_complete) {
        console.log('[MBP Store] Analysis complete')
        set({ 
          currentPhase: 'complete',
          currentPhaseNumber: 6,
          isLoading: false 
        })
      } else {
        console.error('[MBP Store] No question in response:', data)
        set({ error: 'Tidak ada pertanyaan tersedia', isLoading: false })
      }
      
    } catch (error) {
      console.error('[MBP Store] Error loading question:', error)
      set({ error: 'Failed to load question', isLoading: false })
    }
  },

  // Submit answer for current question
  submitAnswer: async (answer: string) => {
    const { sessionId, currentQuestion } = get()
    if (!sessionId || !currentQuestion) return
    
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`${API_URL}/api/sessions/${sessionId}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: currentQuestion.id,
          answer: answer,
          timestamp: new Date().toISOString()
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to submit answer')
      }
      
      const data = await response.json()
      
      // Save answer locally
      const newAnswer: Answer = {
        questionId: currentQuestion.id,
        questionText: currentQuestion.text,
        answer: answer,
        phase: currentQuestion.phase,
        timestamp: new Date(),
        dimensions: currentQuestion.dimensions
      }
      
      set((state) => ({
        answers: [...state.answers, newAnswer]
      }))
      
      // Check if phase is complete
      if (data.phase_complete) {
        await get().nextPhase()
      } else if (data.next_question) {
        set({ 
          currentQuestion: data.next_question,
          isLoading: false 
        })
      } else if (data.analysis_complete) {
        set({ 
          currentPhase: 'complete',
          currentPhaseNumber: 6,
          isLoading: false 
        })
      }
      
    } catch (error) {
      console.error('Error submitting answer:', error)
      set({ error: 'Failed to submit answer', isLoading: false })
    }
  },

  // Move to next question (used for navigation)
  nextQuestion: async () => {
    await get().loadCurrentQuestion()
  },

  // Advance to next phase (triggers AI processing)
  nextPhase: async () => {
    const { sessionId } = get()
    if (!sessionId) return
    
    set({ isProcessing: true, isLoading: false })
    
    try {
      const response = await fetch(`${API_URL}/api/sessions/${sessionId}/next-phase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm: true })
      })
      
      if (!response.ok) {
        throw new Error('Failed to advance phase')
      }
      
      const data = await response.json()
      
      if (data.analysis_complete) {
        set({ 
          currentPhase: 'complete',
          currentPhaseNumber: 6,
          isProcessing: false 
        })
      } else if (data.next_phase) {
        set({ 
          currentPhase: data.next_phase,
          currentPhaseNumber: data.phase_number ?? get().currentPhaseNumber + 1,
          isProcessing: false 
        })
        // Load first question of new phase
        await get().loadCurrentQuestion()
      }
      
    } catch (error) {
      console.error('Error advancing phase:', error)
      set({ error: 'Failed to advance phase', isProcessing: false })
    }
  },

  // Get current phase info
  getCurrentPhaseInfo: () => {
    const state = get()
    return PHASES.find(p => p.number === state.currentPhaseNumber)
  },

  // Get progress within current phase
  getPhaseProgress: () => {
    const state = get()
    const phaseInfo = PHASES.find(p => p.number === state.currentPhaseNumber)
    
    if (!phaseInfo) return { current: 0, total: 0 }
    
    // Count answers in current phase
    const phaseAnswers = state.answers.filter(a => {
      const answerPhaseNum = PHASES.find(p => 
        p.name.toLowerCase() === a.phase.toLowerCase()
      )?.number ?? -1
      return answerPhaseNum === state.currentPhaseNumber
    }).length
    
    return { 
      current: phaseAnswers + 1, 
      total: phaseInfo.totalQuestions 
    }
  },

  // Get overall progress through all phases
  getOverallProgress: () => {
    const state = get()

    // Calculate total questions across all phases up to current
    let totalAnswered = state.answers.length
    let totalQuestions = PHASES.reduce((sum, p) => sum + p.totalQuestions, 0)

    return {
      current: totalAnswered,
      total: totalQuestions
    }
  },

  // Save personal data
  savePersonalData: async (data: PersonalDataInput) => {
    const response = await fetch(`${API_URL}/api/personal-data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    
    if (!response.ok) {
      throw new Error('Failed to save personal data')
    }
    
    const result = await response.json()
    const personalDataId = result.personal_data_id
    
    set({ 
      personalData: { ...data, id: personalDataId },
      personalDataId 
    })
    
    return personalDataId
  },

  // Load analyses list
  loadAnalyses: async () => {
    set({ isLoadingAnalyses: true })
    try {
      const response = await fetch(`${API_URL}/api/analyses`)
      if (!response.ok) {
        throw new Error('Failed to load analyses')
      }
      const data = await response.json()
      set({ analyses: data.analyses || [] })
    } catch (error) {
      console.error('Error loading analyses:', error)
    } finally {
      set({ isLoadingAnalyses: false })
    }
  },

  // Save analysis
  saveAnalysis: async (sessionId: string, data: any) => {
    const { personalDataId } = get()
    
    const response = await fetch(`${API_URL}/api/analyses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        personal_data_id: personalDataId,
        final_profile: data.final_profile,
        matrix_12d: data.matrix_12d,
        executive_summary: data.executive_summary,
        core_insights: data.core_insights || [],
        tensions: data.tensions || []
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to save analysis')
    }
    
    await get().loadAnalyses()
  },

  setPersonalDataId: (id: string | null) => {
    set({ personalDataId: id })
  },

  resetSession: () => {
    set({
      sessionId: null,
      currentPhase: 'safety',
      currentPhaseNumber: 0,
      currentQuestion: null,
      questions: [],
      answers: [],
      isLoading: false,
      isProcessing: false,
      error: null
    })
  }
}))
