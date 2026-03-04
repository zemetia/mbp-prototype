import { create } from 'zustand'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  phase: number
  metadata?: any
  timestamp: Date
}

interface MBPState {
  sessionId: string | null
  phase: number
  messages: Message[]
  isConnected: boolean
  isLoading: boolean
  ws: WebSocket | null
  
  // Actions
  connect: () => Promise<void>
  disconnect: () => void
  sendMessage: (content: string) => void
  addMessage: (message: Message) => void
  setPhase: (phase: number) => void
}

export const useMBPStore = create<MBPState>((set, get) => ({
  sessionId: null,
  phase: 0,
  messages: [],
  isConnected: false,
  isLoading: false,
  ws: null,

  connect: async () => {
    try {
      // Create session
      const response = await fetch(`${API_URL}/api/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      const data = await response.json()
      const sessionId = data.session_id

      // Connect WebSocket
      const ws = new WebSocket(`${API_URL.replace('http', 'ws')}/ws/${sessionId}`)

      ws.onopen = () => {
        set({ isConnected: true, sessionId, ws })
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.type === 'state') {
          set({ phase: data.phase })
        } else if (data.type === 'phase_start') {
          set({ phase: data.phase })
          get().addMessage({
            id: Date.now().toString(),
            role: 'system',
            content: `## ${data.title}\n${data.description}`,
            phase: data.phase,
            timestamp: new Date()
          })
        } else if (data.type === 'question' || data.type === 'message') {
          get().addMessage({
            id: Date.now().toString(),
            role: 'assistant',
            content: data.content,
            phase: data.phase,
            metadata: { context: data.context, tension_target: data.tension_target },
            timestamp: new Date()
          })
          set({ isLoading: false })
        } else if (data.type === 'synthesis_preview') {
          get().addMessage({
            id: Date.now().toString(),
            role: 'assistant',
            content: data.content,
            phase: data.phase,
            metadata: { preview: data.profile_preview },
            timestamp: new Date()
          })
          set({ isLoading: false })
        } else if (data.type === 'profile_complete') {
          get().addMessage({
            id: Date.now().toString(),
            role: 'assistant',
            content: data.content,
            phase: data.phase,
            metadata: { profile: data.profile },
            timestamp: new Date()
          })
          set({ phase: 6, isLoading: false })
        } else if (data.type === 'error') {
          get().addMessage({
            id: Date.now().toString(),
            role: 'system',
            content: `Error: ${data.message}`,
            phase: get().phase,
            timestamp: new Date()
          })
          set({ isLoading: false })
        }
      }

      ws.onclose = () => {
        set({ isConnected: false, ws: null })
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        set({ isConnected: false, isLoading: false })
      }

    } catch (error) {
      console.error('Connection error:', error)
      set({ isConnected: false, isLoading: false })
    }
  },

  disconnect: () => {
    const { ws } = get()
    if (ws) {
      ws.close()
    }
    set({ ws: null, isConnected: false })
  },

  sendMessage: (content: string) => {
    const { ws, phase } = get()
    if (ws && ws.readyState === WebSocket.OPEN) {
      set({ isLoading: true })
      ws.send(JSON.stringify({
        type: 'response',
        content,
        phase
      }))
      
      get().addMessage({
        id: Date.now().toString(),
        role: 'user',
        content,
        phase,
        timestamp: new Date()
      })
    }
  },

  addMessage: (message: Message) => {
    set((state) => ({
      messages: [...state.messages, message]
    }))
  },

  setPhase: (phase: number) => {
    set({ phase })
  }
}))
