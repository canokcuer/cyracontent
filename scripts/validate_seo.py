#!/usr/bin/env python3
"""
SEO Validation Script for CyraSoul Content.
Validates content against SEO standards defined in knowledge_base/seo/standards.md

Usage:
    uv run python scripts/validate_seo.py output/articles/my-article.md
    uv run python scripts/validate_seo.py --json '{"title": "...", "content": "..."}'

Exit codes:
    0 - Score >= 80 (Excellent)
    1 - Score 60-79 (Good, minor fixes needed)
    2 - Score 40-59 (Needs work)
    3 - Score < 40 (Poor, rewrite needed)
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Turkish character mapping for slug validation
TURKISH_CHARS = "şğüöçıİŞĞÜÖÇ"

class SEOValidator:
    """Validates content against CyraSoul SEO standards."""

    # Thresholds from standards.md
    RULES = {
        "h1_length_min": 50,
        "h1_length_max": 60,
        "h2_count_min": 3,
        "h2_count_max": 7,
        "meta_desc_min": 150,
        "meta_desc_max": 160,
        "slug_max_words": 5,
        "blog_words_min": 1500,
        "blog_words_max": 2500,
        "product_words_min": 500,
        "product_words_max": 1000,
        "keyword_density_min": 0.01,
        "keyword_density_max": 0.02,
        "internal_links_min": 2,
        "paragraph_sentences_max": 4,
    }

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.score = 0

    def validate(self, content: dict) -> dict:
        """
        Validate content and return results.

        Args:
            content: dict with keys: title, content, meta_description, slug,
                     content_type, keyword (optional)

        Returns:
            dict with score, errors, warnings, and detailed checks
        """
        self.errors = []
        self.warnings = []
        self.score = 0

        checks = {}

        # Extract content text
        text = content.get("content", "")
        content_type = content.get("content_type", "blog")

        # 1. H1 validation (10 points)
        h1_check = self._check_h1(text, content.get("title", ""))
        checks["h1"] = h1_check
        if h1_check["pass"]:
            self.score += 10

        # 2. H2 count validation (10 points)
        h2_check = self._check_h2_count(text)
        checks["h2_count"] = h2_check
        if h2_check["pass"]:
            self.score += 10

        # 3. Meta description validation (10 points)
        meta_check = self._check_meta_description(content.get("meta_description", ""))
        checks["meta_description"] = meta_check
        if meta_check["pass"]:
            self.score += 10

        # 4. URL slug validation (10 points)
        slug_check = self._check_slug(content.get("slug", ""))
        checks["slug"] = slug_check
        if slug_check["pass"]:
            self.score += 10

        # 5. Word count validation (10 points)
        word_check = self._check_word_count(text, content_type)
        checks["word_count"] = word_check
        if word_check["pass"]:
            self.score += 10

        # 6. Keyword in first 100 words (10 points)
        keyword = content.get("keyword", "")
        keyword_check = self._check_keyword_placement(text, keyword)
        checks["keyword_placement"] = keyword_check
        if keyword_check["pass"]:
            self.score += 10

        # 7. Has list (10 points)
        list_check = self._check_has_list(text)
        checks["has_list"] = list_check
        if list_check["pass"]:
            self.score += 10

        # 8. Internal links (10 points)
        links_check = self._check_internal_links(text)
        checks["internal_links"] = links_check
        if links_check["pass"]:
            self.score += 10

        # 9. No Turkish chars in slug (10 points) - already in slug check
        # 10. Readability (10 points)
        readability_check = self._check_readability(text)
        checks["readability"] = readability_check
        if readability_check["pass"]:
            self.score += 10

        # 11. H3 structure (bonus, doesn't affect score but warns)
        h3_check = self._check_h3_structure(text)
        checks["h3_structure"] = h3_check

        return {
            "score": self.score,
            "grade": self._get_grade(self.score),
            "errors": self.errors,
            "warnings": self.warnings,
            "checks": checks,
            "recommendation": self._get_recommendation(self.score)
        }

    def _check_h1(self, text: str, title: str) -> dict:
        """Check H1 exists and has correct length."""
        # Find H1 in markdown
        h1_match = re.search(r'^# (.+)$', text, re.MULTILINE)
        h1_text = h1_match.group(1) if h1_match else title

        h1_count = len(re.findall(r'^# ', text, re.MULTILINE))
        length = len(h1_text) if h1_text else 0

        passed = True
        issues = []

        if h1_count == 0:
            issues.append("No H1 found")
            self.errors.append("Missing H1 heading")
            passed = False
        elif h1_count > 1:
            issues.append(f"Multiple H1s found ({h1_count})")
            self.errors.append("Multiple H1 headings (should be 1)")
            passed = False

        if length < self.RULES["h1_length_min"]:
            issues.append(f"H1 too short ({length} chars, min {self.RULES['h1_length_min']})")
            self.warnings.append(f"H1 too short: {length} chars")
            passed = False
        elif length > self.RULES["h1_length_max"]:
            issues.append(f"H1 too long ({length} chars, max {self.RULES['h1_length_max']})")
            self.warnings.append(f"H1 too long: {length} chars")
            passed = False

        return {"pass": passed, "value": h1_text, "length": length, "count": h1_count, "issues": issues}

    def _check_h2_count(self, text: str) -> dict:
        """Check H2 count is within range."""
        h2_matches = re.findall(r'^## (.+)$', text, re.MULTILINE)
        count = len(h2_matches)

        passed = self.RULES["h2_count_min"] <= count <= self.RULES["h2_count_max"]
        issues = []

        if count < self.RULES["h2_count_min"]:
            issues.append(f"Too few H2s ({count}, min {self.RULES['h2_count_min']})")
            self.errors.append(f"Need at least {self.RULES['h2_count_min']} H2 headings")
        elif count > self.RULES["h2_count_max"]:
            issues.append(f"Too many H2s ({count}, max {self.RULES['h2_count_max']})")
            self.warnings.append(f"Consider reducing H2 count from {count}")

        return {"pass": passed, "count": count, "headings": h2_matches[:5], "issues": issues}

    def _check_meta_description(self, meta: str) -> dict:
        """Check meta description length."""
        length = len(meta) if meta else 0
        passed = self.RULES["meta_desc_min"] <= length <= self.RULES["meta_desc_max"]
        issues = []

        if length == 0:
            issues.append("No meta description")
            self.errors.append("Missing meta description")
        elif length < self.RULES["meta_desc_min"]:
            issues.append(f"Too short ({length} chars, min {self.RULES['meta_desc_min']})")
            self.errors.append(f"Meta description too short: {length} chars")
        elif length > self.RULES["meta_desc_max"]:
            issues.append(f"Too long ({length} chars, max {self.RULES['meta_desc_max']})")
            self.warnings.append(f"Meta description too long: {length} chars")

        return {"pass": passed, "length": length, "issues": issues}

    def _check_slug(self, slug: str) -> dict:
        """Check URL slug is valid."""
        issues = []
        passed = True

        if not slug:
            issues.append("No slug provided")
            self.errors.append("Missing URL slug")
            return {"pass": False, "value": slug, "issues": issues}

        # Check for Turkish characters
        has_turkish = any(c in slug for c in TURKISH_CHARS)
        if has_turkish:
            issues.append("Contains Turkish characters")
            self.errors.append("Slug contains Turkish characters (use ASCII)")
            passed = False

        # Check word count
        words = slug.split("-")
        if len(words) > self.RULES["slug_max_words"]:
            issues.append(f"Too many words ({len(words)}, max {self.RULES['slug_max_words']})")
            self.warnings.append(f"Slug too long: {len(words)} words")
            passed = False

        # Check lowercase
        if slug != slug.lower():
            issues.append("Not lowercase")
            self.warnings.append("Slug should be lowercase")

        return {"pass": passed, "value": slug, "word_count": len(words), "issues": issues}

    def _check_word_count(self, text: str, content_type: str) -> dict:
        """Check word count matches content type requirements."""
        # Remove markdown syntax for accurate count
        clean_text = re.sub(r'[#*`\[\]()]', '', text)
        words = len(clean_text.split())

        if content_type == "blog":
            min_words = self.RULES["blog_words_min"]
            max_words = self.RULES["blog_words_max"]
        elif content_type == "product":
            min_words = self.RULES["product_words_min"]
            max_words = self.RULES["product_words_max"]
        else:
            min_words = 100
            max_words = 5000

        passed = min_words <= words <= max_words
        issues = []

        if words < min_words:
            issues.append(f"Too short ({words} words, min {min_words})")
            self.errors.append(f"Content too short: {words} words (min {min_words})")
        elif words > max_words:
            issues.append(f"Too long ({words} words, max {max_words})")
            self.warnings.append(f"Content too long: {words} words")

        return {"pass": passed, "count": words, "min": min_words, "max": max_words, "issues": issues}

    def _check_keyword_placement(self, text: str, keyword: str) -> dict:
        """Check keyword appears in first 100 words."""
        if not keyword:
            return {"pass": True, "issues": ["No keyword specified (skipped)"]}

        words = text.split()[:100]
        first_100 = " ".join(words).lower()
        keyword_lower = keyword.lower()

        found = keyword_lower in first_100
        issues = []

        if not found:
            issues.append(f"Keyword '{keyword}' not in first 100 words")
            self.warnings.append(f"Add keyword '{keyword}' to introduction")

        return {"pass": found, "keyword": keyword, "issues": issues}

    def _check_has_list(self, text: str) -> dict:
        """Check content has at least one list."""
        bullet_lists = len(re.findall(r'^[\-\*] ', text, re.MULTILINE))
        numbered_lists = len(re.findall(r'^\d+\. ', text, re.MULTILINE))
        total = bullet_lists + numbered_lists

        passed = total >= 3  # At least 3 list items
        issues = []

        if total == 0:
            issues.append("No lists found")
            self.warnings.append("Add at least one bulleted or numbered list")

        return {"pass": passed, "bullet_items": bullet_lists, "numbered_items": numbered_lists, "issues": issues}

    def _check_internal_links(self, text: str) -> dict:
        """Check for internal links."""
        # Match markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)

        # Filter for internal links (cyrasoul.com or relative)
        internal = [l for l in links if 'cyrasoul.com' in l[1] or l[1].startswith('/')]
        count = len(internal)

        passed = count >= self.RULES["internal_links_min"]
        issues = []

        if count < self.RULES["internal_links_min"]:
            issues.append(f"Only {count} internal links (min {self.RULES['internal_links_min']})")
            self.warnings.append(f"Add more internal links ({count} found, need {self.RULES['internal_links_min']})")

        return {"pass": passed, "count": count, "links": internal[:5], "issues": issues}

    def _check_readability(self, text: str) -> dict:
        """Check readability (paragraph length, sentence length)."""
        paragraphs = [p for p in text.split('\n\n') if p.strip() and not p.startswith('#')]

        long_paragraphs = 0
        for p in paragraphs:
            sentences = re.split(r'[.!?]+', p)
            if len([s for s in sentences if s.strip()]) > self.RULES["paragraph_sentences_max"]:
                long_paragraphs += 1

        passed = long_paragraphs <= 2  # Allow max 2 long paragraphs
        issues = []

        if long_paragraphs > 0:
            issues.append(f"{long_paragraphs} paragraphs too long (max {self.RULES['paragraph_sentences_max']} sentences)")
            if long_paragraphs > 2:
                self.warnings.append("Break up long paragraphs for readability")

        return {"pass": passed, "long_paragraphs": long_paragraphs, "total_paragraphs": len(paragraphs), "issues": issues}

    def _check_h3_structure(self, text: str) -> dict:
        """Check H3 usage is reasonable."""
        h3_matches = re.findall(r'^### (.+)$', text, re.MULTILINE)
        count = len(h3_matches)

        issues = []
        if count > 10:
            issues.append(f"Many H3s ({count}), consider restructuring")
            self.warnings.append("Consider reducing H3 headings")

        return {"pass": True, "count": count, "issues": issues}

    def _get_grade(self, score: int) -> str:
        """Convert score to grade."""
        if score >= 80:
            return "A (Excellent)"
        elif score >= 60:
            return "B (Good)"
        elif score >= 40:
            return "C (Needs Work)"
        else:
            return "D (Poor)"

    def _get_recommendation(self, score: int) -> str:
        """Get recommendation based on score."""
        if score >= 80:
            return "Ready to publish"
        elif score >= 60:
            return "Minor fixes needed, then publish"
        elif score >= 40:
            return "Send back to NEO for revision"
        else:
            return "Major rewrite needed"


def parse_markdown_file(filepath: str) -> dict:
    """Parse markdown file into content dict."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    text = path.read_text(encoding="utf-8")

    # Extract frontmatter if present
    meta_desc = ""
    slug = path.stem  # Default to filename
    keyword = ""

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            text = parts[2]

            # Parse frontmatter
            for line in frontmatter.strip().split("\n"):
                if line.startswith("description:"):
                    meta_desc = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("slug:"):
                    slug = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("keyword:"):
                    keyword = line.split(":", 1)[1].strip().strip('"\'')

    # Extract title from H1
    h1_match = re.search(r'^# (.+)$', text, re.MULTILINE)
    title = h1_match.group(1) if h1_match else ""

    return {
        "title": title,
        "content": text,
        "meta_description": meta_desc,
        "slug": slug,
        "keyword": keyword,
        "content_type": "blog"
    }


def main():
    parser = argparse.ArgumentParser(description="Validate content against SEO standards")
    parser.add_argument("file", nargs="?", help="Markdown file to validate")
    parser.add_argument("--json", help="JSON content to validate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    if args.json:
        content = json.loads(args.json)
    elif args.file:
        content = parse_markdown_file(args.file)
    else:
        print("Error: Provide either a file path or --json content")
        return 1

    validator = SEOValidator()
    result = validator.validate(content)

    # Output
    print("=" * 60)
    print(f"SEO VALIDATION REPORT")
    print("=" * 60)
    print(f"\nScore: {result['score']}/100 ({result['grade']})")
    print(f"Recommendation: {result['recommendation']}")

    if result["errors"]:
        print(f"\n{chr(10060)} ERRORS ({len(result['errors'])}):")
        for err in result["errors"]:
            print(f"  - {err}")

    if result["warnings"]:
        print(f"\n{chr(9888)} WARNINGS ({len(result['warnings'])}):")
        for warn in result["warnings"]:
            print(f"  - {warn}")

    if args.verbose:
        print("\nDETAILED CHECKS:")
        for check_name, check_result in result["checks"].items():
            status = chr(9989) if check_result["pass"] else chr(10060)
            print(f"  {status} {check_name}: {check_result.get('issues', [])}")

    print("=" * 60)

    # Exit code based on score
    if result["score"] >= 80:
        return 0
    elif result["score"] >= 60:
        return 1
    elif result["score"] >= 40:
        return 2
    else:
        return 3


if __name__ == "__main__":
    sys.exit(main())
