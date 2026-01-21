"""
AI Hackathon Judge System - Configuration Settings

This module contains all configurable parameters for the judging system,
including scoring criteria weights, penalty thresholds, and keyword lists.
"""

from typing import Dict, List, Tuple


# =============================================================================
# SCORING CRITERIA WEIGHTS (Must sum to 100)
# =============================================================================

SCORING_CRITERIA: Dict[str, Dict] = {
    "innovation": {
        "name": "Innovation & Originality",
        "weight": 25,
        "description": "How unique and creative is the solution? Does it bring something new to the table?",
        "icon": "💡"
    },
    "technical_depth": {
        "name": "Technical Depth",
        "weight": 20,
        "description": "How sophisticated is the technical implementation? Is there real engineering effort?",
        "icon": "⚙️"
    },
    "problem_relevance": {
        "name": "Problem Relevance",
        "weight": 15,
        "description": "How important is the problem being solved? Does it address a real need?",
        "icon": "🎯"
    },
    "feasibility": {
        "name": "Feasibility",
        "weight": 15,
        "description": "Can this project actually be built and deployed in the real world?",
        "icon": "🔧"
    },
    "scalability": {
        "name": "Scalability",
        "weight": 10,
        "description": "Can the solution scale to handle growth? Is the architecture extensible?",
        "icon": "📈"
    },
    "ui_ux": {
        "name": "UI/UX & Presentation",
        "weight": 10,
        "description": "How well-designed is the user interface? Is it intuitive and polished?",
        "icon": "🎨"
    },
    "real_world_impact": {
        "name": "Real-World Impact",
        "weight": 5,
        "description": "What tangible impact could this have on users or society?",
        "icon": "🌍"
    }
}


# =============================================================================
# VERDICT THRESHOLDS
# =============================================================================

VERDICT_THRESHOLDS: Dict[str, Tuple[int, int, str, str]] = {
    # (min_score, max_score, verdict, emoji)
    "winner": (85, 100, "Winner Material", "🏆"),
    "strong": (70, 84, "Strong Contender", "✅"),
    "average": (50, 69, "Average", "⚠️"),
    "not_ready": (0, 49, "Not Hackathon Ready", "❌")
}


# =============================================================================
# BUZZWORD DETECTION
# =============================================================================

BUZZWORDS: List[str] = [
    "revolutionary", "disruptive", "game-changing", "world-changing",
    "cutting-edge", "state-of-the-art", "next-generation", "groundbreaking",
    "paradigm shift", "synergy", "leverage", "ecosystem", "holistic",
    "seamless", "robust", "scalable", "innovative", "transformative",
    "best-in-class", "world-class", "unprecedented", "unique", "novel",
    "breakthrough", "pioneering", "trailblazing", "bleeding-edge",
    "AI-powered", "blockchain-enabled", "cloud-native", "future-proof",
    "mission-critical", "enterprise-grade", "industry-leading"
]

# Maximum allowed buzzword density (buzzwords per 100 words)
MAX_BUZZWORD_DENSITY = 5.0

# Penalty per excess buzzword (percentage points)
BUZZWORD_PENALTY = 2.0


# =============================================================================
# VAGUENESS DETECTION
# =============================================================================

VAGUE_PHRASES: List[str] = [
    "and more", "etc.", "various", "multiple", "several", "many",
    "some kind of", "sort of", "kind of", "basically", "essentially",
    "generally", "typically", "usually", "often", "sometimes",
    "might", "could potentially", "may be able to", "possibly",
    "in some cases", "under certain conditions", "as needed",
    "when appropriate", "if necessary", "as applicable",
    "and so on", "and stuff", "things like", "or something",
    "whatever", "somehow", "somewhere", "something", "anything"
]

# Penalty for vague descriptions (percentage points per vague phrase)
VAGUENESS_PENALTY = 1.5


# =============================================================================
# OVERCLAIMING DETECTION
# =============================================================================

OVERCLAIM_PHRASES: List[str] = [
    "will change the world", "will revolutionize", "first ever",
    "never been done before", "completely unique", "100% original",
    "no competition", "unmatched", "unparalleled", "unprecedented success",
    "guaranteed to", "will definitely", "proven to", "scientifically proven",
    "backed by research", "studies show", "experts agree",
    "millions of users", "billion dollar", "unicorn potential",
    "viral growth", "exponential", "hockey stick growth"
]

# Penalty for overclaiming (percentage points per overclaim)
OVERCLAIM_PENALTY = 3.0


# =============================================================================
# POSITIVE SIGNALS (BOOST SCORE)
# =============================================================================

TECHNICAL_DEPTH_SIGNALS: List[str] = [
    "algorithm", "architecture", "api", "database", "optimization",
    "performance", "latency", "throughput", "caching", "indexing",
    "authentication", "authorization", "encryption", "security",
    "testing", "unit test", "integration test", "ci/cd", "deployment",
    "monitoring", "logging", "error handling", "edge cases",
    "data structure", "time complexity", "space complexity",
    "microservices", "containerization", "kubernetes", "docker",
    "rest api", "graphql", "websocket", "real-time",
    "machine learning", "neural network", "model training", "inference"
]

FEASIBILITY_SIGNALS: List[str] = [
    "prototype", "mvp", "working demo", "implemented", "built",
    "deployed", "tested", "validated", "user feedback", "iteration",
    "sprint", "milestone", "roadmap", "timeline", "budget",
    "resource", "constraint", "limitation", "trade-off", "decision"
]

INNOVATION_SIGNALS: List[str] = [
    "novel approach", "new method", "unique combination", "fresh perspective",
    "different from", "improves upon", "addresses gap", "solves differently",
    "creative solution", "unconventional", "out-of-the-box", "reimagined"
]


# =============================================================================
# AI-GENERATED TEXT DETECTION PATTERNS
# =============================================================================

AI_GENERATED_PATTERNS: List[str] = [
    "in conclusion", "it is important to note", "it is worth noting",
    "in this regard", "in the realm of", "in today's world",
    "at the end of the day", "moving forward", "going forward",
    "with that being said", "having said that", "that being said",
    "as we can see", "as mentioned earlier", "as discussed above",
    "furthermore", "moreover", "additionally", "subsequently",
    "in summary", "to summarize", "in essence", "ultimately",
    "delve into", "dive deeper", "explore further", "shed light on",
    "it's important to", "we need to", "one must", "we should"
]

# Penalty for suspected AI-generated content
AI_GENERATED_PENALTY = 5.0


# =============================================================================
# PROJECT COMPLEXITY LEVELS
# =============================================================================

COMPLEXITY_LEVELS = {
    "beginner": {
        "team_size_range": (1, 2),
        "expected_tech_count": (1, 3),
        "score_multiplier": 1.1,  # Slight boost for beginners doing well
        "description": "Early-stage developers learning the ropes"
    },
    "intermediate": {
        "team_size_range": (2, 4),
        "expected_tech_count": (3, 6),
        "score_multiplier": 1.0,
        "description": "Experienced developers with solid foundations"
    },
    "advanced": {
        "team_size_range": (3, 6),
        "expected_tech_count": (5, 10),
        "score_multiplier": 0.95,  # Slightly higher expectations
        "description": "Expert developers expected to deliver excellence"
    }
}


# =============================================================================
# TECH STACK CATEGORIES
# =============================================================================

TECH_CATEGORIES = {
    "frontend": ["react", "vue", "angular", "svelte", "next.js", "nuxt", "html", "css", "javascript", "typescript", "tailwind", "bootstrap"],
    "backend": ["node.js", "express", "django", "flask", "fastapi", "spring", "rails", "laravel", "go", "rust", "java", "python", "php"],
    "database": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "firebase", "supabase", "sqlite", "dynamodb", "cassandra"],
    "ml_ai": ["tensorflow", "pytorch", "scikit-learn", "keras", "huggingface", "openai", "langchain", "opencv", "nltk", "spacy"],
    "cloud": ["aws", "gcp", "azure", "vercel", "netlify", "heroku", "digitalocean", "cloudflare", "docker", "kubernetes"],
    "mobile": ["react native", "flutter", "swift", "kotlin", "ionic", "expo"],
    "other": ["graphql", "websocket", "grpc", "kafka", "rabbitmq", "celery", "stripe", "twilio", "sendgrid"]
}


# =============================================================================
# FEEDBACK TEMPLATES
# =============================================================================

FEEDBACK_TEMPLATES = {
    "strength_intro": [
        "This project shines in several areas:",
        "Notable strengths include:",
        "What works well:",
        "Impressive aspects of this submission:"
    ],
    "weakness_intro": [
        "Areas that need improvement:",
        "Critical gaps identified:",
        "What's holding this project back:",
        "Concerns from the judging panel:"
    ],
    "suggestion_intro": [
        "To take this project to the next level:",
        "Recommendations for improvement:",
        "If I were mentoring this team, I'd suggest:",
        "Here's how to make this a winner:"
    ],
    "winner_verdict": [
        "This is genuinely impressive work. The team has demonstrated real engineering depth and a clear understanding of the problem space.",
        "A standout submission that showcases both innovation and execution. This is what hackathon winners look like.",
        "Exceptional work. This project demonstrates the rare combination of creativity, technical skill, and real-world applicability."
    ],
    "strong_verdict": [
        "Solid work overall. With some refinement, this could be a serious contender.",
        "This project has real potential. The foundation is strong, and the team clearly knows what they're doing.",
        "Good execution on an interesting problem. A few improvements could push this into winner territory."
    ],
    "average_verdict": [
        "This project has promise but needs significant work before it's ready for primetime.",
        "The idea is there, but the execution doesn't quite match the ambition.",
        "More substance and less fluff would help this project stand out."
    ],
    "not_ready_verdict": [
        "This submission needs fundamental rethinking. The current approach has too many gaps.",
        "Back to the drawing board. The project lacks the depth and clarity expected at this level.",
        "Not ready for competition. Focus on building a working prototype before presenting."
    ]
}


# =============================================================================
# UI CONFIGURATION
# =============================================================================

UI_CONFIG = {
    "page_title": "🏆 AI Hackathon Judge",
    "page_icon": "🏆",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "theme_colors": {
        "primary": "#6366f1",
        "secondary": "#8b5cf6",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "background_dark": "#0f172a",
        "background_light": "#f8fafc",
        "card_dark": "#1e293b",
        "card_light": "#ffffff"
    }
}
