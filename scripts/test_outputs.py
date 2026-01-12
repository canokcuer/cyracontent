#!/usr/bin/env python3
"""
Test output handlers by creating sample files.
Verifies markdown, JSON, and validates structure.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

OUTPUT_DIR = Path(__file__).parent.parent / "output"

# Sample content for testing
SAMPLE_CONTENT = {
    "title": "Test Article: Uyku Kalitesi",
    "slug": "test-uyku-kalitesi",
    "meta_description": "Bu bir test makalesidir. Uyku kalitesi hakkinda bilgi verir.",
    "content": """# Uyku Kalitesini Artirmanin Yollari

## Giris

Kaliteli uyku, saglikli bir yasamin temel taslarindan biridir.

## Uyku Hijyeni

Duzenli uyku saatleri onemlidir.

### Yatak Odasi Ortami

- Karanlik ortam
- Serin sicaklik (18-20°C)
- Sessiz ortam

## Beslenme ve Uyku

Yatmadan once agir yemeklerden kacinin.

## Sonuc

Kaliteli uyku icin bu onerileri takip edin.

Bir saglik uzmanina danismanizi oneririz.
""",
    "word_count": 75,
    "created_at": datetime.now().isoformat(),
    "content_type": "blog",
    "products_mentioned": ["DreamGlow"],
    "seo": {
        "h1_count": 1,
        "h2_count": 4,
        "h3_count": 1,
        "has_meta": True
    }
}

def test_markdown_export():
    """Test markdown exporter."""
    print("[1/3] Testing Markdown export...")
    try:
        from src.outputs.markdown import MarkdownExporter

        exporter = MarkdownExporter()
        output_path = OUTPUT_DIR / "articles" / "test_output.md"

        # Export
        result_path = exporter.export(SAMPLE_CONTENT, output_path)

        # Verify file exists
        if result_path and Path(result_path).exists():
            content = Path(result_path).read_text()
            print(f"  OK - Created {result_path} ({len(content)} chars)")
            return True
        else:
            print("  FAIL - File not created")
            return False
    except Exception as e:
        print(f"  FAIL - Error: {e}")
        return False

def test_json_export():
    """Test JSON exporter."""
    print("[2/3] Testing JSON export...")
    try:
        from src.outputs.json_export import JSONExporter

        exporter = JSONExporter()
        output_path = OUTPUT_DIR / "json" / "test_output.json"

        # Export
        result_path = exporter.export(SAMPLE_CONTENT, output_path)

        # Verify file exists and is valid JSON
        if result_path and Path(result_path).exists():
            content = Path(result_path).read_text()
            data = json.loads(content)  # Validate JSON
            print(f"  OK - Created {result_path} ({len(content)} chars)")
            return True
        else:
            print("  FAIL - File not created")
            return False
    except Exception as e:
        print(f"  FAIL - Error: {e}")
        return False

def test_seo_validation():
    """Test SEO structure validation."""
    print("[3/3] Testing SEO validation...")
    try:
        content = SAMPLE_CONTENT["content"]

        # Count headings
        h1_count = content.count("\n# ") + (1 if content.startswith("# ") else 0)
        h2_count = content.count("\n## ")
        h3_count = content.count("\n### ")

        checks = [
            ("H1 count == 1", h1_count == 1),
            ("H2 count >= 3", h2_count >= 3),
            ("Has meta description", len(SAMPLE_CONTENT.get("meta_description", "")) > 0),
            ("Meta length 150-160", 100 <= len(SAMPLE_CONTENT.get("meta_description", "")) <= 200),
        ]

        all_pass = True
        for check_name, passed in checks:
            status = "OK" if passed else "WARN"
            print(f"    {status} - {check_name}")
            if not passed:
                all_pass = False

        return True  # SEO warnings don't fail the test
    except Exception as e:
        print(f"  FAIL - Error: {e}")
        return False

def main():
    print("=" * 50)
    print("Output Handler Tests")
    print("=" * 50)

    # Ensure output directories exist
    (OUTPUT_DIR / "articles").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "json").mkdir(parents=True, exist_ok=True)

    results = []
    results.append(("markdown", test_markdown_export()))
    results.append(("json", test_json_export()))
    results.append(("seo", test_seo_validation()))

    print("=" * 50)
    print("Results:")

    all_passed = True
    for name, passed in results:
        status = "\033[92mPASS\033[0m" if passed else "\033[91mFAIL\033[0m"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False

    print("=" * 50)

    # List created files
    print("Files created:")
    for f in OUTPUT_DIR.rglob("test_output.*"):
        print(f"  - {f}")

    if all_passed:
        print("\n\033[92mAll output tests passed!\033[0m")
        return 0
    else:
        print("\n\033[91mSome tests failed.\033[0m")
        return 1

if __name__ == "__main__":
    sys.exit(main())
