"""
JSON output handler for CyraSoul content.
Exports content in structured JSON format for CMS integration.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from ..agents.can import ContentOutput


@dataclass
class JSONExportResult:
    """Result of JSON export."""
    file_path: Optional[Path]
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class JSONExporter:
    """
    Exports content to structured JSON format.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize JSON exporter.

        Args:
            output_dir: Directory for output files.
        """
        self.output_dir = output_dir or Path("output/json")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        content_output: ContentOutput,
        filename: Optional[str] = None,
        include_pipeline_state: bool = False
    ) -> JSONExportResult:
        """
        Export content to JSON file.

        Args:
            content_output: Content to export.
            filename: Optional filename (without extension).
            include_pipeline_state: Whether to include full pipeline state.

        Returns:
            JSONExportResult with file path and data.
        """
        try:
            # Build JSON structure
            data = self._build_json_structure(content_output, include_pipeline_state)

            # Generate filename
            if not filename:
                filename = content_output.slug or f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if not filename.endswith(".json"):
                filename = f"{filename}.json"

            file_path = self.output_dir / filename

            # Write file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return JSONExportResult(
                file_path=file_path,
                success=True,
                data=data
            )

        except Exception as e:
            return JSONExportResult(
                file_path=None,
                success=False,
                error=str(e)
            )

    def export_to_dict(
        self,
        content_output: ContentOutput,
        include_pipeline_state: bool = False
    ) -> Dict[str, Any]:
        """
        Export content to dictionary without saving to file.

        Args:
            content_output: Content to export.
            include_pipeline_state: Whether to include full pipeline state.

        Returns:
            Dictionary with content data.
        """
        return self._build_json_structure(content_output, include_pipeline_state)

    def _build_json_structure(
        self,
        content_output: ContentOutput,
        include_pipeline_state: bool
    ) -> Dict[str, Any]:
        """Build the JSON structure for export."""
        data = {
            "metadata": {
                "title": content_output.title,
                "meta_description": content_output.meta_description,
                "slug": content_output.slug,
                "keywords": content_output.keywords,
                "word_count": content_output.word_count,
                "created_at": datetime.now().isoformat(),
                "author": "CyraSoul",
                "language": "tr"
            },
            "content": {
                "body": content_output.content,
                "format": "markdown"
            },
            "seo": {
                "score": content_output.seo_score,
                "internal_links": content_output.internal_links,
                "schema_markup": content_output.schema_markup
            },
            "quality": {
                "scientific_score": content_output.scientific_score,
                "seo_score": content_output.seo_score
            }
        }

        if include_pipeline_state:
            state = content_output.pipeline_state
            data["pipeline"] = {
                "topic": state.topic,
                "content_type": state.content_type,
                "stage": state.stage,
                "started_at": state.started_at,
                "completed_at": state.completed_at,
                "errors": state.errors
            }

        return data

    def export_social_media(
        self,
        content_output: ContentOutput,
        platform: str = "all"
    ) -> JSONExportResult:
        """
        Export content formatted for social media.

        Args:
            content_output: Content to export.
            platform: Target platform (instagram, facebook, all).

        Returns:
            JSONExportResult with social media formatted content.
        """
        try:
            # Extract first paragraphs for social posts
            paragraphs = content_output.content.split("\n\n")
            intro = paragraphs[0] if paragraphs else ""

            # Remove markdown formatting
            import re
            clean_intro = re.sub(r'[#*\[\]()]', '', intro).strip()

            data = {
                "source": {
                    "title": content_output.title,
                    "slug": content_output.slug,
                    "url": f"https://cyrasoul.com/blog/{content_output.slug}"
                },
                "platforms": {}
            }

            if platform in ["instagram", "all"]:
                # Instagram: max 2200 chars, hashtags
                ig_text = clean_intro[:1800] if len(clean_intro) > 1800 else clean_intro
                hashtags = self._generate_hashtags(content_output.keywords)
                data["platforms"]["instagram"] = {
                    "caption": ig_text,
                    "hashtags": hashtags,
                    "full_post": f"{ig_text}\n\n{hashtags}",
                    "char_count": len(ig_text) + len(hashtags)
                }

            if platform in ["facebook", "all"]:
                # Facebook: shorter, with link
                fb_text = clean_intro[:400] if len(clean_intro) > 400 else clean_intro
                fb_cta = f"\n\n👉 Devamını oku: https://cyrasoul.com/blog/{content_output.slug}"
                data["platforms"]["facebook"] = {
                    "post": fb_text,
                    "full_post": f"{fb_text}{fb_cta}",
                    "char_count": len(fb_text) + len(fb_cta)
                }

            if platform in ["twitter", "all"]:
                # Twitter: max 280 chars
                tw_text = clean_intro[:200] if len(clean_intro) > 200 else clean_intro
                tw_link = f" https://cyrasoul.com/blog/{content_output.slug}"
                data["platforms"]["twitter"] = {
                    "tweet": tw_text,
                    "full_post": f"{tw_text}{tw_link}",
                    "char_count": len(tw_text) + len(tw_link)
                }

            # Generate filename
            filename = f"social_{content_output.slug}.json"
            file_path = self.output_dir / filename

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return JSONExportResult(
                file_path=file_path,
                success=True,
                data=data
            )

        except Exception as e:
            return JSONExportResult(
                file_path=None,
                success=False,
                error=str(e)
            )

    def _generate_hashtags(self, keywords: list, max_tags: int = 20) -> str:
        """Generate Instagram hashtags from keywords."""
        base_hashtags = [
            "#wellness", "#saglik", "#saglikliYasam", "#cyrasoul",
            "#takviye", "#vitaminler", "#dogalYasam"
        ]

        keyword_hashtags = []
        for kw in keywords[:10]:
            # Convert to hashtag format
            tag = kw.replace(" ", "").replace("-", "")
            keyword_hashtags.append(f"#{tag}")

        all_hashtags = keyword_hashtags + base_hashtags
        return " ".join(all_hashtags[:max_tags])
