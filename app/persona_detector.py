"""
Persona Detection Module.

Uses a two-pass strategy:
1. Rule-based pre-screening via keyword analysis
2. LLM-based classification with confidence scoring

Personas:
- Technical Expert: Uses technical jargon, asks for logs/APIs/configs
- Frustrated User: Emotional language, urgency, multiple complaints
- Business Executive: Outcome-focused, impact-focused, concise language preference
"""

import re
import json
import logging
from dataclasses import dataclass
from typing import Optional

import google.generativeai as genai

from app.config import config

logger = logging.getLogger(__name__)


@dataclass
class PersonaResult:
    """Result of persona detection."""
    persona: str
    confidence: float          # 0.0 – 1.0
    reasoning: str
    detection_method: str      # "llm", "rule-based", "hybrid"
    signals: dict              # Raw keyword/signal counts


# ──────────────────────────────────────────────────────────────
# Keyword signal dictionaries
# ──────────────────────────────────────────────────────────────

TECHNICAL_KEYWORDS = [
    r"\bapi\b", r"\bsdk\b", r"\brest\b", r"\bgraphql\b", r"\bwebhook\b",
    r"\bauth(?:entication|orization)?\b", r"\bjwt\b", r"\boauth\b",
    r"\btoken\b", r"\bssl\b", r"\btls\b", r"\bssl certificate\b",
    r"\bdebug\b", r"\bstack trace\b", r"\bexception\b", r"\berror code\b",
    r"\blog(?:s)?\b", r"\bconfig(?:uration)?\b", r"\bpayload\b",
    r"\bendpoint\b", r"\brate limit\b", r"\b429\b", r"\b401\b", r"\b403\b",
    r"\b500\b", r"\blatency\b", r"\btimeout\b", r"\bcidr\b", r"\bip whitelist\b",
    r"\bcron\b", r"\bdaemon\b", r"\bcontainer\b", r"\bdocker\b", r"\bkubernetes\b",
    r"\bpostgres(?:ql)?\b", r"\bmysql\b", r"\bmongodb\b", r"\bredis\b",
    r"\bchunk\b", r"\bpagination\b", r"\bcursor\b", r"\bfaiss\b",
    r"\bembedding\b", r"\bvector\b", r"\bllm\b", r"\bintegration\b",
    r"\bsync\b", r"\bpipeline\b", r"\barchitecture\b", r"\binfrastructure\b",
    r"\bdeploy(?:ment)?\b", r"\bci/cd\b", r"\brepository\b", r"\bversion control\b",
    r"\broot cause\b", r"\bdiagnos(?:e|tic)\b", r"\btroubleshoot\b",
    r"\bbackoff\b", r"\bretry\b", r"\bhmac\b", r"\bsha256\b",
]

FRUSTRATED_KEYWORDS = [
    r"\bfrustr(?:ated|ating|ation)\b", r"\bangr(?:y|ily)\b", r"\bupset\b",
    r"\bdisappointed\b", r"\bdisgusted\b", r"\bterrrible\b", r"\bawful\b",
    r"\bworst\b", r"\bunacceptable\b", r"\bridiculous\b", r"\babsurd\b",
    r"\bunbelievable\b", r"\bstill not working\b", r"\bnothing works\b",
    r"\bwon'?t work\b", r"\bdon'?t work\b", r"\bkeep(?:s)? (?:failing|breaking)\b",
    r"\bi'?ve tried\b", r"\bi tried\b", r"\balready tried\b",
    r"\bplease help\b", r"\burgent(?:ly)?\b", r"\basap\b",
    r"\bimmediately\b", r"\bright now\b", r"\bwaiting for\b",
    r"\bwasted\b", r"\bhours?\b", r"\bdays?\b",
    r"\bwhy (?:is|isn'?t|won'?t|doesn'?t|can'?t)\b",
    r"\bhow (?:long|many times)\b", r"\bover and over\b",
    r"\bcompletely broken\b", r"\bnot working at all\b",
    r"!{2,}", r"\bOMG\b", r"\bWTF\b",
]

EXECUTIVE_KEYWORDS = [
    r"\bbusiness impact\b", r"\bbusiness continuity\b",
    r"\brevenue\b", r"\broi\b", r"\bkpi\b",
    r"\boperations?\b", r"\bproductivity\b", r"\befficiency\b",
    r"\bcompliance\b", r"\bgovernance\b", r"\bauditing?\b",
    r"\bstrategic\b", r"\bexecutive\b", r"\bmanagement\b",
    r"\bstakeholder\b", r"\bleadership\b", r"\bboard\b",
    r"\bquarter(?:ly)?\b", r"\bq[1-4]\b", r"\bannual\b",
    r"\bdeadline\b", r"\btimeline\b", r"\bschedule\b",
    r"\bresolution time\b", r"\beta\b", r"\bwhen will\b",
    r"\bsla\b", r"\buptime\b", r"\bavailability\b",
    r"\bcost\b", r"\bbudget\b", r"\bcontract\b",
    r"\bcritical (?:issue|problem|situation)\b",
    r"\bbottom line\b", r"\bhigh level\b", r"\bsummary\b",
    r"\bbrief(?:ing|ly)?\b", r"\bquick(?:ly)?\b",
]


def _count_keyword_matches(text: str, patterns: list[str]) -> int:
    """Count how many keyword patterns match in the text."""
    text_lower = text.lower()
    count = 0
    for pattern in patterns:
        if re.search(pattern, text_lower):
            count += 1
    return count


def _rule_based_classify(message: str) -> tuple[str, dict]:
    """
    Fast rule-based persona classification using keyword matching.
    Returns (persona, signals_dict).
    """
    tech_score = _count_keyword_matches(message, TECHNICAL_KEYWORDS)
    frustrated_score = _count_keyword_matches(message, FRUSTRATED_KEYWORDS)
    exec_score = _count_keyword_matches(message, EXECUTIVE_KEYWORDS)

    # Boost frustrated score for all-caps words and multiple exclamations
    if sum(1 for w in message.split() if w.isupper() and len(w) > 2) >= 2:
        frustrated_score += 2
    if message.count("!") >= 2:
        frustrated_score += 1

    signals = {
        "technical_signals": tech_score,
        "frustrated_signals": frustrated_score,
        "executive_signals": exec_score,
    }

    scores = {
        "Technical Expert": tech_score,
        "Frustrated User": frustrated_score,
        "Business Executive": exec_score,
    }

    # Default to Frustrated User if no strong signal
    if max(scores.values()) == 0:
        return config.persona.default_persona, signals

    return max(scores, key=scores.get), signals


def _build_persona_prompt(message: str, conversation_history: list[dict]) -> str:
    """Build the LLM classification prompt."""
    history_text = ""
    if conversation_history:
        recent = conversation_history[-4:]  # Last 4 turns for context
        history_text = "\n".join([
            f"{'User' if m['role'] == 'user' else 'Agent'}: {m['content'][:200]}"
            for m in recent
        ])

    return f"""You are an expert customer support analyst specialized in identifying customer personas.

Analyze the following customer message (and conversation history if available) and classify the customer into EXACTLY ONE of these three personas:

**Persona Definitions:**

1. **Technical Expert**
   - Uses technical terminology (API, SDK, authentication, logs, config, endpoints, etc.)
   - Asks for detailed technical explanations, root cause analysis, or system-level details
   - Mentions specific error codes, stack traces, or technical configurations
   - Wants step-by-step technical troubleshooting

2. **Frustrated User**
   - Shows emotional distress, frustration, or urgency
   - Uses phrases like "nothing works", "tried everything", "ASAP", "still broken"
   - May have exclamation marks, capitalized words, or desperate tone
   - Repeats complaints or expresses exasperation
   - Needs empathetic, reassuring, simple-language support

3. **Business Executive**
   - Focuses on business outcomes, impact, ROI, operational continuity
   - Asks about timelines, resolution ETAs, SLA commitments
   - Uses business terms: revenue, operations, stakeholders, compliance, productivity
   - Wants concise, high-level answers without technical jargon
   - Concerned about costs, deadlines, and strategic implications

**Conversation History (if any):**
{history_text if history_text else "No prior history — this is the first message."}

**Current Customer Message:**
"{message}"

**Instructions:**
- Analyze tone, vocabulary, urgency level, and focus area
- Consider the full context including conversation history
- Provide a confidence score between 0.0 and 1.0
- Give brief reasoning (1-2 sentences)

**Respond with ONLY valid JSON (no markdown, no extra text):**
{{
  "persona": "<Technical Expert|Frustrated User|Business Executive>",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>"
}}"""


class PersonaDetector:
    """
    Two-pass persona detection:
    1. Fast rule-based keyword analysis
    2. LLM-based classification with confidence scoring
    """

    def __init__(self):
        self._llm_available = False
        self._model = None
        self._init_llm()

    def _init_llm(self):
        """Initialize the LLM for persona classification."""
        try:
            if config.llm.provider == "google" and config.llm.google_api_key:
                genai.configure(api_key=config.llm.google_api_key)
                self._model = genai.GenerativeModel(
                    model_name=config.llm.model_name,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Low temperature for classification
                        max_output_tokens=256,
                    )
                )
                self._llm_available = True
                logger.info("PersonaDetector: LLM initialized (Google Gemini)")
            else:
                logger.warning("PersonaDetector: No LLM configured, using rule-based only")
        except Exception as e:
            logger.error(f"PersonaDetector: LLM init failed: {e}")
            self._llm_available = False

    def detect(
        self,
        message: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> PersonaResult:
        """
        Detect the persona from a user message.

        Args:
            message: The user's current message
            conversation_history: List of past {'role': ..., 'content': ...} dicts

        Returns:
            PersonaResult with persona, confidence, reasoning, and signals
        """
        if conversation_history is None:
            conversation_history = []

        # Pass 1: Rule-based classification
        rule_persona, signals = _rule_based_classify(message)

        # Pass 2: LLM classification (if available)
        if self._llm_available:
            llm_result = self._llm_classify(message, conversation_history)
            if llm_result:
                # Hybrid: combine rule-based signals with LLM judgment
                final_persona = llm_result["persona"]
                confidence = llm_result["confidence"]

                # If LLM confidence is low, use rule-based as tiebreaker
                if confidence < config.persona.llm_confidence_threshold:
                    # Trust rule-based more when LLM is uncertain
                    if rule_persona != final_persona:
                        final_persona = rule_persona
                        confidence = 0.6
                        reasoning = (
                            f"Low LLM confidence ({llm_result['confidence']:.2f}). "
                            f"Rule-based analysis suggests: {rule_persona}. "
                            f"LLM suggested: {llm_result['persona']}."
                        )
                        method = "hybrid"
                    else:
                        reasoning = llm_result["reasoning"]
                        method = "hybrid"
                else:
                    reasoning = llm_result["reasoning"]
                    method = "llm"

                return PersonaResult(
                    persona=final_persona,
                    confidence=confidence,
                    reasoning=reasoning,
                    detection_method=method,
                    signals=signals,
                )

        # Fallback to rule-based only
        max_signal = max(signals.values()) if signals.values() else 0
        confidence = min(0.5 + (max_signal * 0.08), 0.85)

        return PersonaResult(
            persona=rule_persona,
            confidence=confidence,
            reasoning=f"Classified based on keyword analysis: {signals}",
            detection_method="rule-based",
            signals=signals,
        )

    def _llm_classify(
        self,
        message: str,
        conversation_history: list[dict],
    ) -> Optional[dict]:
        """Call LLM for persona classification. Returns None on failure."""
        try:
            prompt = _build_persona_prompt(message, conversation_history)
            response = self._model.generate_content(prompt)
            text = response.text.strip()

            # Strip markdown code blocks if present
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

            result = json.loads(text)

            # Validate response structure
            if "persona" not in result or result["persona"] not in config.persona.personas:
                logger.warning(f"LLM returned invalid persona: {result.get('persona')}")
                return None

            result["confidence"] = float(result.get("confidence", 0.7))
            result["confidence"] = max(0.0, min(1.0, result["confidence"]))

            return result

        except json.JSONDecodeError as e:
            logger.error(f"PersonaDetector: JSON parse error: {e}")
            return None
        except Exception as e:
            logger.error(f"PersonaDetector: LLM call failed: {e}")
            return None


# Module-level singleton
_detector: Optional[PersonaDetector] = None


def get_detector() -> PersonaDetector:
    """Get or create the singleton PersonaDetector."""
    global _detector
    if _detector is None:
        _detector = PersonaDetector()
    return _detector
