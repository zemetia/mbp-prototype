"""
MBP v2.0 - Question Templates
Fixed and flexible questions for each phase of the MirrorBreak Protocol
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class QuestionType(str, Enum):
    FIXED = "fixed"
    FLEXIBLE = "flexible"


class MBPPhase(str, Enum):
    SAFETY = "safety"           # Phase 0: Safety & Context Screening
    CORE = "core"               # Phase 1: Core Questioning
    PROBING = "probing"         # Phase 2: Adaptive Probing
    MINING = "mining"           # Phase 3: Adaptation Pattern Mining
    VALIDATION = "validation"   # Phase 4: Cross-Validation
    SYNTHESIS = "synthesis"     # Phase 5: Structural Synthesis (no questions)
    CLOSURE = "closure"         # Phase 6: Debriefing & Closure


@dataclass
class Question:
    """Question template structure"""
    question_id: str
    phase: str
    type: QuestionType
    text: str
    dimensions: List[str] = field(default_factory=list)
    order: int = 0
    sub_questions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "id": self.question_id,  # Alias for frontend compatibility
            "phase": self.phase,
            "phase_number": self.get_phase_number(),
            "type": self.type.value,
            "text": self.text,
            "dimensions": self.dimensions,
            "order": self.order,
            "sub_questions": self.sub_questions
        }
    
    def get_phase_number(self) -> int:
        """Get phase number from phase name"""
        phase_map = {
            "safety": 0,
            "core": 1,
            "probing": 2,
            "mining": 3,
            "validation": 4,
            "synthesis": 5,
            "closure": 6,
        }
        return phase_map.get(self.phase, 0)


# ============ PHASE 0: SAFETY & CONTEXT SCREENING ============
# Ratio: Fixed 100% | Flexible 0%
PHASE_0_QUESTIONS = [
    Question(
        question_id="q0.1",
        phase="safety",
        type=QuestionType.FIXED,
        order=1,
        text="Sebelum kita mulai, ada beberapa hal yang perlu dipastikan. Saat ini, apakah kamu merasa cukup stabil secara emosional untuk membahas hal-hal personal? Ada situasi krisis atau trauma baru-baru ini yang sedang kamu hadapi?",
        dimensions=["Safety"]
    ),
    Question(
        question_id="q0.2",
        phase="safety",
        type=QuestionType.FIXED,
        order=2,
        text="Kalau nanti dalam percakapan ini ada hal yang mengganggu atau memicu emosi, siapa yang bisa kamu hubungi setelahnya? Apakah kamu punya akses ke support system saat ini?",
        dimensions=["Safety", "SupportSystem"]
    ),
    Question(
        question_id="q0.3",
        phase="safety",
        type=QuestionType.FIXED,
        order=3,
        text="Proses ini akan mengeksplorasi pola perilaku dan struktur adaptasimu. Terkadang ini bisa memunculkan hal yang tidak nyaman. Kamu punya hak untuk berhenti kapan saja. Apakah kamu setuju untuk melanjutkan?",
        dimensions=["Safety", "InformedConsent"]
    ),
    Question(
        question_id="q0.4",
        phase="safety",
        type=QuestionType.FIXED,
        order=4,
        text="Coba gambarkan lingkungan tempat kamu dibesarkan — bukan lokasi geografisnya, tapi 'aturan main' yang kamu pelajari untuk survive. Apa yang 'dibutuhkan' dari kamu di situ untuk aman/diterima?",
        dimensions=["CFV", "CRF", "RSI"]
    ),
    Question(
        question_id="q0.5",
        phase="safety",
        type=QuestionType.FIXED,
        order=5,
        text="Bagaimana pola komunikasi dengan orang tuamu saat kamu kecil — bukan apa yang mereka *ajar*, tapi apa yang mereka *modelkan* tentang cara mengekspresikan butuh, marah, atau sedih?",
        dimensions=["ARP", "EG", "VB"]
    ),
    Question(
        question_id="q0.6",
        phase="safety",
        type=QuestionType.FIXED,
        order=6,
        text="Kapan pertama kali kamu sadar bahwa dunia nggak aman/damai — dan apa yang kamu mulai lakukan berbeda setelah itu untuk menjaga diri?",
        dimensions=["CDI", "StressResponse", "ASC"]
    ),
    Question(
        question_id="q0.7",
        phase="safety",
        type=QuestionType.FIXED,
        order=7,
        text="Latar belakang keluargamu secara kultural seperti apa? Ada ekspektasi atau norma tertentu yang memengaruhi cara kamu melihat diri sendiri?",
        dimensions=["CulturalFrame"]
    ),
]


# ============ PHASE 1: CORE QUESTIONING ============
# Ratio: Fixed 70% | Flexible 30%
PHASE_1_QUESTIONS = [
    Question(
        question_id="q1.1",
        phase="core",
        type=QuestionType.FIXED,
        order=1,
        text="Kalau disuruh deskripsikan dirimu dalam 3 kata, apa yang kamu pilih? ... Sekarang, bagian mana dari dirimu yang paling bertentangan dengan ketiga kata itu?",
        dimensions=["CFV", "CRF", "ASC"]
    ),
    Question(
        question_id="q1.2",
        phase="core",
        type=QuestionType.FIXED,
        order=2,
        text="Kalau bisa kasih advice ke dirimu 5 tahun lalu, apa yang kamu bilang? ... Terus kenapa advice yang sama nggak kamu apply sekarang?",
        dimensions=["ASC", "COI", "CDI", "CRF"]
    ),
    Question(
        question_id="q1.3",
        phase="core",
        type=QuestionType.FIXED,
        order=3,
        text="Di kantor/professional setting, kamu tipe yang gimana? ... Di rumah sama keluarga/dekat, apakah sama persis atau ada bedanya? Ceritain perbedaannya.",
        dimensions=["RSI", "Compartmentalization", "VB", "AB"]
    ),
    Question(
        question_id="q1.4",
        phase="core",
        type=QuestionType.FIXED,
        order=4,
        text="Sifat apa yang paling kamu benci dari orang lain? ... Pernah nggak kamu sadar kalau sebenarnya kamu juga punya sifat itu, meski dalam bentuk berbeda?",
        dimensions=["Projection", "Shadow", "CFV"]
    ),
    Question(
        question_id="q1.5",
        phase="core",
        type=QuestionType.FIXED,
        order=5,
        text="Saat ada konflik atau ketidaksetujuan, insting pertama kamu apa — menghindar, membela diri, mencari solusi, atau yang lain? Coba ceritain satu contoh konkret.",
        dimensions=["ARP", "COI", "RSI", "StressResponse"]
    ),
    Question(
        question_id="q1.6",
        phase="core",
        type=QuestionType.FIXED,
        order=6,
        text="Bagaimana perasaanmu saat seseorang yang lebih berotoritas (atasan, orang tua, figure of authority) menolak ide atau usulanmu? Apa yang tubuhmu rasakan di saat itu?",
        dimensions=["ARP", "RS", "EmotionalStructure", "StressResponse"]
    ),
    Question(
        question_id="q1.7",
        phase="core",
        type=QuestionType.FIXED,
        order=7,
        text="Kamu bilang decision-making mu sangat logical/analytical. Coba ceritain decision terbesar akhir tahun ini — apa yang tubuhmu rasakan 5 detik sebelum kamu bilang 'yes'?",
        dimensions=["AB", "StressResponse", "CognitiveClaim"]
    ),
    Question(
        question_id="q1.8",
        phase="core",
        type=QuestionType.FIXED,
        order=8,
        text="Kalau disuruh urutkan: Comfort, Growth, Recognition, Stability — urutannya gimana? ... Terus keputusan terakhir yang melawan ranking itu kapan dan kenapa?",
        dimensions=["COI", "CFV", "ASC"]
    ),
    Question(
        question_id="q1.9",
        phase="core",
        type=QuestionType.FIXED,
        order=9,
        text="Apa keputusan yang paling kamu sesali dalam 5 tahun terakhir? ... Kalau diulang situasinya dengan 'kamu yang sekarang', apa yang bakal kamu lakukan berbeda?",
        dimensions=["CDI", "CRF", "COI", "CFV"]
    ),
    Question(
        question_id="q1.10",
        phase="core",
        type=QuestionType.FIXED,
        order=10,
        text="Kapan terakhir kali kamu merasa 'flow' — benar-benar asyik, waktu berlalu tanpa kamu sadari, nggak capek meski lama? Apa yang sedang kamu lakukan?",
        dimensions=["ASC", "CoreDrive", "AB"]
    ),
    Question(
        question_id="q1.11",
        phase="core",
        type=QuestionType.FIXED,
        order=11,
        text="Kegiatan atau situasi seperti apa yang paling membuatmu merasa 'habis' — bukan capek fisik, tapi empty/drained?",
        dimensions=["AdaptationCost", "Suppression", "RSI"]
    ),
]


# ============ PHASE 2: ADAPTIVE PROBING ============
# Ratio: Fixed 20% | Flexible 80%
PHASE_2_QUESTIONS = [
    Question(
        question_id="q2.1",
        phase="probing",
        type=QuestionType.FIXED,
        order=1,
        text="Berdasarkan apa yang kamu ceritakan sejauh ini, saya ada hipotesis sementara: [AI_GENERATED_HYPOTHESIS]. Apakah ini resonate dengan yang kamu rasakan, atau ada yang miss?",
        dimensions=["Validation", "Hypothesis"]
    ),
    Question(
        question_id="q2.2",
        phase="probing",
        type=QuestionType.FIXED,
        order=2,
        text="Coba kita test dari sudut berlawanan. Kalau ada yang bilang [AI_GENERATED_CONTRA], apa argumen yang mendukung pandangan itu tentang kamu?",
        dimensions=["DevilsAdvocate", "SelfAwareness"]
    ),
    Question(
        question_id="q2.3",
        phase="probing",
        type=QuestionType.FIXED,
        order=3,
        text="Kalau harus pilih: Diabaikan oleh teman dekat vs Dikritik di depan publik — mana yang lebih menyakitkan dan kenapa?",
        dimensions=["RS", "ARP", "VB"]
    ),
]

# Flexible question templates for Phase 2
PHASE_2_FLEXIBLE_TEMPLATES = {
    "family_origin": "Kapan pertama kali kamu sadar harus jadi 'orang yang [PATTERN]' di keluarga?",
    "attachment_safety": "Saat membicarakan [RELATIONSHIP], apa yang tubuhmu rasakan?",
    "validation_seeking": "Seberapa penting pendapat [GROUP] bagi kamu? Kapan itu mulai jadi penting?",
    "processing_style": "Kamu lebih sering 'tahu' jawabannya dulu atau 'merasakan' dulu?",
    "emotional_expression": "Kapan terakhir kali kamu bener-bener [EMOTION]? Bukan annoyed, tapi [INTENSIFIED].",
    "defense_mechanism": "Kapan kamu mulai belajar bahwa [BEHAVIOR] adalah cara yang aman?",
    "identity_construction": "Siapa yang pertama kali 'menamai' kamu sebagai [IDENTITY_LABEL]?",
    "survival_rule": "Apa 'aturan tak tertulis' yang kamu pelajari untuk survive di [ENVIRONMENT]?",
    "cost_identification": "Hal apa yang paling sering kamu sacrifice untuk maintain [PATTERN]?",
}


# ============ PHASE 3: ADAPTATION PATTERN MINING ============
# Ratio: Fixed 0% | Flexible 100%
# All questions are AI-generated based on patterns
PHASE_3_FLEXIBLE_CATEGORIES = {
    "body_signal": "Kapan tubuhmu bereaksi sebelum pikiranmu proses? Apa yang tubuhmu 'tahu' lebih dulu?",
    "physiological_anchors": "Di situasi seperti apa kamu notice [tension/knot in stomach/shallow breathing] muncul?",
    "energy_shifts": "Apa yang biasanya terjadi 5 menit sebelum kamu merasa [drained/overwhelmed/withdrawn]?",
    "relational_role": "Posisi apa yang selalu kamu tempati dalam dinamika keluarga/teman? Pernah coba 'keluar' dari peran itu?",
    "need_expression": "Bagaimana caramu mengekspresikan butuh/bantuan saat kecil? Apa yang terjadi saat kamu coba?",
    "intimacy_regulation": "Seberapa dekat orang bisa mendekat sebelum kamu merasa harus [menarik diri/menjaga jarak]?",
    "survival_rule_extraction": "Kalau ada satu 'aturan' yang kamu pelajari untuk aman di dunia, apa itu? Dari mana datangnya?",
    "identity_preservation": "Bagian dari dirimu apa yang paling kamu proteksi dari orang lain? Kenapa itu perlu dijaga?",
    "pattern_breakdown_fear": "Apa yang paling kamu takutkan kalau kamu berhenti jadi 'orang yang [PATTERN]'?",
    "maintenance_cost": "Hal apa yang paling sering kamu korbankan untuk tetap jadi [IDENTITY_CLAIM]?",
    "exhaustion_pattern": "Kapan pattern ini nggak 'work' lagi? Apa yang terjadi saat itu?",
    "forbidden_self": "Bagian dirimu apa yang paling kamu hindari untuk jadi? Kenapa itu forbidden?",
}


# ============ PHASE 4: CROSS-VALIDATION ============
# Ratio: Fixed 50% | Flexible 50%
PHASE_4_QUESTIONS = [
    Question(
        question_id="q4.1",
        phase="validation",
        type=QuestionType.FIXED,
        order=1,
        text="Tadi kamu bilang paling benci [TRAIT] di orang lain. Tapi di bagian regret, kamu juga mention [RELATED_BEHAVIOR]. Apa hubungan antara keduanya?",
        dimensions=["Projection", "ShadowAwareness"]
    ),
    Question(
        question_id="q4.2",
        phase="validation",
        type=QuestionType.FIXED,
        order=2,
        text="Saat konflik dengan selevel, kamu [STYLE_A]. Tapi dengan authority, kamu [STYLE_B]. Apa yang beda dari kedua situasi itu yang bikin responsmu beda?",
        dimensions=["ARP", "COI", "PowerDynamics"]
    ),
    Question(
        question_id="q4.3",
        phase="validation",
        type=QuestionType.FIXED,
        order=3,
        text="Kamu bisa bedain [X] emotion types (high EG), tapi tadi bilang nggak pernah share [DEEP_FEELING] ke siapapun (low VB). Apa yang bikin beda antara 'tahu' dan 'bagi'?",
        dimensions=["EG", "VB", "AwarenessExpressionGap"]
    ),
    Question(
        question_id="q4.4",
        phase="validation",
        type=QuestionType.FIXED,
        order=4,
        text="Kamu bilang takut akan [FEAR]. Tapi pattern kontrolmu adalah [CONTROL_STYLE]. Apa yang terjadi kalau strategi kontrol itu gagal menghalangi [FEAR]?",
        dimensions=["COI", "StressResponse", "CoreWound"]
    ),
    Question(
        question_id="q4.5",
        phase="validation",
        type=QuestionType.FIXED,
        order=5,
        text="Kamu identify sebagai [IDENTITY]. Tapi tadi cerita bahwa untuk jadi itu, kamu harus [COST]. Apakah identity-nya tetap worth it dengan harga itu?",
        dimensions=["ASC", "IdentityFusion"]
    ),
]

# Flexible cross-validation templates
PHASE_4_FLEXIBLE_TEMPLATES = {
    "ab_stress": "Kamu bilang analytical, tapi tubuhmu freeze. Apa yang analytical mind-nya lakukan saat tubuh freeze?",
    "eg_vb": "Kamu tahu persis apa yang dirasakan, tapi nggak pernah express. Apa yang terjadi dengan emosi yang 'tahu' tapi nggak 'keluar'?",
    "rs_arp": "Kamu butuh recognition, tapi response ke authority adalah [dominance/rebellion]. Bagaimana cara kamu dapat recognition tanpa terlihat butuh?",
    "asc_emotional": "Kamu bilang [ADAPTATION] adalah strength. Tapi ada cost [EMOTIONAL]. Apakah ini genuine strength atau glorified survival?",
    "temporal": "5 tahun lalu kamu [X], sekarang [Y]. Evolusi atau reaksi?",
    "contextual": "Di kantor [A], di rumah [B]. Apakah ini dua 'kamu' yang berbeda, atau satu kamu dengan mask berbeda?",
    "value_behavior": "Kamu bilang value [X] paling penting, tapi decision terakhir [Y]. Apa yang lebih powerful dari value di saat itu?",
    "claim_reality": "Kamu bilang [CLAIM], tapi contoh yang kamu ceritakan menunjukkan [REALITY]. Help me understand the gap.",
    "integration_coherent": "Apakah kamu merasa semua bagian ini adalah 'satu kesatuan' yang nyambung?",
    "integration_compartmentalized": "Apakah ada 'kamu' yang beda untuk konteks berbeda? Mereka tahu satu sama lain?",
    "integration_conflicted": "Apakah ada dua 'bagian' dalam dirimu yang sering bertentangan? Apa yang mereka perjuangkan masing-masing?",
}


# ============ PHASE 5: STRUCTURAL SYNTHESIS ============
# Ratio: Fixed 0% | Flexible 0%
# NO QUESTIONS - Internal analysis phase


# ============ PHASE 6: DEBRIEFING & CLOSURE ============
# Ratio: Fixed 60% | Flexible 40%
PHASE_6_QUESTIONS = [
    Question(
        question_id="q6.1",
        phase="closure",
        type=QuestionType.FIXED,
        order=1,
        text="Kita akan segera selesai. Coba tarik napas dalam... kembali ke ruangan ini, ke waktu sekarang. Apa yang kamu lihat di sekitarmu saat ini?",
        dimensions=["Grounding", "Presence"]
    ),
    Question(
        question_id="q6.2",
        phase="closure",
        type=QuestionType.FIXED,
        order=2,
        text="Dari semua yang kita bahas, apa yang paling resonate dengan kamu? Apa yang paling tidak sesuai atau perlu ditolak?",
        dimensions=["SubjectiveValidation"]
    ),
    Question(
        question_id="q6.3",
        phase="closure",
        type=QuestionType.FIXED,
        order=3,
        text="Apa yang membuatmu merasa aman, kuat, atau grounded? Bisa tempat, orang, aktivitas, atau hal sederhana lainnya.",
        dimensions=["ResourceActivation"]
    ),
    Question(
        question_id="q6.4",
        phase="closure",
        type=QuestionType.FIXED,
        order=4,
        text="Apa satu insight atau pemahaman baru yang kamu bawa pulang dari sesi ini?",
        dimensions=["InsightCapture"]
    ),
    Question(
        question_id="q6.5",
        phase="closure",
        type=QuestionType.FIXED,
        order=5,
        text="Apa yang perlu kamu lakukan setelah ini untuk merawat diri? Ada yang perlu disiapkan atau dihindari?",
        dimensions=["NextSteps"]
    ),
    Question(
        question_id="q6.6",
        phase="closure",
        type=QuestionType.FIXED,
        order=6,
        text="Proses ini selesai. Apa yang kita lakukan adalah eksplorasi, bukan diagnosis. Kamu punya otoritas penuh atas interpretasi dirimu sendiri. Ada yang mau ditanyakan sebelum kita tutup?",
        dimensions=["Closure", "Authorization"]
    ),
]

# Flexible closure templates for crisis/activation situations
PHASE_6_FLEXIBLE_TEMPLATES = {
    "distressed": "Saya notice kamu terlihat [STATE]. Apa yang bisa saya bantu saat ini?",
    "activated": "Jika emosi ini terus berlanjut, siapa yang bisa kamu hubungi?",
    "overwhelmed": "Mari kita grounding dulu. Coba sebutkan 3 hal yang kamu lihat, 2 yang kamu dengar, 1 yang kamu rasakan.",
    "suppression_pattern": "Bagaimana cara yang aman untuk kamu melepaskan sedikit tekanan tanpa harus explode?",
    "low_support": "Di mana kamu bisa menemukan 'safe space' meski kecil?",
    "high_cost": "Bagian kecil apa yang bisa kamu 'kembalikan' ke dirimu sendiri minggu ini?",
    "identity_confusion": "Tanpa harus define siapa kamu, apa yang kamu butuhkan saat ini?",
}


# ============ QUESTION MANAGER ============

class QuestionManager:
    """Manages questions for all phases of MBP"""
    
    PHASE_QUESTIONS = {
        "safety": PHASE_0_QUESTIONS,
        "core": PHASE_1_QUESTIONS,
        "probing": PHASE_2_QUESTIONS,
        "validation": PHASE_4_QUESTIONS,
        "closure": PHASE_6_QUESTIONS,
    }
    
    FLEXIBLE_TEMPLATES = {
        "probing": PHASE_2_FLEXIBLE_TEMPLATES,
        "mining": PHASE_3_FLEXIBLE_CATEGORIES,
        "validation": PHASE_4_FLEXIBLE_TEMPLATES,
        "closure": PHASE_6_FLEXIBLE_TEMPLATES,
    }
    
    # Phase order for progression
    PHASE_ORDER = [
        "safety",      # Phase 0
        "core",        # Phase 1
        "probing",     # Phase 2
        "mining",      # Phase 3
        "validation",  # Phase 4
        "synthesis",   # Phase 5 (no questions)
        "closure",     # Phase 6
    ]
    
    @classmethod
    def get_phase_questions(cls, phase: str) -> List[Question]:
        """Get all fixed questions for a phase"""
        return cls.PHASE_QUESTIONS.get(phase, [])
    
    @classmethod
    def get_question_by_id(cls, phase: str, question_id: str) -> Optional[Question]:
        """Get a specific question by ID"""
        questions = cls.get_phase_questions(phase)
        for q in questions:
            if q.question_id == question_id:
                return q
        return None
    
    @classmethod
    def get_next_phase(cls, current_phase: str) -> Optional[str]:
        """Get the next phase in sequence"""
        try:
            idx = cls.PHASE_ORDER.index(current_phase)
            if idx < len(cls.PHASE_ORDER) - 1:
                return cls.PHASE_ORDER[idx + 1]
        except ValueError:
            pass
        return None
    
    @classmethod
    def get_fixed_question_count(cls, phase: str) -> int:
        """Get number of fixed questions for a phase"""
        return len(cls.get_phase_questions(phase))
    
    @classmethod
    def has_fixed_questions(cls, phase: str) -> bool:
        """Check if phase has fixed questions"""
        return phase in cls.PHASE_QUESTIONS and len(cls.PHASE_QUESTIONS[phase]) > 0
    
    @classmethod
    def is_flexible_only_phase(cls, phase: str) -> bool:
        """Check if phase is 100% flexible (AI-generated questions)"""
        return phase in ["mining", "synthesis"]
    
    @classmethod
    def get_flexible_templates(cls, phase: str) -> Dict[str, str]:
        """Get flexible question templates for a phase"""
        return cls.FLEXIBLE_TEMPLATES.get(phase, {})


# Export all questions
def get_all_questions() -> Dict[str, List[Question]]:
    """Get all questions organized by phase"""
    return {
        "safety": PHASE_0_QUESTIONS,
        "core": PHASE_1_QUESTIONS,
        "probing": PHASE_2_QUESTIONS,
        "validation": PHASE_4_QUESTIONS,
        "closure": PHASE_6_QUESTIONS,
    }