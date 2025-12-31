#!/usr/bin/env python3
"""
Split openapi-combined.json into openapi-gpt.json and openapi-full.json.

- openapi-gpt.json: <=30 operations for ChatGPT (removes /api/koi/stats, /api/koi/health)
- openapi-full.json: All operations including dev/ops endpoints

Usage: python scripts/split_openapi.py
"""

import json
import copy
from pathlib import Path

# Paths to exclude from GPT schema to stay under 30 operations
GPT_EXCLUDE_PATHS = [
    "/api/koi/stats",
    "/api/koi/health",
]

def count_operations(schema):
    """Count total HTTP operations in schema."""
    count = 0
    for path, methods in schema.get("paths", {}).items():
        for method in methods:
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                count += 1
    return count

def main():
    script_dir = Path(__file__).parent
    repo_dir = script_dir.parent

    combined_path = repo_dir / "openapi-combined.json"
    gpt_path = repo_dir / "openapi-gpt.json"
    full_path = repo_dir / "openapi-full.json"

    # Load combined schema
    with open(combined_path) as f:
        combined = json.load(f)

    print(f"Loaded openapi-combined.json: {count_operations(combined)} operations")

    # Create full schema (copy of combined)
    full = copy.deepcopy(combined)
    full["info"]["title"] = "Regen Network Full API"
    full["info"]["description"] = combined["info"]["description"] + " (Full schema including dev/ops endpoints)"

    # Create GPT schema (combined minus excluded paths)
    gpt = copy.deepcopy(combined)
    gpt["info"]["title"] = "Regen Network GPT API"
    gpt["info"]["description"] = combined["info"]["description"] + " (Optimized for ChatGPT - max 30 operations)"

    for path in GPT_EXCLUDE_PATHS:
        if path in gpt["paths"]:
            del gpt["paths"][path]
            print(f"  Removed from GPT: {path}")

    gpt_ops = count_operations(gpt)
    full_ops = count_operations(full)

    print(f"\nGenerated schemas:")
    print(f"  openapi-gpt.json: {gpt_ops} operations {'(OK)' if gpt_ops <= 30 else '(OVER LIMIT!)'}")
    print(f"  openapi-full.json: {full_ops} operations")

    # Save schemas
    with open(gpt_path, "w") as f:
        json.dump(gpt, f, indent=2)
    print(f"\nSaved: {gpt_path}")

    with open(full_path, "w") as f:
        json.dump(full, f, indent=2)
    print(f"Saved: {full_path}")

    # Verify GPT limit
    if gpt_ops > 30:
        print(f"\n⚠️  WARNING: GPT schema has {gpt_ops} operations (limit: 30)")
        print("   Add more paths to GPT_EXCLUDE_PATHS to reduce count")
        return 1

    print("\n✅ Schema split complete")
    return 0

if __name__ == "__main__":
    exit(main())
