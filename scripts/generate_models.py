#!/usr/bin/env python3
"""Generate Pydantic v2 models from the Guru public Swagger spec.

Usage:
    python scripts/generate_models.py

What it does:
    1. Reads swagger/swagger.json
    2. Generates Pydantic v2 models via datamodel-code-generator
    3. Applies GuruModel base class (extra="ignore")
    4. Filters out deprecated/board-related schemas
    5. Formats with ruff

Requires the 'codegen' extra:
    pip install guru-sdk[codegen]
"""

from __future__ import annotations

import sys
from pathlib import Path

# =============================================================================
# Paths
# =============================================================================

ROOT = Path(__file__).resolve().parent.parent
SWAGGER_PATH = ROOT / "swagger" / "swagger.json"
OUTPUT_DIR = ROOT / "src" / "guru_sdk" / "models"

# =============================================================================
# Schemas to exclude — deprecated Guru concepts
# =============================================================================

EXCLUDED_SCHEMAS = {
    "Board",
    "BoardGroup",
    "BoardPermission",
    "HomeBoard",
    "Section",
    "Framework",
    "Question",
    "ReviewedAnswer",
    "AnswerSource",
    "CollectionStats",
    "TeamStats",
}


def main() -> int:
    """Generate models from the Swagger spec."""
    if not SWAGGER_PATH.exists():
        print(f"ERROR: Swagger spec not found at {SWAGGER_PATH}")
        print("Download it first:")
        print("  curl -o swagger/swagger.json https://api.getguru.com/api/v1/swagger.json")
        return 1

    # Phase 2 will implement the full generation pipeline:
    # 1. Load swagger.json
    # 2. Filter out EXCLUDED_SCHEMAS
    # 3. Run datamodel-code-generator with GuruModel base class
    # 4. Post-process: apply field alias mappings
    # 5. Format with ruff
    print("Model generation will be implemented in Phase 2.")
    print(f"  Swagger spec: {SWAGGER_PATH}")
    print(f"  Output dir:   {OUTPUT_DIR}")
    print(f"  Excluded:     {len(EXCLUDED_SCHEMAS)} deprecated schemas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
