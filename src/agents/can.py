"""
CAN Agent - Master Orchestrator for CyraSoul Content Pipeline.

This agent coordinates the entire content generation workflow,
managing FENIX (writer), HIPPOCRATES (reviewer), and NEO (SEO).
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

from .fenix import FenixAgent, ContentRequest, ContentDraft
from .hippocrates import HippocratesAgent, ScientificReview
from .neo import NeoAgent, SEOOptimizedContent
from ..rag.retriever import RAGRetriever

load_dotenv()


@dataclass
class PipelineState:
    """Current state of the content pipeline."""
    topic: str
    content_type: str
    stage: str  # init, fenix, hippocrates, neo, completed, failed
    started_at: str
    fenix_draft: Optional[ContentDraft] = None
    hippocrates_review: Optional[ScientificReview] = None
    neo_optimization: Optional[SEOOptimizedContent] = None
    final_content: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    completed_at: Optional[str] = None


@dataclass
class ContentOutput:
    """Final content output from the pipeline."""
    title: str
    content: str
    meta_description: str
    slug: str
    keywords: List[str]
    word_count: int
    seo_score: float
    scientific_score: float
    internal_links: List[Dict[str, str]]
    schema_markup: Optional[str]
    pipeline_state: PipelineState


class CANOrchestrator:
    """
    CAN - Master Orchestrator.

    Coordinates the multi-agent content generation pipeline:
    1. FENIX writes initial content
    2. HIPPOCRATES reviews for accuracy
    3. NEO optimizes for SEO
    """

    def __init__(
        self,
        state_dir: Optional[Path] = None,
        guardrails_path: Optional[Path] = None
    ):
        """
        Initialize CAN orchestrator.

        Args:
            state_dir: Directory for state files.
            guardrails_path: Path to guardrails.md file.
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        # Initialize agents
        self.fenix = FenixAgent()
        self.hippocrates = HippocratesAgent()
        self.neo = NeoAgent()

        # Initialize RAG retriever
        try:
            self.retriever = RAGRetriever()
        except Exception:
            self.retriever = None
            print("Warning: RAG retriever not available. Running without knowledge base.")

        # State management
        self.state_dir = state_dir or Path("state")
        self.state_dir.mkdir(exist_ok=True)

        # Load guardrails
        self.guardrails = None
        if guardrails_path and guardrails_path.exists():
            self.guardrails = guardrails_path.read_text(encoding="utf-8")
        elif (self.state_dir / "guardrails.md").exists():
            self.guardrails = (self.state_dir / "guardrails.md").read_text(encoding="utf-8")

    def generate_content(
        self,
        topic: str,
        content_type: str = "blog",
        keywords: Optional[List[str]] = None,
        product_focus: Optional[str] = None,
        max_revisions: int = 2
    ) -> ContentOutput:
        """
        Run the full content generation pipeline.

        Args:
            topic: Content topic in Turkish.
            content_type: Type of content (blog, product, social).
            keywords: Target keywords.
            product_focus: Optional product to focus on.
            max_revisions: Maximum revision iterations.

        Returns:
            ContentOutput with final content.
        """
        # Initialize state
        state = PipelineState(
            topic=topic,
            content_type=content_type,
            stage="init",
            started_at=datetime.now().isoformat()
        )
        self._save_state(state)

        try:
            # Phase 1: Retrieve knowledge context
            print(f"[CAN] Starting content generation for: {topic}")
            rag_context = self._get_rag_context(topic)

            # Phase 2: FENIX writes content
            print("[CAN] Phase 1: FENIX writing content...")
            state.stage = "fenix"
            self._save_state(state)

            request = ContentRequest(
                topic=topic,
                content_type=content_type,
                target_words=2000 if content_type == "blog" else 600,
                keywords=keywords or [],
                product_focus=product_focus
            )

            draft = self.fenix.generate_content(
                request=request,
                rag_context=rag_context,
                guardrails=self.guardrails
            )
            state.fenix_draft = draft
            self._save_state(state)
            print(f"[CAN] FENIX completed: {draft.word_count} words, {len(draft.sections)} sections")

            # Phase 3: HIPPOCRATES reviews content
            print("[CAN] Phase 2: HIPPOCRATES reviewing for accuracy...")
            state.stage = "hippocrates"
            self._save_state(state)

            scientific_context = self._get_scientific_context(topic)
            review = self.hippocrates.review_content(
                content=draft.content,
                title=draft.title,
                scientific_context=scientific_context
            )
            state.hippocrates_review = review
            self._save_state(state)
            print(f"[CAN] HIPPOCRATES completed: Score {review.overall_score}/100, "
                  f"{len(review.claims_found)} claims reviewed")

            # Handle review issues
            current_content = draft.content
            if not review.is_approved and review.revised_content:
                current_content = review.revised_content
                print("[CAN] HIPPOCRATES provided revised content")
            elif review.suggestions:
                # Let FENIX refine based on feedback
                feedback = "\n".join(review.suggestions)
                refined_draft = self.fenix.refine_content(draft, feedback)
                current_content = refined_draft.content
                print("[CAN] FENIX refined content based on HIPPOCRATES feedback")

            # Phase 4: NEO optimizes for SEO
            print("[CAN] Phase 3: NEO optimizing for SEO...")
            state.stage = "neo"
            self._save_state(state)

            optimized = self.neo.optimize_content(
                content=current_content,
                title=draft.title,
                target_keywords=keywords,
                content_type=content_type
            )
            state.neo_optimization = optimized
            self._save_state(state)
            print(f"[CAN] NEO completed: SEO Score {optimized.analysis.score}/100")

            # Finalize
            state.stage = "completed"
            state.final_content = optimized.content
            state.completed_at = datetime.now().isoformat()
            self._save_state(state)

            print("[CAN] Pipeline completed successfully!")

            return ContentOutput(
                title=optimized.metadata.title or draft.title,
                content=optimized.content,
                meta_description=optimized.metadata.meta_description,
                slug=optimized.metadata.slug,
                keywords=optimized.metadata.secondary_keywords,
                word_count=len(optimized.content.split()),
                seo_score=optimized.analysis.score,
                scientific_score=review.overall_score,
                internal_links=optimized.internal_links,
                schema_markup=optimized.schema_markup,
                pipeline_state=state
            )

        except Exception as e:
            state.stage = "failed"
            state.errors.append(str(e))
            self._save_state(state)
            raise

    def _get_rag_context(self, topic: str) -> Optional[str]:
        """Retrieve RAG context for topic."""
        if not self.retriever:
            return None

        try:
            results = self.retriever.retrieve_for_topic(topic)
            return self.retriever.format_topic_context(results)
        except Exception as e:
            print(f"[CAN] Warning: RAG retrieval failed: {e}")
            return None

    def _get_scientific_context(self, topic: str) -> Optional[str]:
        """Retrieve scientific context for topic."""
        if not self.retriever:
            return None

        try:
            results = self.retriever.retrieve(
                query=f"bilimsel araştırma {topic}",
                collections=["scientific"],
                top_k=5
            )
            return self.retriever.format_context(results, max_tokens=1000)
        except Exception as e:
            print(f"[CAN] Warning: Scientific context retrieval failed: {e}")
            return None

    def _save_state(self, state: PipelineState):
        """Save pipeline state to file."""
        state_file = self.state_dir / "pipeline-state.json"

        # Convert state to dict, handling dataclass objects
        state_dict = {
            "topic": state.topic,
            "content_type": state.content_type,
            "stage": state.stage,
            "started_at": state.started_at,
            "completed_at": state.completed_at,
            "errors": state.errors,
            "fenix_draft": asdict(state.fenix_draft) if state.fenix_draft else None,
            "hippocrates_review": {
                "is_approved": state.hippocrates_review.is_approved,
                "overall_score": state.hippocrates_review.overall_score,
                "issues": state.hippocrates_review.issues,
                "suggestions": state.hippocrates_review.suggestions
            } if state.hippocrates_review else None,
            "neo_optimization": {
                "seo_score": state.neo_optimization.analysis.score if state.neo_optimization else None
            } if state.neo_optimization else None
        }

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state_dict, f, ensure_ascii=False, indent=2)

    def _load_state(self) -> Optional[PipelineState]:
        """Load pipeline state from file."""
        state_file = self.state_dir / "pipeline-state.json"

        if not state_file.exists():
            return None

        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return PipelineState(
            topic=data.get("topic", ""),
            content_type=data.get("content_type", "blog"),
            stage=data.get("stage", "init"),
            started_at=data.get("started_at", ""),
            errors=data.get("errors", []),
            completed_at=data.get("completed_at")
        )

    def resume_pipeline(self) -> Optional[ContentOutput]:
        """
        Resume a previously interrupted pipeline.

        Returns:
            ContentOutput if pipeline can be resumed and completed.
        """
        state = self._load_state()
        if not state:
            print("[CAN] No previous state found")
            return None

        if state.stage == "completed":
            print("[CAN] Pipeline already completed")
            return None

        if state.stage == "failed":
            print("[CAN] Previous pipeline failed. Starting fresh.")
            return self.generate_content(state.topic, state.content_type)

        print(f"[CAN] Resuming pipeline from stage: {state.stage}")
        return self.generate_content(state.topic, state.content_type)

    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        state = self._load_state()
        if not state:
            return {"status": "idle", "message": "No active pipeline"}

        return {
            "status": state.stage,
            "topic": state.topic,
            "content_type": state.content_type,
            "started_at": state.started_at,
            "completed_at": state.completed_at,
            "errors": state.errors
        }
