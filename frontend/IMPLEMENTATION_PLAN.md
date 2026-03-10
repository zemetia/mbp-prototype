# MBP Frontend - Implementation Plan

## 1. Component Hierarchy (New Structure)

```
App.tsx (Router wrapper)
├── Layout.tsx
│   └── Header.tsx (shared across pages)
├── routes/
│   ├── Dashboard.tsx
│   │   ├── Header.tsx (Dashboard title + logo)
│   │   ├── EmptyState.tsx (when no analyses)
│   │   └── AnalysisCard.tsx (individual analysis preview)
│   ├── PersonalDataForm.tsx
│   ├── AnalysisFlow.tsx (modified ChatInterface wrapper)
│   │   ├── PhaseIndicator.tsx (existing)
│   │   └── ChatInterface.tsx (existing, modified)
│   ├── ResultsView.tsx
│   └── ProfileView.tsx (existing, modified)
└── stores/
    └── mbpStore.ts (extended)
```

## 2. Route Structure

| URL | Component | Purpose |
|-----|-----------|---------|
| `/` | `Dashboard` | List of previous analyses, "+ Tambah Baru" CTA |
| `/new-analysis` | `PersonalDataForm` | Step 1: Personal data input form |
| `/analysis/:sessionId` | `AnalysisFlow` | Step 2: MBP chat analysis (existing chat interface) |
| `/results/:analysisId` | `ResultsView` | Step 3: Show results, save analysis button |
| `/profile/:sessionId` | `ProfileView` | Full detailed profile view (existing) |

## 3. State Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              STATE FLOW                                      │
└─────────────────────────────────────────────────────────────────────────────┘

[Dashboard] ──loadAnalyses()──► GET /analyses
     │
     │ click "+ Tambah Baru"
     ▼
[PersonalDataForm]
     │
     │ submit form
     │ savePersonalData(data)
     ▼
POST /personal-data ──► returns personalDataId
     │
     │ navigate to /analysis/:sessionId
     ▼
[AnalysisFlow]
     │
     │ connect(sessionId, personalDataId)
     │ POST /sessions/with-personal-data
     ▼
WebSocket chat flow (existing)
     │
     │ phase === 6 (complete)
     ▼
[ResultsView]
     │
     │ click "Simpan Analisis"
     │ saveAnalysis(sessionId)
     ▼
POST /analyses ──► navigate to /
     │
     │ click "Lihat Detail"
     ▼
[ProfileView]
```

## 4. API Integration Map

### Component → Endpoint Mapping

| Component | HTTP Method | Endpoint | Purpose |
|-----------|-------------|----------|---------|
| **Dashboard** | GET | `/api/analyses` | Load list of analyses |
| **PersonalDataForm** | POST | `/api/personal-data` | Save personal data |
| **AnalysisFlow** | POST | `/api/sessions/with-personal-data` | Create session with personal data context |
| **ResultsView** | POST | `/api/analyses` | Save completed analysis |
| **ResultsView** | GET | `/api/analyses/:id` | Load saved analysis details |
| **ProfileView** | GET | `/api/sessions/:id/profile` | Load profile (existing) |
| **ProfileView** | GET | `/api/personal-data/:id` | Load personal data (new) |

### Store Actions → API Calls

```typescript
// stores/mbpStore.ts

// NEW ACTIONS:

savePersonalData(data: PersonalDataInput): Promise<string>
  └── POST ${API_URL}/api/personal-data
  └── Returns: personalDataId
  └── Updates: state.personalData

loadAnalyses(): Promise<void>
  └── GET ${API_URL}/api/analyses
  └── Updates: state.analyses

saveAnalysis(sessionId: string): Promise<void>
  └── POST ${API_URL}/api/analyses
  └── Body: { sessionId, personalDataId }
  └── Updates: state.analyses (append new)

// MODIFIED ACTIONS:

connect(personalDataId?: string): Promise<void>
  └── IF personalDataId:
        POST ${API_URL}/api/sessions/with-personal-data
        Body: { personal_data_id: personalDataId }
  └── ELSE:
        POST ${API_URL}/api/sessions (existing behavior)
```

## 5. Implementation Plan - File-by-File Changes

### Phase 1: Install Dependencies

```bash
npm install react-router-dom
```

---

### Phase 2: Update Store (`src/stores/mbpStore.ts`)

**Changes:**
1. Add new interfaces: `PersonalData`, `Analysis`
2. Extend `MBPState` interface with new fields
3. Add new actions: `savePersonalData`, `loadAnalyses`, `saveAnalysis`
4. Modify `connect` action to accept optional `personalDataId`

**Key additions:**
```typescript
interface PersonalData {
  id: string | null
  nama: string
  tanggal_lahir: string
  tempat_lahir: string
  agama: string
}

interface Analysis {
  id: string
  personalDataId: string
  sessionId: string
  nama: string
  createdAt: string
  completedAt: string
  profileSummary?: string
}

// Add to MBPState:
personalData: PersonalData
analyses: Analysis[]
personalDataId: string | null  // for passing to session

// Add actions:
savePersonalData: (data: Omit<PersonalData, 'id'>) => Promise<string>
loadAnalyses: () => Promise<void>
saveAnalysis: (sessionId: string) => Promise<void>
setPersonalDataId: (id: string | null) => void
```

---

### Phase 3: Create New Components

#### 3.1 `src/components/dashboard/Header.tsx` (NEW)
Simple header component for dashboard with logo and title.

#### 3.2 `src/components/dashboard/EmptyState.tsx` (NEW)
Shown when no analyses exist. Contains illustration and CTA.

#### 3.3 `src/components/dashboard/AnalysisCard.tsx` (NEW)
Card component showing single analysis preview:
- Name
- Date
- Brief summary/status
- Click to view detail

#### 3.4 `src/components/dashboard/Dashboard.tsx` (NEW - REPLACES StartScreen)
Main dashboard page:
- Header with title
- List of AnalysisCards (or EmptyState)
- "+ Tambah Baru" floating/action button

#### 3.5 `src/components/PersonalDataForm.tsx` (NEW)
Form page with 4 inputs:
- nama (text)
- tanggal_lahir (text, placeholder: "DD/MM/YYYY")
- tempat_lahir (text)
- agama (text - free text, NOT dropdown)
- "Lanjutkan" button

Form validation + POST to /personal-data on submit.

#### 3.6 `src/components/AnalysisFlow.tsx` (NEW - wraps ChatInterface)
Container for the analysis chat flow:
- Receives `:sessionId` from URL params
- Gets `personalDataId` from store
- Shows PhaseIndicator + ChatInterface
- Monitors phase completion → navigates to results

#### 3.7 `src/components/ResultsView.tsx` (NEW)
Results display page:
- Shows analysis summary
- "Simpan Analisis" button → POST /analyses → navigate to /
- "Lihat Detail" button → navigate to /profile/:sessionId

---

### Phase 4: Modify Existing Components

#### 4.1 `src/App.tsx` (MAJOR CHANGES)
Replace with router setup:
```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Dashboard } from './components/dashboard/Dashboard'
import { PersonalDataForm } from './components/PersonalDataForm'
import { AnalysisFlow } from './components/AnalysisFlow'
import { ResultsView } from './components/ResultsView'
import { ProfileView } from './components/ProfileView'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/new-analysis" element={<PersonalDataForm />} />
          <Route path="/analysis/:sessionId" element={<AnalysisFlow />} />
          <Route path="/results/:analysisId" element={<ResultsView />} />
          <Route path="/profile/:sessionId" element={<ProfileView />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
```

#### 4.2 `src/components/ChatInterface.tsx` (MINOR CHANGES)
- Remove "View Profile" button logic (moved to ResultsView)
- Keep phase completion detection
- Export `phase` completion event or use store

#### 4.3 `src/components/ProfileView.tsx` (MINOR CHANGES)
- Update to work with router (use `useNavigate` for back button)
- Optionally display personal data if available

#### 4.4 `src/components/StartScreen.tsx` (DELETE)
Replaced by Dashboard.

---

### Phase 5: File Structure After Changes

```
src/
├── App.tsx                    # Router setup
├── main.tsx                   # Entry point (no change)
├── index.css                  # Styles (no change)
├── vite-env.d.ts             # Types (no change)
├── components/
│   ├── ChatInterface.tsx      # Modified
│   ├── PhaseIndicator.tsx     # No change
│   ├── ProfileView.tsx        # Modified
│   ├── PersonalDataForm.tsx   # NEW
│   ├── AnalysisFlow.tsx       # NEW
│   ├── ResultsView.tsx        # NEW
│   └── dashboard/
│       ├── Dashboard.tsx      # NEW (replaces StartScreen)
│       ├── Header.tsx         # NEW
│       ├── EmptyState.tsx     # NEW
│       └── AnalysisCard.tsx   # NEW
├── stores/
│   └── mbpStore.ts            # Extended
└── types/
    └── index.ts               # NEW (shared types)
```

---

## 6. Data Models

### PersonalData
```typescript
interface PersonalData {
  id: string | null
  nama: string
  tanggal_lahir: string  // Format: DD/MM/YYYY
  tempat_lahir: string
  agama: string
}
```

### Analysis (Frontend Model)
```typescript
interface Analysis {
  id: string
  personalDataId: string
  sessionId: string
  nama: string
  createdAt: string
  completedAt: string
  profileSummary?: string
  overallConfidence?: number
}
```

---

## 7. UI/UX Specifications

### Color Scheme (Consistent with existing)
- Background: `bg-gradient-to-br from-slate-50 to-slate-100`
- Cards: `bg-white border border-slate-200`
- Primary button: `bg-slate-900 text-white`
- Text inputs: `border-slate-300 focus:border-slate-500`
- Success: `bg-emerald-50 text-emerald-700`

### Dashboard Layout
- Header: Fixed top with logo + "MirrorBreak Protocol - Dashboard"
- Content: Max-width 4xl, centered
- Grid: 1 column mobile, 2 columns tablet, 3 columns desktop for analysis cards
- FAB (Floating Action Button): Bottom-right "+ Tambah Baru"

### Form Layout (PersonalDataForm)
- Centered card, max-w-md
- Vertical stack of inputs with 1rem gap
- Labels above inputs
- Full-width "Lanjutkan" button

---

## 8. Navigation Flow Summary

```
┌─────────────┐     + Tambah Baru      ┌──────────────────┐
│  Dashboard  │ ─────────────────────► │ PersonalDataForm │
│     /       │                        │   /new-analysis  │
└─────────────┘                        └──────────────────┘
       ▲                                          │
       │                                          │ Lanjutkan
       │                                          ▼
       │                              ┌──────────────────┐
       │                              │   AnalysisFlow   │
       │                              │/analysis/:session│
       │                              └──────────────────┘
       │                                          │
       │                                          │ Complete
       │                                          ▼
       │                              ┌──────────────────┐
       │                              │   ResultsView    │
       │                              │/results/:analysis│
       │                              └──────────────────┘
       │                                    │         │
       │                    Simpan Analisis │         │ Lihat Detail
       │                                    ▼         ▼
       │                           ┌─────────┐   ┌──────────┐
       └───────────────────────────│ Dashboard│   │ProfileView│
                                   │    /     │   │/profile/:id
                                   └─────────┘   └──────────┘
```

---

## 9. Implementation Checklist

### Phase 1: Setup
- [ ] Install react-router-dom
- [ ] Create types/index.ts for shared interfaces

### Phase 2: Store
- [ ] Extend mbpStore.ts with new state and actions
- [ ] Add personalData state
- [ ] Add analyses state
- [ ] Implement savePersonalData action
- [ ] Implement loadAnalyses action
- [ ] Implement saveAnalysis action
- [ ] Modify connect action for personalDataId

### Phase 3: Dashboard Components
- [ ] Create dashboard/Header.tsx
- [ ] Create dashboard/EmptyState.tsx
- [ ] Create dashboard/AnalysisCard.tsx
- [ ] Create dashboard/Dashboard.tsx

### Phase 4: Flow Components
- [ ] Create PersonalDataForm.tsx
- [ ] Create AnalysisFlow.tsx
- [ ] Create ResultsView.tsx

### Phase 5: Integration
- [ ] Rewrite App.tsx with Router
- [ ] Modify ChatInterface.tsx (remove profile button logic)
- [ ] Modify ProfileView.tsx (router navigation)
- [ ] Delete StartScreen.tsx

### Phase 6: Testing
- [ ] Test full flow: Dashboard → Form → Analysis → Results → Dashboard
- [ ] Verify API integrations
- [ ] Check responsive design

---

## 10. API Endpoint Assumptions

Based on the requirements, assumed backend endpoints:

```
POST   /api/personal-data          → Create personal data, returns { id }
GET    /api/personal-data/:id      → Get personal data by ID
POST   /api/sessions/with-personal-data → Create session with personal_data_id
GET    /api/analyses               → List all analyses
POST   /api/analyses               → Save new analysis
GET    /api/analyses/:id           → Get single analysis
```

**Note:** Confirm these endpoints with backend team or adjust accordingly.
