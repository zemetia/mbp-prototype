// Shared type definitions for MBP Frontend

export interface PersonalData {
  id: string | null
  nama: string
  tanggal_lahir: string
  tempat_lahir: string
  agama: string
}

export interface PersonalDataInput {
  nama: string
  tanggal_lahir: string
  tempat_lahir: string
  agama: string
}

export interface Analysis {
  id: string
  personalDataId: string
  sessionId: string
  nama: string
  createdAt: string
  completedAt: string
  profileSummary?: string
  overallConfidence?: number
}

// Question-based types
export interface Question {
  id: string
  question_id?: string  // Backend field (snake_case)
  text: string
  phase: string
  phase_number: number  // Backend returns snake_case
  phaseNumber?: number  // Alias for frontend compatibility
  dimensions: string[] // 12D dimensions this question maps to
  type: 'fixed' | 'flexible'
  order: number
}

export interface Answer {
  questionId: string
  questionText: string
  answer: string
  phase: string
  timestamp: Date
  dimensions: string[]
}

export interface PhaseInfo {
  name: string
  number: number
  description: string
  totalQuestions: number
}

// Legacy Message type (keep for compatibility)
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  phase: number
  metadata?: {
    context?: string
    tension_target?: string
    preview?: any
    profile?: any
  }
  timestamp: Date
}
