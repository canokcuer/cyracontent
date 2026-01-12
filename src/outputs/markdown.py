"""
Markdown output handler for CyraSoul content.
"""

import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

from ..agents.can import ContentOutput


@dataclass
class MarkdownExportResult:
    """Result of markdown export."""
    file_path: Path
    success: bool
    error: Optional[str] = None


class MarkdownExporter:
    """
    Exports content to markdown files with frontmatter.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize markdown exporter.

        Args:
            output_dir: Directory for output files.
        """
        self.output_dir = output_dir or Path("output/articles")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        content_output: ContentOutput,
        filename: Optional[str] = None
    ) -> MarkdownExportResult:
        """
        Export content to markdown file.

        Args:
            content_output: Content to export.
            filename: Optional filename (without extension).

        Returns:
            MarkdownExportResult with file path.
        """
        try:
            # Generate filename from slug or title
            if not filename:
                filename = content_output.slug or self._slugify(content_output.title)

            # Ensure .md extension
            if not filename.endswith(".md"):
                filename = f"{filename}.md"

            file_path = self.output_dir / filename

            # Build frontmatter
            frontmatter = self._build_frontmatter(content_output)

            # Combine frontmatter and content
            full_content = f"---\n{frontmatter}---\n\n{content_output.content}"

            # Write file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_content)

            return MarkdownExportResult(
                file_path=file_path,
                success=True
            )

        except Exception as e:
            return MarkdownExportResult(
                file_path=Path(""),
                success=False,
                error=str(e)
            )

    def _build_frontmatter(self, content_output: ContentOutput) -> str:
        """Build YAML frontmatter."""
        lines = []

        lines.append(f"title: \"{content_output.title}\"")
        lines.append(f"description: \"{content_output.meta_description}\"")
        lines.append(f"slug: \"{content_output.slug}\"")
        lines.append(f"date: \"{datetime.now().strftime('%Y-%m-%d')}\"")
        lines.append(f"author: \"CyraSoul\"")

        if content_output.keywords:
            keywords_str = ", ".join(f'"{k}"' for k in content_output.keywords)
            lines.append(f"keywords: [{keywords_str}]")

        lines.append(f"seo_score: {content_output.seo_score}")
        lines.append(f"scientific_score: {content_output.scientific_score}")
        lines.append(f"word_count: {content_output.word_count}")

        return "\n".join(lines) + "\n"

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        import re

        # Turkish character mapping
        tr_map = {
            'ı': 'i', 'İ': 'i',
            'ğ': 'g', 'Ğ': 'g',
            'ü': 'u', 'Ü': 'u',
            'ş': 's', 'Ş': 's',
            'ö': 'o', 'Ö': 'o',
            'ç': 'c', 'Ç': 'c'
        }

        for tr_char, en_char in tr_map.items():
            text = text.replace(tr_char, en_char)

        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'\s+', '-', text)
        text = re.sub(r'-+', '-', text)
        text = text.strip('-')

        return text

    def export_batch(
        self,
        outputs: list,
        prefix: Optional[str] = None
    ) -> list:
        """
        Export multiple content outputs.

        Args:
            outputs: List of ContentOutput objects.
            prefix: Optional filename prefix.

        Returns:
            List of MarkdownExportResult.
        """
        results = []
        for i, output in enumerate(outputs):
            filename = f"{prefix}_{i+1}" if prefix else None
            result = self.export(output, filename)
            results.append(result)
        return results
