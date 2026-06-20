"""
Escalation Handler Module.

Determines when to escalate a conversation to a human support agent
and generates a structured handoff summary.

Escalation Triggers:
1. Retrieval confidence below threshold (low similarity scores)
2. No relevant documents found
3. Sensitive topic keywords detected (billing, legal, security breach)
4. Explicit user request to speak with a human
5. Too many frustrated turns without resolution
6. Conversation turn limit exceeded
7. Consecutive low-confidence retrievals
"""

import json
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.config import config
from app.rag_pipeline import RAGResponse
from app.conversation_memory import ConversationMemory

logger = logging.getLogger(__name__)


@dataclass
class EscalationDecision:
    """Result of the escalation check."""
    should_escalate: bool
    reason: str              # Human-readable reason
    trigger_code: str        # Machine-readable trigger code
    priority: str            # P1 / P2 / P3
    handoff_summary: Optional[dict] = None  # Populated when escalating


# ──────────────────────────────────────────────────────────────
# Priority mapping
# ──────────────────────────────────────────────────────────────

PRIORITY_MAP = {
    "EXPLICIT_REQUEST": "P1",
    "SENSITIVE_TOPIC": "P1",
    "NO_CONTEXT": "P2",
    "LOW_CONFIDENCE_STREAK": "P2",
    "FRUSTRATED_ESCALATION": "P2",
    "TURN_LIMIT": "P3",
    "GROUNDING_FAILURE": "P2",
}


def _contains_keywords(text: str, keywords: tuple) -> Optional[str]:
    """Check if text contains any of the given keyword patterns. Returns matched keyword or None."""
    text_lower = text.lower()
    for kw in keywords:
        # Support simple substring match
        if kw.lower() in text_lower:
            return kw
    return None


class EscalationHandler:
    """
    Evaluates whether a conversation should be escalated to a human agent
    and generates structured handoff summaries.
    """

    def __init__(self):
        self.esc_config = config.escalation

    def evaluate(
        self,
        user_message: str,
        rag_response: RAGResponse,
        memory: ConversationMemory,
        agent_response_grounded: bool = True,
    ) -> EscalationDecision:
        """
        Evaluate whether the current turn should trigger escalation.

        Args:
            user_message: Current user message
            rag_response: RAG retrieval result for this turn
            memory: Current conversation memory
            agent_response_grounded: Whether the response was grounded in KB

        Returns:
            EscalationDecision with trigger details
        """
        # ── Check 1: Explicit user request ─────────────────────────
        matched_kw = _contains_keywords(
            user_message, self.esc_config.escalation_keywords
        )
        if matched_kw:
            logger.info(f"Escalation: Explicit request detected ('{matched_kw}')")
            return EscalationDecision(
                should_escalate=True,
                reason=f"You have requested to speak with a human support agent. "
                       f"We're connecting you now.",
                trigger_code="EXPLICIT_REQUEST",
                priority="P1",
            )

        # ── Check 2: Sensitive topic detected ──────────────────────
        matched_sensitive = _contains_keywords(
            user_message, self.esc_config.sensitive_topic_keywords
        )
        if matched_sensitive:
            # Only escalate sensitive topics if retrieval is low confidence
            if not rag_response.is_confident:
                logger.info(f"Escalation: Sensitive topic + low confidence ('{matched_sensitive}')")
                return EscalationDecision(
                    should_escalate=True,
                    reason=(
                        f"Your query involves a sensitive topic ('{matched_sensitive}') "
                        f"that requires verified information from our specialist team. "
                        f"Connecting you to a human agent."
                    ),
                    trigger_code="SENSITIVE_TOPIC",
                    priority="P1",
                )

        # ── Check 3: No relevant documents found ───────────────────
        if not rag_response.results and memory.total_user_turns >= 1:
            logger.info("Escalation: No relevant context found in KB")
            return EscalationDecision(
                should_escalate=True,
                reason=(
                    "I wasn't able to find relevant information in our knowledge base "
                    "to address your specific query. A human specialist will be better "
                    "equipped to help you."
                ),
                trigger_code="NO_CONTEXT",
                priority="P2",
            )

        # ── Check 4: Consecutive low-confidence retrievals ─────────
        if memory.low_confidence_streak >= self.esc_config.max_low_confidence_turns:
            logger.info(f"Escalation: {memory.low_confidence_streak} consecutive low-confidence turns")
            return EscalationDecision(
                should_escalate=True,
                reason=(
                    f"I've been unable to find sufficiently accurate information for your queries "
                    f"over the last {memory.low_confidence_streak} exchanges. "
                    f"I'm escalating to ensure you get the right help."
                ),
                trigger_code="LOW_CONFIDENCE_STREAK",
                priority="P2",
            )

        # ── Check 5: Too many frustrated turns ─────────────────────
        if memory.frustrated_turn_count >= self.esc_config.max_frustrated_turns:
            logger.info(f"Escalation: {memory.frustrated_turn_count} frustrated turns detected")
            return EscalationDecision(
                should_escalate=True,
                reason=(
                    "I can see you're still experiencing difficulties despite our attempts to help. "
                    "I don't want to keep you waiting — let me connect you with one of our "
                    "specialist agents who can give you more personalized attention."
                ),
                trigger_code="FRUSTRATED_ESCALATION",
                priority="P2",
            )

        # ── Check 6: Conversation turn limit ──────────────────────
        if memory.total_user_turns >= self.esc_config.max_conversation_turns:
            logger.info(f"Escalation: Turn limit reached ({memory.total_user_turns} turns)")
            return EscalationDecision(
                should_escalate=True,
                reason=(
                    "We've been working on this for a while now. To make sure we get this "
                    "fully resolved for you, I'm connecting you with a senior support specialist "
                    "who can take a fresh look and bring this to closure."
                ),
                trigger_code="TURN_LIMIT",
                priority="P3",
            )

        # ── Check 7: Response not grounded ─────────────────────────
        if not agent_response_grounded and memory.total_user_turns >= 2:
            logger.info("Escalation: Response not grounded in KB")
            return EscalationDecision(
                should_escalate=True,
                reason=(
                    "I don't have enough verified information to confidently address your query. "
                    "Escalating to a specialist who can provide accurate guidance."
                ),
                trigger_code="GROUNDING_FAILURE",
                priority="P2",
            )

        # No escalation needed
        return EscalationDecision(
            should_escalate=False,
            reason="",
            trigger_code="NONE",
            priority="N/A",
        )

    def generate_handoff_summary(
        self,
        escalation_decision: EscalationDecision,
        memory: ConversationMemory,
        current_user_message: str,
    ) -> dict:
        """
        Generate a structured handoff summary for the human agent.

        Returns a dict with all relevant context for the receiving agent.
        """
        timestamp = datetime.now().isoformat()

        # Build conversation log
        conversation_log = []
        for turn in memory.turns:
            conversation_log.append({
                "role": turn.role,
                "content": turn.content[:500],  # Truncate long messages
                "timestamp": turn.timestamp.isoformat(),
                "persona": turn.persona if turn.role == "user" else None,
                "sources_used": turn.sources if turn.role == "assistant" else None,
            })

        summary = {
            "escalation_timestamp": timestamp,
            "session_id": memory.session_id,
            "priority": escalation_decision.priority,
            "escalation_trigger": escalation_decision.trigger_code,
            "escalation_reason": escalation_decision.reason,

            # Persona information
            "persona": {
                "detected": memory.dominant_persona or "Unknown",
                "all_turns": [
                    {
                        "turn": i + 1,
                        "persona": t.persona,
                        "confidence": round(t.persona_confidence, 2)
                    }
                    for i, t in enumerate(memory.turns)
                    if t.role == "user" and t.persona
                ],
            },

            # Issue details
            "issue": {
                "summary": memory.get_issue_summary(),
                "current_message": current_user_message,
                "total_exchanges": memory.total_user_turns,
            },

            # Knowledge base usage
            "knowledge_base": {
                "documents_referenced": memory.all_sources_used,
                "total_sources_consulted": len(memory.all_sources_used),
            },

            # What was tried
            "attempted_steps": memory.attempted_steps,

            # Conversation history
            "conversation_history": conversation_log,

            # Recommendations for human agent
            "recommendation": self._generate_recommendation(escalation_decision, memory),

            # Contact routing suggestion
            "route_to": self._suggest_routing(escalation_decision, memory),
        }

        return summary

    @staticmethod
    def _generate_recommendation(
        decision: EscalationDecision,
        memory: ConversationMemory,
    ) -> str:
        """Generate a recommendation for the human agent."""
        recommendations = {
            "EXPLICIT_REQUEST": (
                "Customer explicitly requested human assistance. Review conversation history "
                "to understand what was already attempted before continuing support."
            ),
            "SENSITIVE_TOPIC": (
                "This involves a sensitive topic (billing/legal/security). Verify account details "
                "and proceed with caution. May require supervisor approval for resolution."
            ),
            "NO_CONTEXT": (
                "AI agent could not find relevant KB documentation. This may be a novel issue "
                "or require product/engineering team investigation. Check internal systems for "
                "known issues matching this description."
            ),
            "LOW_CONFIDENCE_STREAK": (
                "AI agent had consistently low retrieval confidence. The customer's issue may be "
                "edge-case or undocumented. Consider if KB documentation needs to be updated "
                "after resolving this issue."
            ),
            "FRUSTRATED_ESCALATION": (
                "Customer has been increasingly frustrated. Prioritize empathy and quick resolution. "
                "Consider goodwill gesture (e.g., service credit) if multiple interactions failed."
            ),
            "TURN_LIMIT": (
                "Extended conversation without full resolution. Review all attempted steps in "
                "conversation log to avoid repeating ineffective solutions."
            ),
            "GROUNDING_FAILURE": (
                "AI agent could not ground response in KB. Verify if this is a known issue "
                "and if KB documentation needs updating."
            ),
        }
        return recommendations.get(decision.trigger_code, "Review conversation and resolve the customer's issue.")

    @staticmethod
    def _suggest_routing(
        decision: EscalationDecision,
        memory: ConversationMemory,
    ) -> str:
        """Suggest which team should handle this escalation."""
        if decision.trigger_code in ("SENSITIVE_TOPIC",):
            return "Billing & Accounts Specialist"
        if decision.trigger_code in ("NO_CONTEXT", "LOW_CONFIDENCE_STREAK", "GROUNDING_FAILURE"):
            return "Level 2 Technical Support"
        if decision.trigger_code == "FRUSTRATED_ESCALATION":
            return "Senior Customer Success Manager"
        if memory.dominant_persona == "Technical Expert":
            return "Level 2 Technical Support"
        if memory.dominant_persona == "Business Executive":
            return "Customer Success Manager"
        return "General Support — Level 2"

    def format_handoff_for_display(self, summary: dict) -> str:
        """Format the handoff summary as readable markdown."""
        persona_info = summary.get("persona", {})
        issue_info = summary.get("issue", {})
        kb_info = summary.get("knowledge_base", {})

        docs = kb_info.get("documents_referenced", [])
        docs_str = "\n".join(f"  • {d}" for d in docs) if docs else "  • None"

        steps = summary.get("attempted_steps", [])
        steps_str = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(steps)) if steps else "  • None recorded"

        return f"""
## 🚨 Human Escalation — Handoff Summary

| Field | Value |
|---|---|
| **Session ID** | `{summary.get('session_id', 'N/A')}` |
| **Priority** | **{summary.get('priority', 'P2')}** |
| **Escalation Trigger** | `{summary.get('escalation_trigger', 'N/A')}` |
| **Detected Persona** | {persona_info.get('detected', 'Unknown')} |
| **Total Exchanges** | {issue_info.get('total_exchanges', 0)} turns |
| **Route To** | {summary.get('route_to', 'General Support')} |

### 📋 Issue Summary
{issue_info.get('summary', 'No summary available.')}

### 📚 Documents Referenced
{docs_str}

### 🔧 Steps Already Attempted
{steps_str}

### 💡 Recommendation for Agent
{summary.get('recommendation', 'Review conversation and assist the customer.')}

### ⏰ Escalation Time
{summary.get('escalation_timestamp', 'N/A')}
"""


# Module-level singleton
_handler: Optional[EscalationHandler] = None


def get_handler() -> EscalationHandler:
    """Get or create the singleton EscalationHandler."""
    global _handler
    if _handler is None:
        _handler = EscalationHandler()
    return _handler
