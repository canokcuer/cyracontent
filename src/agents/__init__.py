"""
CyraSoul Multi-Agent Content Generation Agents.
"""

from .fenix import FenixAgent, ContentRequest, ContentDraft
from .hippocrates import HippocratesAgent, HealthClaim, ScientificReview
from .neo import NeoAgent, SEOMetadata, SEOAnalysis, SEOOptimizedContent
from .can import CANOrchestrator, PipelineState, ContentOutput

__all__ = [
    # FENIX - Content Writer
    "FenixAgent",
    "ContentRequest",
    "ContentDraft",

    # HIPPOCRATES - Scientific Reviewer
    "HippocratesAgent",
    "HealthClaim",
    "ScientificReview",

    # NEO - SEO Optimizer
    "NeoAgent",
    "SEOMetadata",
    "SEOAnalysis",
    "SEOOptimizedContent",

    # CAN - Orchestrator
    "CANOrchestrator",
    "PipelineState",
    "ContentOutput",
]
