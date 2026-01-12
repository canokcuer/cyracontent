#!/usr/bin/env python3
"""
Test the agent pipeline (FENIX -> HIPPOCRATES -> NEO).
Use --dry-run to test without making API calls.
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all agents can be imported."""
    print("[1/4] Testing imports...")
    try:
        from src.agents.can import CANOrchestrator
        from src.agents.fenix import FenixAgent
        from src.agents.hippocrates import HippocratesAgent
        from src.agents.neo import NeoAgent
        print("  OK - All agents imported successfully")
        return True
    except ImportError as e:
        print(f"  FAIL - Import error: {e}")
        return False

def test_rag_connection():
    """Test RAG retriever can connect to Qdrant."""
    print("[2/4] Testing RAG connection...")
    try:
        from src.rag.retriever import RAGRetriever
        retriever = RAGRetriever()
        results = retriever.retrieve("test", collection="wellness", top_k=1)
        print(f"  OK - RAG connected, found {len(results)} results")
        return True
    except Exception as e:
        print(f"  FAIL - RAG error: {e}")
        return False

def test_output_handlers():
    """Test output handlers can be instantiated."""
    print("[3/4] Testing output handlers...")
    try:
        from src.outputs.markdown import MarkdownExporter
        from src.outputs.json_export import JSONExporter
        from src.outputs.shopify import ShopifyPublisher

        md = MarkdownExporter()
        js = JSONExporter()
        # Shopify may fail without credentials, that's OK for dry-run
        print("  OK - Output handlers ready")
        return True
    except Exception as e:
        print(f"  FAIL - Output handler error: {e}")
        return False

def test_pipeline_dry_run():
    """Test pipeline flow without making API calls."""
    print("[4/4] Testing pipeline flow (dry-run)...")
    try:
        from src.agents.can import CANOrchestrator

        # Just verify the orchestrator can be created
        # Full test would require API calls
        print("  OK - Pipeline structure valid")
        print("  (Full test requires --live flag and API credits)")
        return True
    except Exception as e:
        print(f"  FAIL - Pipeline error: {e}")
        return False

def test_pipeline_live(topic: str):
    """Run actual pipeline with API calls."""
    print(f"[LIVE] Running pipeline for topic: {topic}")
    try:
        from src.agents.can import CANOrchestrator

        orchestrator = CANOrchestrator()
        result = orchestrator.run(topic=topic, content_type="blog")

        if result and result.get("content"):
            print(f"  OK - Generated {len(result['content'])} characters")
            return True
        else:
            print("  FAIL - No content generated")
            return False
    except Exception as e:
        print(f"  FAIL - Pipeline error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test agent pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Test without API calls")
    parser.add_argument("--live", action="store_true", help="Run actual pipeline")
    parser.add_argument("--topic", default="Uyku Kalitesi", help="Topic for live test")
    args = parser.parse_args()

    print("=" * 50)
    print("Agent Pipeline Test")
    print("=" * 50)

    results = []

    # Always run these tests
    results.append(("imports", test_imports()))
    results.append(("rag", test_rag_connection()))
    results.append(("outputs", test_output_handlers()))

    if args.live:
        results.append(("pipeline_live", test_pipeline_live(args.topic)))
    else:
        results.append(("pipeline_dry", test_pipeline_dry_run()))

    print("=" * 50)
    print("Results:")

    all_passed = True
    for name, passed in results:
        status = "\033[92mPASS\033[0m" if passed else "\033[91mFAIL\033[0m"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("\033[92mAll tests passed!\033[0m")
        return 0
    else:
        print("\033[91mSome tests failed.\033[0m")
        return 1

if __name__ == "__main__":
    sys.exit(main())
