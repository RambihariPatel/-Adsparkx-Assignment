"""
Adaptive Response Generator Module.

Generates persona-specific responses using retrieved knowledge base content.
Each persona gets a unique system prompt defining tone, structure, and style.

Persona Response Styles:
- Technical Expert: Detailed, root-cause analysis, code/config examples, step-by-step
- Frustrated User: Empathetic opener, simple language, reassuring, action-oriented
- Business Executive: Concise bullet points, impact-first, resolution ETA, no jargon

Strict grounding: responses are generated ONLY from retrieved context.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import google.generativeai as genai

from app.config import config
from app.rag_pipeline import RAGResponse

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Complete agent response with metadata."""
    content: str
    persona: str
    sources: list[str]
    top_retrieval_score: float
    is_grounded: bool       # True if response is based on retrieved content
    model_used: str


# ──────────────────────────────────────────────────────────────
# Persona System Prompts
# ──────────────────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "Technical Expert": """You are a senior technical support engineer at NexaCloud. 
You are speaking with a TECHNICAL EXPERT who has deep technical knowledge.

**Communication Style:**
- Use technical terminology freely — they understand it
- Provide detailed, precise explanations
- Include root cause analysis when relevant
- Offer step-by-step troubleshooting with specific commands, code snippets, or configurations
- Reference specific error codes, API endpoints, configuration parameters
- Be direct and information-dense — they don't need hand-holding
- Structure complex answers with headers, numbered steps, or code blocks

**Response Rules:**
1. ONLY use information from the provided knowledge base context
2. If the context doesn't cover the question, say so explicitly and suggest what type of resource might help
3. Do NOT fabricate error codes, API endpoints, or technical specifications
4. Be precise — if you cite a setting or parameter, quote it exactly as it appears in the docs
5. Keep responses comprehensive but focused — technical users value precision over brevity""",

    "Frustrated User": """You are an empathetic customer support specialist at NexaCloud.
You are speaking with a FRUSTRATED USER who is stressed and needs reassurance.

**Communication Style:**
- Open with genuine empathy — acknowledge their frustration first
- Use simple, clear language — avoid jargon and technical terms
- Be warm, patient, and reassuring
- Break solutions into simple, numbered steps
- End with positive reassurance and next steps if current approach fails
- Avoid: long paragraphs, technical jargon, passive voice, dismissive language

**Response Rules:**
1. ONLY use information from the provided knowledge base context
2. Start with an empathetic acknowledgment (e.g., "I completely understand how frustrating this must be...")
3. Keep steps simple — one action per step
4. If the context doesn't fully address the issue, acknowledge it honestly and offer escalation
5. End with clear next steps or assurance that you're there to help
6. Do NOT make promises about resolution timelines unless the docs explicitly state them""",

    "Business Executive": """You are a senior customer success manager at NexaCloud.
You are speaking with a BUSINESS EXECUTIVE who values efficiency and business outcomes.

**Communication Style:**
- Lead with business impact and the bottom line
- Be concise — executives value brevity over depth
- Use bullet points and clear structure
- Avoid technical jargon — translate tech concepts to business language
- Address business impact, operational implications, and resolution timelines
- Provide the "what" and "when" — they don't need deep technical "how"
- Be authoritative and confident

**Response Rules:**
1. ONLY use information from the provided knowledge base context
2. Start with the most important information first (inverted pyramid)
3. Keep the response under 200 words unless the question requires more
4. Include estimated resolution timeframes ONLY if explicitly stated in the docs
5. If SLA or business impact info is available, highlight it prominently
6. Do NOT fabricate business metrics, SLA guarantees, or resolution timelines not in the docs""",
}

NO_CONTEXT_PROMPTS = {
    "Technical Expert": (
        "I've searched our knowledge base for information on your query, but I don't have "
        "specific documentation that directly addresses this technical issue. "
        "This may require investigation by our engineering team. "
        "I recommend escalating this to our Level 2 technical support team who can review "
        "system logs and investigate the root cause directly."
    ),
    "Frustrated User": (
        "I completely understand how frustrating this situation is, and I truly want to help you. "
        "Unfortunately, I don't have enough information in my current knowledge base to give you "
        "a confident answer to this specific problem. Rather than risk giving you incorrect guidance, "
        "I think the best next step is to connect you with one of our specialist support agents "
        "who can look into this personally and get you a resolution quickly."
    ),
    "Business Executive": (
        "I want to provide you with accurate information, and this specific situation falls "
        "outside what I can confidently address from our standard documentation. "
        "To ensure you receive accurate, authoritative guidance on this matter, "
        "I recommend connecting you with our senior support team who can provide "
        "a definitive answer and resolution timeline."
    ),
}


def _build_response_prompt(
    persona: str,
    user_message: str,
    rag_response: RAGResponse,
    conversation_history: list[dict],
) -> str:
    """Build the complete LLM prompt for response generation."""
    system_prompt = SYSTEM_PROMPTS.get(persona, SYSTEM_PROMPTS["Frustrated User"])

    # Format conversation history
    history_text = ""
    if conversation_history:
        recent = conversation_history[-6:]
        history_lines = []
        for msg in recent:
            role = "Customer" if msg["role"] == "user" else "Support Agent"
            history_lines.append(f"{role}: {msg['content'][:300]}")
        history_text = "\n".join(history_lines)

    prompt = f"""{system_prompt}

---

**KNOWLEDGE BASE CONTEXT** (use ONLY this information to answer):

{rag_response.context_text}

---

**CONVERSATION HISTORY:**
{history_text if history_text else "This is the start of the conversation."}

---

**CURRENT CUSTOMER MESSAGE:**
{user_message}

---

**YOUR RESPONSE** (respond directly to the customer, as the NexaCloud support agent):"""

    return prompt


class ResponseGenerator:
    """
    Generates persona-adapted responses grounded in retrieved knowledge base content.
    """

    def __init__(self):
        self._model = None
        self._model_name = "Unavailable"
        self._init_llm()

    def _init_llm(self):
        """Initialize the LLM."""
        try:
            if config.llm.provider == "google" and config.llm.google_api_key:
                genai.configure(api_key=config.llm.google_api_key)
                self._model = genai.GenerativeModel(
                    model_name=config.llm.model_name,
                    generation_config=genai.types.GenerationConfig(
                        temperature=config.llm.temperature,
                        max_output_tokens=config.llm.max_output_tokens,
                    )
                )
                self._model_name = config.llm.model_name
                logger.info(f"ResponseGenerator: LLM initialized ({self._model_name})")
            else:
                logger.error("ResponseGenerator: No LLM provider configured")
        except Exception as e:
            logger.error(f"ResponseGenerator: LLM init failed: {e}")

    def generate(
        self,
        persona: str,
        user_message: str,
        rag_response: RAGResponse,
        conversation_history: Optional[list[dict]] = None,
    ) -> AgentResponse:
        """
        Generate a persona-adapted response grounded in retrieved context.

        Args:
            persona: Detected customer persona
            user_message: Current user message
            rag_response: Retrieved knowledge base context
            conversation_history: Past conversation turns

        Returns:
            AgentResponse with content, sources, and metadata
        """
        if conversation_history is None:
            conversation_history = []

        source_names = [r.source for r in rag_response.results]

        # If no relevant content found, use canned no-context response
        if not rag_response.is_confident or not rag_response.results:
            fallback = NO_CONTEXT_PROMPTS.get(persona, NO_CONTEXT_PROMPTS["Frustrated User"])
            return AgentResponse(
                content=fallback,
                persona=persona,
                sources=[],
                top_retrieval_score=rag_response.top_score,
                is_grounded=False,
                model_used=self._model_name,
            )

        # Generate with LLM
        if self._model is None:
            return AgentResponse(
                content=(
                    "I'm sorry, the AI response system is currently unavailable. "
                    "Please contact support@nexacloud.io directly."
                ),
                persona=persona,
                sources=source_names,
                top_retrieval_score=rag_response.top_score,
                is_grounded=False,
                model_used="unavailable",
            )

        try:
            prompt = _build_response_prompt(
                persona=persona,
                user_message=user_message,
                rag_response=rag_response,
                conversation_history=conversation_history,
            )

            response = self._model.generate_content(prompt)
            content = response.text.strip()

            return AgentResponse(
                content=content,
                persona=persona,
                sources=list(set(source_names)),  # Deduplicate
                top_retrieval_score=rag_response.top_score,
                is_grounded=True,
                model_used=self._model_name,
            )

        except Exception as e:
            logger.error(f"ResponseGenerator: Generation failed: {e}")
            return AgentResponse(
                content=(
                    "I encountered an issue generating a response. "
                    "Please try again or contact support@nexacloud.io if this persists."
                ),
                persona=persona,
                sources=source_names,
                top_retrieval_score=rag_response.top_score,
                is_grounded=False,
                model_used=self._model_name,
            )


# Module-level singleton
_generator: Optional[ResponseGenerator] = None


def get_generator() -> ResponseGenerator:
    """Get or create the singleton ResponseGenerator."""
    global _generator
    if _generator is None:
        _generator = ResponseGenerator()
    return _generator
