#!/usr/bin/env python3
"""
Verify knowledge base collections have data.
Exit 0 if all required collections have documents, exit 1 otherwise.
"""
import sys
import httpx

QDRANT_URL = "http://localhost:6333"
REQUIRED_COLLECTIONS = ["wellness", "products", "brand", "scientific"]

def check_collection(name: str) -> tuple[bool, int]:
    """Check if collection exists and has points."""
    try:
        response = httpx.get(f"{QDRANT_URL}/collections/{name}")
        if response.status_code != 200:
            return False, 0
        data = response.json()
        points_count = data.get("result", {}).get("points_count", 0)
        return points_count > 0, points_count
    except Exception as e:
        print(f"  Error checking {name}: {e}")
        return False, 0

def main():
    print("=" * 50)
    print("Knowledge Base Verification")
    print("=" * 50)

    all_ok = True
    results = []

    for collection in REQUIRED_COLLECTIONS:
        has_data, count = check_collection(collection)
        status = "OK" if has_data else "EMPTY"
        color = "\033[92m" if has_data else "\033[91m"  # Green or Red
        reset = "\033[0m"

        print(f"{color}[{status}]{reset} {collection}: {count} points")
        results.append((collection, has_data, count))

        if not has_data:
            all_ok = False

    print("=" * 50)

    if all_ok:
        print("\033[92mAll collections have data!\033[0m")
        return 0
    else:
        print("\033[91mSome collections are empty.\033[0m")
        print("\nTo fix, add documents to knowledge_base/ and run:")
        print("  uv run python -c \"from src.knowledge.loader import KnowledgeLoader; ...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
