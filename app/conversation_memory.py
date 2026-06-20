"""
Conversation Memory Module.

Manages multi-turn conversation history with:
- Sliding window of recent messages
- Per-turn metadata (persona, sources, escalation status)
- Sentiment tracking across turns
- Formatted context for LLM consumption
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Turn:
    """A single conversation turn."""
    role: str                           # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    persona: Optional[str] = None       # Detected persona (user turns)
    persona_confidence: float = 0.0
    sources: list[str] = field(default_factory=list)  # Retrieved doc names
    retrieval_score: float = 0.0        # Best similarity score from retrieval
    escalated: bool = False
    escalation_reason: Optional[str] = None
    sentiment_negative: bool = False    # Whether this turn shows negative sentiment


class ConversationMemory:
    """
    Manages conversation history for multi-turn support sessions.
    """

    def __init__(self, window_size: int = 8):
        self.window_size = window_size
        self.turns: list[Turn] = []
        self.session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.escalated: bool = False
        self.escalation_turn: Optional[int] = None

        # Session-level tracking
        self._low_confidence_streak: int = 0
        self._frustrated_turn_count: int = 0
        self._total_user_turns: int = 0

    # ──────────────────────────────────────────────────────────────
    # Add turns
    # ──────────────────────────────────────────────────────────────

    def add_user_turn(
        self,
        content: str,
        persona: Optional[str] = None,
        persona_confidence: float = 0.0,
        sentiment_negative: bool = False,
    ) -> None:
        """Record a user message."""
        turn = Turn(
            role="user",
            content=content,
            persona=persona,
            persona_confidence=persona_confidence,
            sentiment_negative=sentiment_negative,
        )
        self.turns.append(turn)
        self._total_user_turns += 1

        if sentiment_negative:
            self._frustrated_turn_count += 1

    def add_assistant_turn(
        self,
        content: str,
        sources: Optional[list[str]] = None,
        retrieval_score: float = 0.0,
        escalated: bool = False,
        escalation_reason: Optional[str] = None,
    ) -> None:
        """Record an assistant response."""
        if retrieval_score < 0.40:
            self._low_confidence_streak += 1
        else:
            self._low_confidence_streak = 0

        turn = Turn(
            role="assistant",
            content=content,
            sources=sources or [],
            retrieval_score=retrieval_score,
            escalated=escalated,
            escalation_reason=escalation_reason,
        )
        self.turns.append(turn)

        if escalated:
            self.escalated = True
            self.escalation_turn = len(self.turns)

    # ──────────────────────────────────────────────────────────────
    # Accessors
    # ──────────────────────────────────────────────────────────────

    @property
    def total_user_turns(self) -> int:
        return self._total_user_turns

    @property
    def low_confidence_streak(self) -> int:
        return self._low_confidence_streak

    @property
    def frustrated_turn_count(self) -> int:
        return self._frustrated_turn_count

    @property
    def dominant_persona(self) -> Optional[str]:
        """Return the most frequently detected persona across the session."""
        persona_counts: dict[str, int] = {}
        for turn in self.turns:
            if turn.role == "user" and turn.persona:
                persona_counts[turn.persona] = persona_counts.get(turn.persona, 0) + 1
        if not persona_counts:
            return None
        return max(persona_counts, key=persona_counts.get)

    @property
    def all_sources_used(self) -> list[str]:
        """Unique list of all source documents retrieved across the session."""
        sources = set()
        for turn in self.turns:
            if turn.role == "assistant":
                sources.update(turn.sources)
        return list(sources)

    @property
    def user_messages(self) -> list[str]:
        """All user messages in order."""
        return [t.content for t in self.turns if t.role == "user"]

    @property
    def attempted_steps(self) -> list[str]:
        """
        Extract suggested actions from assistant responses (simple heuristic).
        """
        steps = []
        for turn in self.turns:
            if turn.role == "assistant" and turn.content:
                # Look for numbered list items or bullet points as "attempted steps"
                import re
                lines = turn.content.split("\n")
                for line in lines:
                    line = line.strip()
                    if re.match(r"^(\d+\.|[-*•])\s+", line):
                        clean = re.sub(r"^(\d+\.|[-*•])\s+", "", line)
                        if 10 < len(clean) < 120:
                            steps.append(clean)
        return steps[:8]  # Return at most 8 steps

    # ──────────────────────────────────────────────────────────────
    # Context for LLM
    # ──────────────────────────────────────────────────────────────

    def get_windowed_history(self) -> list[dict]:
        """
        Return the last N turns as a list of {'role': ..., 'content': ...} dicts.
        Used as context for the LLM.
        """
        recent = self.turns[-self.window_size:]
        return [{"role": t.role, "content": t.content} for t in recent]

    def get_formatted_history(self) -> str:
        """
        Return conversation history as a formatted string for prompts.
        """
        lines = []
        for turn in self.turns[-self.window_size:]:
            role = "Customer" if turn.role == "user" else "Support Agent"
            lines.append(f"**{role}:** {turn.content}")
        return "\n\n".join(lines)

    def get_issue_summary(self) -> str:
        """
        Generate a brief issue summary from conversation history.
        Uses the first user message + any follow-ups.
        """
        user_msgs = self.user_messages
        if not user_msgs:
            return "No issue described."
        if len(user_msgs) == 1:
            return user_msgs[0][:500]
        return f"{user_msgs[0][:300]}... (followed by {len(user_msgs)-1} additional message(s))"

    def clear(self) -> None:
        """Reset conversation history."""
        self.turns.clear()
        self.escalated = False
        self.escalation_turn = None
        self._low_confidence_streak = 0
        self._frustrated_turn_count = 0
        self._total_user_turns = 0
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
