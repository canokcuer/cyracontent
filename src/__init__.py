"""
CyraSoul Multi-Agent Content Generation Framework.

A multi-agent RAG system for generating Turkish wellness content using:
- FENIX: Content Writer
- HIPPOCRATES: Scientific Reviewer
- NEO: SEO Optimizer
- CAN: Orchestrator

Usage:
    from src.agents import CANOrchestrator

    orchestrator = CANOrchestrator()
    output = orchestrator.generate_content(
        topic="Uyku Kalitesini Artırmanın 10 Yolu",
        content_type="blog"
    )
"""

__version__ = "0.1.0"
__author__ = "CyraSoul"
