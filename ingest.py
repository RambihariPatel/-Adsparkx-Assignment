"""
Document Ingestion Script for NexaCloud Support Agent.

Run this script ONCE to load all documents from /data into ChromaDB.
Usage:
    python ingest.py
    python ingest.py --data-dir ./data
    python ingest.py --force  (re-ingest even if store exists)
"""

import os
import sys
import time
import argparse
import logging
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ingest")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ingest NexaCloud support documents into ChromaDB vector store."
    )
    parser.add_argument(
        "--data-dir",
        default="./data",
        help="Path to the data directory containing support documents (default: ./data)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingestion even if vector store already exists",
    )
    return parser.parse_args()


def print_header():
    print("\n" + "=" * 60)
    print("  NexaCloud Support Agent -- Document Ingestion")
    print("=" * 60 + "\n")


def print_progress(step: str, status: str = "...", color: str = ""):
    icons = {"...": "[.]", "[OK]": "[OK]", "[ERR]": "[ERR]", "[i]": "[i]"}
    icon = icons.get(status, "[.]")
    print(f"  [{status}] {step}")


def main():
    print_header()
    args = parse_args()

    # Import after path is set
    from app.config import config, validate_config

    # Validate config
    print_progress("Validating configuration")
    is_valid, issues = validate_config()
    if not is_valid:
        for issue in issues:
            print(f"\n  [ERR] {issue}\n")
        print("  Create a .env file with:\n  GOOGLE_API_KEY=your_key_here\n")
        sys.exit(1)
    print_progress("Configuration valid", "[OK]")

    # Check data directory
    data_dir = args.data_dir
    print_progress(f"Checking data directory: {data_dir}")
    if not os.path.exists(data_dir):
        print(f"\n  [ERR] Data directory not found: {data_dir}")
        print("  Create the /data directory and add support documents.\n")
        sys.exit(1)

    # Count documents
    supported_ext = (".pdf", ".md", ".txt", ".markdown")
    doc_files = [
        f for f in os.listdir(data_dir)
        if os.path.splitext(f)[1].lower() in supported_ext
    ]
    print_progress(f"Found {len(doc_files)} document(s) in {data_dir}", "[OK]")

    if not doc_files:
        print(f"\n  [ERR] No supported documents found (.pdf, .md, .txt)\n")
        sys.exit(1)

    print("\n  Documents to ingest:")
    for f in sorted(doc_files):
        size_kb = os.path.getsize(os.path.join(data_dir, f)) / 1024
        print(f"    * {f} ({size_kb:.1f} KB)")
    print()

    # Check if already ingested
    persist_dir = config.vector_db.persist_directory
    if os.path.exists(persist_dir) and not args.force:
        print_progress(f"Vector store found at {persist_dir}")
        print(
            "\n  [i] Vector store already exists. "
            "Use --force to re-ingest.\n"
            "  Loading existing store instead...\n"
        )
        from app.rag_pipeline import get_pipeline
        pipeline = get_pipeline()
        if pipeline.is_ready():
            count = pipeline._vectorstore._collection.count()
            print(f"  Existing store has {count} chunks -- ready!")
            print(
                "\n  [OK] Knowledge base is ready!\n"
                "  Run: streamlit run ui/streamlit_app.py\n"
                "  Or:  python cli/chat_cli.py\n"
            )
            return
        else:
            print("  Existing store appears empty. Proceeding with ingestion...\n")

    # Force re-ingest: delete existing store
    if args.force and os.path.exists(persist_dir):
        print_progress(f"Removing existing vector store at {persist_dir}")
        shutil.rmtree(persist_dir)
        print_progress("Old vector store removed", "[OK]")

    # Run ingestion
    print_progress("Starting document ingestion")
    print("  (This may take 30-120 seconds depending on document count and internet speed)\n")

    start_time = time.time()

    try:
        from app.rag_pipeline import RAGPipeline

        # Create fresh pipeline (bypass singleton to avoid loading old store)
        pipeline = RAGPipeline()

        print_progress("Loading and parsing documents")
        stats = pipeline.ingest(data_dir=data_dir)
        elapsed = time.time() - start_time

        print("\n" + "=" * 60)
        print("  [OK] INGESTION COMPLETE!")
        print("=" * 60)
        print(f"\n  Statistics:")
        print(f"    * Documents loaded:   {stats['documents_loaded']}")
        print(f"    * Chunks created:     {stats['chunks_created']}")
        print(f"    * Vector store path:  {stats['persist_directory']}")
        print(f"    * Time elapsed:       {elapsed:.1f}s")
        print()
        print("  Ready to launch!")
        print()
        print("  Start the web UI:")
        print("    streamlit run ui/streamlit_app.py")
        print()
        print("  Start the CLI:")
        print("    python cli/chat_cli.py")
        print()

    except ImportError as e:
        print(f"\n  [ERR] Import error: {e}")
        print("  Run: pip install -r requirements.txt\n")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\n  [ERR] File not found: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n  [ERR] Ingestion failed: {e}\n")
        logger.exception("Ingestion error")
        sys.exit(1)


if __name__ == "__main__":
    main()
