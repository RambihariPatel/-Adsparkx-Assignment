"""
NexaCloud Support Agent — Rich CLI Interface

A polished command-line chatbot using the Rich library for colored, 
formatted output with persona badges, source citations, and escalation panels.
"""

import os
import sys
import json
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.columns import Columns
from rich.rule import Rule
from rich.live import Live
from rich.spinner import Spinner
from rich import box

from app.config import config, validate_config
from app.persona_detector import get_detector
from app.rag_pipeline import get_pipeline
from app.response_generator import get_generator
from app.escalation_handler import get_handler
from app.conversation_memory import ConversationMemory

logging.basicConfig(level=logging.ERROR)
console = Console()

# Color scheme
PERSONA_COLORS = {
    "Technical Expert": "cyan",
    "Frustrated User": "red",
    "Business Executive": "yellow",
}

PERSONA_ICONS = {
    "Technical Expert": "⚙️",
    "Frustrated User": "😤",
    "Business Executive": "💼",
}


def print_banner():
    """Print the application banner."""
    banner = Text()
    banner.append("\n  ███╗   ██╗███████╗██╗  ██╗ █████╗  ██████╗██╗      ██████╗ ██╗   ██╗██████╗ \n", style="bold bright_blue")
    banner.append("  ████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗\n", style="bold blue")
    banner.append("  ██╔██╗ ██║█████╗   ╚███╔╝ ███████║██║     ██║     ██║   ██║██║   ██║██║  ██║\n", style="bold bright_magenta")
    banner.append("  ██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║██║     ██║     ██║   ██║██║   ██║██║  ██║\n", style="bold magenta")
    banner.append("  ██║ ╚████║███████╗██╔╝ ██╗██║  ██║╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝\n", style="bold bright_magenta")
    banner.append("  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ \n", style="bold magenta")
    console.print(banner)

    subtitle = Panel(
        "[bold white]Persona-Adaptive Customer Support Agent[/bold white]\n"
        "[dim]Powered by Google Gemini · RAG · ChromaDB[/dim]",
        style="bright_blue",
        border_style="bright_blue",
        box=box.ROUNDED,
    )
    console.print(subtitle)
    console.print()


def print_persona_badge(persona: str, confidence: float, method: str) -> None:
    """Print a colored persona badge."""
    color = PERSONA_COLORS.get(persona, "white")
    icon = PERSONA_ICONS.get(persona, "👤")
    conf_pct = int(confidence * 100)

    badge_text = Text()
    badge_text.append(f" {icon} {persona} ", style=f"bold {color}")
    badge_text.append(f" {conf_pct}% confidence ", style=f"dim {color}")
    badge_text.append(f" via {method} ", style="dim white")

    console.print(
        Panel(badge_text, title="[bold]Detected Persona[/bold]",
              border_style=color, box=box.ROUNDED, padding=(0, 1))
    )


def print_sources(sources: list[str], score: float) -> None:
    """Print source documents used."""
    if not sources:
        return

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Icon", style="dim", width=3)
    table.add_column("Source", style="cyan")
    table.add_column("Score", style="dim")

    for source in set(sources):
        table.add_row("📄", source, "")

    table.add_row("", f"[dim]Retrieval score: {score:.0%}[/dim]", "")

    console.print(
        Panel(table, title="[bold]📚 Sources Retrieved[/bold]",
              border_style="blue", box=box.ROUNDED, padding=(0, 1))
    )


def print_agent_response(content: str, persona: str) -> None:
    """Print the agent response with appropriate formatting."""
    color = PERSONA_COLORS.get(persona, "white")

    # Try to render as markdown
    try:
        md = Markdown(content)
        console.print(
            Panel(
                md,
                title=f"[bold {color}]🤖 NexaCloud Support Agent[/bold {color}]",
                border_style=color,
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
    except Exception:
        console.print(
            Panel(
                content,
                title=f"[bold {color}]🤖 NexaCloud Support Agent[/bold {color}]",
                border_style=color,
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )


def print_escalation(reason: str, handoff_summary: dict) -> None:
    """Print escalation notification and handoff summary."""
    console.print()
    console.print(Rule(style="red"))

    console.print(
        Panel(
            f"[bold red]🚨 ESCALATING TO HUMAN AGENT[/bold red]\n\n"
            f"[white]{reason}[/white]",
            border_style="red",
            box=box.DOUBLE_EDGE,
            padding=(1, 2),
        )
    )

    # Handoff summary table
    console.print()
    console.print("[bold red]📋 HANDOFF SUMMARY[/bold red]")
    console.print(Rule(style="red"))

    # Key info table
    table = Table(box=box.ROUNDED, show_header=False, border_style="red")
    table.add_column("Field", style="bold yellow", width=22)
    table.add_column("Value", style="white")

    persona_info = handoff_summary.get("persona", {})
    issue_info = handoff_summary.get("issue", {})
    kb_info = handoff_summary.get("knowledge_base", {})

    table.add_row("Session ID", handoff_summary.get("session_id", "N/A"))
    table.add_row("Priority", f"[bold]{handoff_summary.get('priority', 'P2')}[/bold]")
    table.add_row("Trigger", handoff_summary.get("escalation_trigger", "N/A"))
    table.add_row("Persona", persona_info.get("detected", "Unknown"))
    table.add_row("Total Exchanges", str(issue_info.get("total_exchanges", 0)))
    table.add_row("Route To", handoff_summary.get("route_to", "General Support"))

    console.print(table)
    console.print()

    # Issue summary
    console.print("[bold yellow]Issue Summary:[/bold yellow]")
    console.print(f"  {issue_info.get('summary', 'N/A')}")
    console.print()

    # Documents used
    docs = kb_info.get("documents_referenced", [])
    if docs:
        console.print("[bold yellow]Documents Referenced:[/bold yellow]")
        for doc in docs:
            console.print(f"  • {doc}")
        console.print()

    # Attempted steps
    steps = handoff_summary.get("attempted_steps", [])
    if steps:
        console.print("[bold yellow]Steps Already Attempted:[/bold yellow]")
        for i, step in enumerate(steps[:6], 1):
            console.print(f"  {i}. {step}")
        console.print()

    # Recommendation
    console.print("[bold yellow]Recommendation for Agent:[/bold yellow]")
    console.print(f"  {handoff_summary.get('recommendation', 'N/A')}")
    console.print()

    # Full JSON option
    console.print("[dim]Press Enter to see full JSON handoff summary, or type anything to skip...[/dim]")
    show_json = input().strip()
    if not show_json:
        console.print_json(json.dumps(handoff_summary, indent=2, default=str))

    console.print(Rule(style="red"))


def print_help():
    """Print available commands."""
    table = Table(title="Available Commands", box=box.ROUNDED, border_style="blue")
    table.add_column("Command", style="cyan", width=15)
    table.add_column("Description", style="white")

    commands = [
        ("/help", "Show this help message"),
        ("/examples", "Show example queries for each persona"),
        ("/status", "Show current session status"),
        ("/history", "Show conversation history"),
        ("/clear", "Clear conversation and start fresh"),
        ("/quit", "Exit the application"),
    ]
    for cmd, desc in commands:
        table.add_row(cmd, desc)

    console.print(table)


def print_examples():
    """Print example queries for each persona."""
    console.print()
    console.print(Rule("[bold cyan]Example Queries by Persona[/bold cyan]"))

    examples = {
        "Technical Expert ⚙️": [
            "I'm getting a 401 error on the API authentication endpoint — can you explain the OAuth token flow?",
            "What are the exact rate limit headers returned on a 429 response?",
            "How do I configure HMAC-SHA256 signature verification for webhooks?",
            "The PostgreSQL integration sync fails with INT_003 — what's the root cause?",
        ],
        "Frustrated User 😤": [
            "I've tried everything and NOTHING WORKS! My password reset isn't working!!!",
            "This is absolutely ridiculous, I can't log in for the 5th time today!",
            "I've been waiting for hours and the app is STILL broken. Please help ASAP!",
            "Why doesn't anything work?! I'm so frustrated with this product!",
        ],
        "Business Executive 💼": [
            "How does this API outage impact our operations and what's the resolution timeline?",
            "What are NexaCloud's SLA commitments and service credit eligibility?",
            "Give me a high-level summary of our data security compliance status.",
            "When will this issue be resolved and what is the business impact?",
        ],
    }

    for persona, queries in examples.items():
        console.print(f"\n[bold yellow]{persona}[/bold yellow]")
        for q in queries:
            console.print(f"  [dim]→[/dim] {q}")


def print_status(memory: ConversationMemory) -> None:
    """Print current session status."""
    console.print()

    table = Table(title="Session Status", box=box.ROUNDED, border_style="blue")
    table.add_column("Metric", style="bold yellow", width=25)
    table.add_column("Value", style="white")

    table.add_row("Session ID", memory.session_id)
    table.add_row("Total Turns", str(memory.total_user_turns))
    table.add_row("Dominant Persona", memory.dominant_persona or "Not determined")
    table.add_row("Escalated", "🚨 YES" if memory.escalated else "✅ NO")
    table.add_row("Sources Used", ", ".join(memory.all_sources_used) or "None yet")
    table.add_row("Low Confidence Streak", str(memory.low_confidence_streak))
    table.add_row("Frustrated Turns", str(memory.frustrated_turn_count))

    console.print(table)


def run_cli():
    """Main CLI loop."""
    print_banner()

    # Validate config
    is_valid, issues = validate_config()
    if not is_valid:
        for issue in issues:
            console.print(f"[bold red]❌ {issue}[/bold red]")
        console.print("[yellow]Create a .env file with GOOGLE_API_KEY=your_key and restart.[/yellow]")
        sys.exit(1)

    # Load components
    console.print("[dim]Loading AI components...[/dim]")
    with console.status("[bold blue]Initializing RAG pipeline and AI models...[/bold blue]"):
        try:
            pipeline = get_pipeline()
            detector = get_detector()
            generator = get_generator()
            handler = get_handler()
        except Exception as e:
            console.print(f"[bold red]Failed to load components: {e}[/bold red]")
            sys.exit(1)

    if not pipeline.is_ready():
        console.print(
            Panel(
                "[yellow]⚠️  Knowledge base not loaded![/yellow]\n\n"
                "Run [bold cyan]python ingest.py[/bold cyan] first to ingest documents.\n"
                "Or continue — the agent will escalate queries it cannot answer.",
                title="[bold yellow]Setup Required[/bold yellow]",
                border_style="yellow",
            )
        )
    else:
        console.print(
            Panel(
                "[green]✅ Knowledge base loaded and ready![/green]\n"
                "[dim]Type your question or /help for commands.[/dim]",
                title="[bold green]System Ready[/bold green]",
                border_style="green",
            )
        )

    memory = ConversationMemory(window_size=config.memory_window)
    escalated = False

    console.print()
    console.print("[bold cyan]Type your question below. Type [white]/help[/white] for commands.[/bold cyan]")
    console.print(Rule(style="dim"))

    while True:
        try:
            # Prompt
            console.print()
            if escalated:
                console.print(
                    "[dim red]This session has been escalated. "
                    "Type [white]/clear[/white] to start a new conversation.[/dim red]"
                )

            user_input = Prompt.ask("[bold bright_blue]You[/bold bright_blue]").strip()

            if not user_input:
                continue

            # ── Handle commands ──────────────────────────────
            if user_input.startswith("/"):
                cmd = user_input.lower().strip()
                if cmd in ("/quit", "/exit", "/q"):
                    console.print("[bold green]Thank you for using NexaCloud Support! Goodbye! 👋[/bold green]")
                    break
                elif cmd == "/help":
                    print_help()
                elif cmd == "/examples":
                    print_examples()
                elif cmd == "/status":
                    print_status(memory)
                elif cmd == "/history":
                    hist = memory.get_formatted_history()
                    if hist:
                        console.print(Panel(Markdown(hist), title="Conversation History", border_style="blue"))
                    else:
                        console.print("[dim]No conversation history yet.[/dim]")
                elif cmd == "/clear":
                    memory.clear()
                    escalated = False
                    console.print("[green]✅ Conversation cleared. Starting fresh![/green]")
                else:
                    console.print(f"[red]Unknown command: {cmd}. Type /help for commands.[/red]")
                continue

            if escalated:
                console.print("[dim red]Session escalated. Type /clear to start new conversation.[/dim red]")
                continue

            # ── Process message ──────────────────────────────
            console.print()

            # 1. Detect persona
            with console.status("[bold blue]🧠 Detecting persona...[/bold blue]"):
                persona_result = detector.detect(
                    message=user_input,
                    conversation_history=memory.get_windowed_history(),
                )

            print_persona_badge(
                persona_result.persona,
                persona_result.confidence,
                persona_result.detection_method,
            )

            is_negative = persona_result.persona == "Frustrated User"
            memory.add_user_turn(
                content=user_input,
                persona=persona_result.persona,
                persona_confidence=persona_result.confidence,
                sentiment_negative=is_negative,
            )

            # 2. Retrieve
            with console.status("[bold blue]📚 Searching knowledge base...[/bold blue]"):
                rag_response = pipeline.retrieve(user_input)

            if rag_response.results:
                print_sources(
                    [r.source for r in rag_response.results],
                    rag_response.top_score,
                )
            else:
                console.print("[dim yellow]⚠️  No directly relevant articles found in knowledge base[/dim yellow]")

            # 3. Check escalation
            escalation = handler.evaluate(
                user_message=user_input,
                rag_response=rag_response,
                memory=memory,
            )

            if escalation.should_escalate:
                # Generate response first then escalate
                agent_content = escalation.reason
                memory.add_assistant_turn(
                    content=agent_content,
                    sources=[],
                    retrieval_score=0.0,
                    escalated=True,
                    escalation_reason=escalation.trigger_code,
                )
                handoff = handler.generate_handoff_summary(
                    escalation_decision=escalation,
                    memory=memory,
                    current_user_message=user_input,
                )
                print_escalation(escalation.reason, handoff)
                escalated = True
                continue

            # 4. Generate response
            with console.status(
                f"[bold {PERSONA_COLORS.get(persona_result.persona, 'white')}]"
                f"✍️  Generating {persona_result.persona} response...[/bold "
                f"{PERSONA_COLORS.get(persona_result.persona, 'white')}]"
            ):
                agent_resp = generator.generate(
                    persona=persona_result.persona,
                    user_message=user_input,
                    rag_response=rag_response,
                    conversation_history=memory.get_windowed_history(),
                )

            print_agent_response(agent_resp.content, persona_result.persona)

            memory.add_assistant_turn(
                content=agent_resp.content,
                sources=agent_resp.sources,
                retrieval_score=agent_resp.top_retrieval_score,
            )

            # 5. Post-generation escalation check
            post_esc = handler.evaluate(
                user_message=user_input,
                rag_response=rag_response,
                memory=memory,
                agent_response_grounded=agent_resp.is_grounded,
            )

            if post_esc.should_escalate:
                handoff = handler.generate_handoff_summary(
                    escalation_decision=post_esc,
                    memory=memory,
                    current_user_message=user_input,
                )
                print_escalation(post_esc.reason, handoff)
                escalated = True

        except KeyboardInterrupt:
            console.print("\n[bold green]Session interrupted. Goodbye! 👋[/bold green]")
            break
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            if config.debug:
                import traceback
                console.print_exception()


if __name__ == "__main__":
    run_cli()
