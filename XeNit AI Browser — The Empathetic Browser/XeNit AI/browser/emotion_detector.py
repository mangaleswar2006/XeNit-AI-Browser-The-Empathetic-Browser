"""
XeNit AI — Emotion Detection Module
Level 1: Keyword-based emotion detection
Level 2: VADER sentiment analysis (if available)
"""

# Level 2: Try to import VADER for sentiment analysis
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
except ImportError:
    _vader = None
    VADER_AVAILABLE = False
    print("XeNit Emotion: vaderSentiment not installed. Using keyword-only detection.")


# ── Level 1: Keyword Lists ──────────────────────────────────────────────────

DISTRESS_KEYWORDS = [
    # Sadness / Depression
    "sad", "depressed", "depression", "hopeless", "worthless", "crying",
    "unhappy", "miserable", "heartbroken", "grief", "grieving", "empty",
    # Loneliness
    "lonely", "alone", "isolated", "no friends", "nobody cares", "no one",
    # Anxiety / Stress
    "anxious", "anxiety", "stressed", "panic", "panicking", "nervous",
    "overwhelmed", "worried", "can't sleep", "insomnia", "restless",
    # Fatigue
    "tired", "exhausted", "fatigue", "burnout", "burned out", "drained",
    # Anger / Frustration
    "angry", "frustrated", "furious", "irritated", "mad",
    # Fear
    "scared", "afraid", "terrified", "fearful",
    # Self-harm (CRITICAL — always trigger support mode)
    "hurt myself", "self harm", "suicide", "suicidal", "kill myself",
    "don't want to live", "end my life", "no reason to live",
]

CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life",
    "don't want to live", "no reason to live", "self harm", "hurt myself",
]

POSITIVE_KEYWORDS = [
    "happy", "great", "amazing", "wonderful", "fantastic", "good",
    "excited", "joyful", "grateful", "thankful", "blessed", "cheerful",
    "love", "loving", "proud", "confident", "relaxed", "calm",
]

TOXIC_KEYWORDS = [
    "stupid", "idiot", "hate you", "shut up", "dumb", "fool", "useless",
    "kill yourself", "die", "crazy", "nasty", "ignorant", "loser",
    "anger", "furious", "mad", "rage", "disgust", "awful", "terrible",
    "abusive", "horrible", "pathetic", "worthless", "scum", "trash",
    "shut your mouth", "you are nothing", "get lost"
] # Expanded list for Toxicity Blocker

# ── Emotion Result ───────────────────────────────────────────────────────────

class EmotionResult:
    """Holds detected emotion data."""
    def __init__(self):
        self.mood = "neutral"          # "distress", "crisis", "positive", "neutral", "anger"
        self.confidence = 0.0          # 0.0 - 1.0
        self.matched_keywords = []     # Level 1 hits
        self.vader_score = None        # Level 2 compound score (-1 to +1)
        self.source = "none"           # "keyword", "vader", "both"

    @property
    def needs_comfort(self):
        """True if the AI should switch to Comfort + Support mode."""
        return self.mood in ("distress", "crisis")

    @property
    def is_crisis(self):
        """True if potential self-harm / suicidal language detected."""
        return self.mood == "crisis"

    def __repr__(self):
        return f"Emotion(mood={self.mood}, confidence={self.confidence:.2f}, source={self.source})"


# ── Detection Engine ─────────────────────────────────────────────────────────

def detect_emotion(text: str) -> EmotionResult:
    """
    Analyze user text and return an EmotionResult.
    Combines Level 1 (keyword) and Level 2 (VADER) when available.
    """
    result = EmotionResult()
    lower = text.lower()

    # ── Level 1: Keyword scan ────────────────────────────────────────────
    crisis_hits = [kw for kw in CRISIS_KEYWORDS if kw in lower]
    toxic_hits = [kw for kw in TOXIC_KEYWORDS if kw in lower]
    distress_hits = [kw for kw in DISTRESS_KEYWORDS if kw in lower]
    positive_hits = [kw for kw in POSITIVE_KEYWORDS if kw in lower]

    if crisis_hits:
        result.mood = "crisis"
        result.matched_keywords = crisis_hits
        result.confidence = 1.0
        result.source = "keyword"
        return result
        
    if toxic_hits:
        result.mood = "anger" # Classify toxic/hate as anger for now
        result.matched_keywords = toxic_hits
        result.confidence = 0.95
        result.source = "keyword"
        return result

    keyword_mood = "neutral"
    keyword_conf = 0.0

    if distress_hits:
        keyword_mood = "distress"
        keyword_conf = min(len(distress_hits) * 0.3, 1.0)
        result.matched_keywords = distress_hits
    elif positive_hits:
        keyword_mood = "positive"
        keyword_conf = min(len(positive_hits) * 0.3, 1.0)
        result.matched_keywords = positive_hits

    # ── Level 2: VADER sentiment ─────────────────────────────────────────
    if VADER_AVAILABLE and _vader:
        scores = _vader.polarity_scores(text)
        compound = scores["compound"]
        result.vader_score = compound

        vader_mood = "neutral"
        vader_conf = abs(compound)

        if compound <= -0.3:
            vader_mood = "distress"
        elif compound >= 0.3:
            vader_mood = "positive"

        # ── Combine Level 1 + Level 2 ────────────────────────────────────
        if keyword_mood == vader_mood:
            # Both agree → high confidence
            result.mood = keyword_mood
            result.confidence = min((keyword_conf + vader_conf) / 2 + 0.2, 1.0)
            result.source = "both"
        elif keyword_mood != "neutral":
            # Keywords found but VADER disagrees → trust keywords slightly more
            result.mood = keyword_mood
            result.confidence = keyword_conf * 0.7
            result.source = "keyword"
        elif vader_mood != "neutral":
            # No keywords but VADER detected sentiment
            result.mood = vader_mood
            result.confidence = vader_conf * 0.6
            result.source = "vader"
        else:
            result.mood = "neutral"
            result.confidence = 0.0
            result.source = "both"
    else:
        # Level 2 unavailable — keyword-only
        result.mood = keyword_mood
        result.confidence = keyword_conf
        result.source = "keyword" if keyword_mood != "neutral" else "none"

    return result
