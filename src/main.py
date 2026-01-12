"""
CyraSoul Multi-Agent Content Generation CLI.

Usage:
    python -m src.main generate "Uyku Kalitesini Artırmanın 10 Yolu"
    python -m src.main generate "DailyGlow" --type product
    python -m src.main index /path/to/knowledge
    python -m src.main status
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def cmd_generate(args):
    """Generate content using the multi-agent pipeline."""
    from src.agents import CANOrchestrator
    from src.outputs import MarkdownExporter, JSONExporter, ShopifyExporter

    print(f"\n{'='*60}")
    print("CyraSoul Multi-Agent Content Generation")
    print(f"{'='*60}\n")

    # Initialize orchestrator
    orchestrator = CANOrchestrator(
        state_dir=Path("state"),
        guardrails_path=Path("state/guardrails.md")
    )

    # Parse keywords
    keywords = args.keywords.split(",") if args.keywords else None

    # Generate content
    print(f"Topic: {args.topic}")
    print(f"Type: {args.type}")
    print(f"Keywords: {keywords or 'Auto-generated'}")
    print(f"\nStarting pipeline...\n")

    try:
        output = orchestrator.generate_content(
            topic=args.topic,
            content_type=args.type,
            keywords=keywords,
            product_focus=args.product
        )

        print(f"\n{'='*60}")
        print("Generation Complete!")
        print(f"{'='*60}")
        print(f"Title: {output.title}")
        print(f"Word Count: {output.word_count}")
        print(f"SEO Score: {output.seo_score}/100")
        print(f"Scientific Score: {output.scientific_score}/100")

        # Export based on format
        if args.format in ["markdown", "all"]:
            md_exporter = MarkdownExporter(Path("output/articles"))
            md_result = md_exporter.export(output)
            if md_result.success:
                print(f"\nMarkdown saved: {md_result.file_path}")

        if args.format in ["json", "all"]:
            json_exporter = JSONExporter(Path("output/json"))
            json_result = json_exporter.export(output, include_pipeline_state=True)
            if json_result.success:
                print(f"JSON saved: {json_result.file_path}")

            # Also export social media versions
            social_result = json_exporter.export_social_media(output)
            if social_result.success:
                print(f"Social media JSON saved: {social_result.file_path}")

        if args.format in ["shopify", "all"] and args.publish:
            try:
                shopify_exporter = ShopifyExporter()
                shop_result = shopify_exporter.publish_article(
                    output,
                    published=args.publish_live
                )
                if shop_result.success:
                    print(f"Published to Shopify: {shop_result.article_url}")
                else:
                    print(f"Shopify publish failed: {shop_result.error}")
            except ValueError as e:
                print(f"Shopify not configured: {e}")

        print(f"\n{'='*60}\n")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


def cmd_index(args):
    """Index knowledge base documents."""
    from src.rag import KnowledgeIndexer

    print(f"\n{'='*60}")
    print("CyraSoul Knowledge Base Indexer")
    print(f"{'='*60}\n")

    indexer = KnowledgeIndexer()

    # Setup collections
    print("Setting up vector database collections...")
    created = indexer.setup_collections()
    for name, was_created in created.items():
        status = "created" if was_created else "exists"
        print(f"  - {name}: {status}")

    # Index documents
    if args.path:
        base_path = Path(args.path)
    else:
        base_path = Path("knowledge_base")

    if not base_path.exists():
        print(f"\nError: Path not found: {base_path}")
        sys.exit(1)

    print(f"\nIndexing documents from: {base_path}")
    results = indexer.index_knowledge_base(base_path)

    print("\nIndexing Results:")
    for collection, result in results.items():
        print(f"  - {collection}:")
        print(f"      Documents: {result.documents_processed}")
        print(f"      Chunks: {result.chunks_indexed}")
        if result.errors:
            print(f"      Errors: {len(result.errors)}")

    # Show stats
    print("\nCollection Statistics:")
    stats = indexer.get_stats()
    for name, info in stats.items():
        if "error" in info:
            print(f"  - {name}: {info['error']}")
        else:
            print(f"  - {name}: {info.get('points_count', 0)} points")

    print(f"\n{'='*60}\n")


def cmd_status(args):
    """Show pipeline status."""
    from src.agents import CANOrchestrator

    orchestrator = CANOrchestrator(state_dir=Path("state"))
    status = orchestrator.get_status()

    print(f"\n{'='*60}")
    print("Pipeline Status")
    print(f"{'='*60}\n")

    for key, value in status.items():
        print(f"{key}: {value}")

    print(f"\n{'='*60}\n")


def cmd_agents(args):
    """Show information about agents."""
    print(f"\n{'='*60}")
    print("CyraSoul Multi-Agent System")
    print(f"{'='*60}\n")

    agents = [
        {
            "name": "CAN",
            "role": "Orchestrator",
            "description": "Master coordinator managing the entire content pipeline"
        },
        {
            "name": "FENIX",
            "role": "Content Writer",
            "description": "Turkish wellness content specialist"
        },
        {
            "name": "HIPPOCRATES",
            "role": "Scientific Reviewer",
            "description": "Health & wellness accuracy validator"
        },
        {
            "name": "NEO",
            "role": "SEO Optimizer",
            "description": "Search engine optimization specialist"
        }
    ]

    for agent in agents:
        print(f"{agent['name']} ({agent['role']})")
        print(f"  {agent['description']}")
        print()

    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="CyraSoul Multi-Agent Content Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate a blog post:
    python -m src.main generate "Uyku Kalitesini Artırmanın 10 Yolu"

  Generate with keywords:
    python -m src.main generate "Stres Yönetimi" --keywords "stres,rahatlama,wellness"

  Generate product description:
    python -m src.main generate "DailyGlow" --type product --product DailyGlow

  Index knowledge base:
    python -m src.main index --path ./knowledge_base

  Check status:
    python -m src.main status
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate content")
    gen_parser.add_argument("topic", help="Content topic in Turkish")
    gen_parser.add_argument(
        "--type", "-t",
        choices=["blog", "product", "social"],
        default="blog",
        help="Content type"
    )
    gen_parser.add_argument(
        "--keywords", "-k",
        help="Comma-separated keywords"
    )
    gen_parser.add_argument(
        "--product", "-p",
        help="Product to focus on (DailyGlow, MindFuel, etc.)"
    )
    gen_parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json", "shopify", "all"],
        default="all",
        help="Output format"
    )
    gen_parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish to Shopify"
    )
    gen_parser.add_argument(
        "--publish-live",
        action="store_true",
        help="Publish as live (not draft)"
    )
    gen_parser.set_defaults(func=cmd_generate)

    # Index command
    index_parser = subparsers.add_parser("index", help="Index knowledge base")
    index_parser.add_argument(
        "--path",
        help="Path to knowledge base directory"
    )
    index_parser.set_defaults(func=cmd_index)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show pipeline status")
    status_parser.set_defaults(func=cmd_status)

    # Agents command
    agents_parser = subparsers.add_parser("agents", help="Show agent information")
    agents_parser.set_defaults(func=cmd_agents)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
