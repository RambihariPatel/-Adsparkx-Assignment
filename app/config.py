"""
Configuration module for NexaCloud Persona-Adaptive Customer Support Agent.
All settings can be overridden via environment variables.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "google"  # google, openai, anthropic
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.3
    max_output_tokens: int = 1500
    google_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))


@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""
    provider: str = "sentence_transformers"  # google, openai, sentence_transformers
    model_name: str = "all-MiniLM-L6-v2"
    # Use sentence-transformers locally (no API key needed, fast & reliable)


@dataclass
class VectorDBConfig:
    """Vector database configuration."""
    provider: str = "chroma"
    persist_directory: str = "./chroma_db"
    collection_name: str = "nexacloud_support"


@dataclass
class RAGConfig:
    """Retrieval-Augmented Generation pipeline configuration."""
    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 4
    # Minimum similarity score (0-1). Below this → low confidence
    min_similarity_score: float = 0.40
    data_directory: str = "./data"
    supported_extensions: tuple = (".md", ".txt", ".pdf", ".docx")


@dataclass
class PersonaConfig:
    """Persona detection configuration."""
    personas: tuple = ("Technical Expert", "Frustrated User", "Business Executive")
    # LLM confidence below which rule-based classification is preferred
    llm_confidence_threshold: float = 0.65
    default_persona: str = "Frustrated User"


@dataclass
class EscalationConfig:
    """Escalation logic configuration."""
    # Retrieval similarity score below which escalation is triggered
    low_confidence_threshold: float = 0.40
    # Number of consecutive turns with no useful retrieval → escalate
    max_low_confidence_turns: int = 2
    # Max conversation turns before suggesting escalation
    max_conversation_turns: int = 6
    # Turns with negative sentiment before escalation
    max_frustrated_turns: int = 3

    # Keywords that trigger immediate escalation
    escalation_keywords: tuple = (
        "lawsuit", "legal action", "lawyer", "attorney",
        "fraud", "scam", "stolen", "hacked", "compromised",
        "data breach", "speak to manager", "talk to human",
        "speak to agent", "escalate", "supervisor",
        "cancel my account", "delete my data", "gdpr request",
        "account suspended", "charge dispute", "chargeback",
    )

    # Keywords indicating billing/legal sensitivity
    sensitive_topic_keywords: tuple = (
        "billing", "invoice", "refund", "charge", "payment failed",
        "account locked", "suspended", "legal", "compliance",
        "data privacy", "gdpr", "ccpa",
    )


@dataclass
class AppConfig:
    """Main application configuration."""
    app_name: str = "NexaCloud Support Agent"
    app_version: str = "1.0.0"
    product_name: str = "NexaCloud"

    llm: LLMConfig = field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vector_db: VectorDBConfig = field(default_factory=VectorDBConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    persona: PersonaConfig = field(default_factory=PersonaConfig)
    escalation: EscalationConfig = field(default_factory=EscalationConfig)

    # Conversation memory window (number of past turns to include in context)
    memory_window: int = 8

    # Debug mode
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"


# Singleton config instance
config = AppConfig()


# Validate required API keys
def validate_config() -> tuple[bool, list[str]]:
    """
    Validate that required configuration is present.
    Returns (is_valid, list_of_issues).
    """
    issues = []

    if config.llm.provider == "google" and not config.llm.google_api_key:
        issues.append(
            "GOOGLE_API_KEY environment variable is not set. "
            "Get your free API key at: https://aistudio.google.com/app/apikey"
        )
    elif config.llm.provider == "openai" and not config.llm.openai_api_key:
        issues.append(
            "OPENAI_API_KEY environment variable is not set."
        )

    return len(issues) == 0, issues
