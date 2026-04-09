#!/usr/bin/env python3
"""Generate Pydantic v2 models from the Guru public Swagger spec.

Usage:
    python scripts/generate_models.py

What it does:
    1. Reads swagger/swagger.json (Swagger 2.0)
    2. Extracts definitions, filters out deprecated schemas
    3. Generates Pydantic v2 models via datamodel-code-generator
    4. Post-processes: replaces BaseModel with GuruModel, fixes imports
    5. Formats with ruff

Requires the 'codegen' extra:
    uv sync --extra codegen
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# =============================================================================
# Paths
# =============================================================================

ROOT = Path(__file__).resolve().parent.parent
SWAGGER_PATH = ROOT / "swagger" / "swagger.json"
OUTPUT_FILE = ROOT / "src" / "guru_sdk" / "models" / "_generated.py"

# =============================================================================
# Schemas to exclude — deprecated Guru concepts
# =============================================================================

# These are removed from the spec before generation so they never appear
# in the output. References to them from other schemas become Any.
EXCLUDED_SCHEMAS = {
    # Boards — replaced by Folders
    "Board",
    "BoardIdExpression",
    "BoardPermission",
    "BoardPermissions",
    # Legacy features — sunset or internal-only
    "Framework",
    "Question",
    "ReviewedAnswer",
    "AnswerSource",
    # Legacy analytics shapes — not exposed in modern API
    "CollectionStats",
    "TeamStats",
}

# =============================================================================
# Generation pipeline
# =============================================================================


def load_and_filter_spec(swagger_path: Path) -> dict:  # noqa: ANN401
    """Load the Swagger 2.0 spec and extract filtered definitions as JSON Schema."""
    with open(swagger_path) as f:
        spec = json.load(f)

    definitions = spec.get("definitions", {})
    original_count = len(definitions)

    # Remove excluded schemas
    for name in EXCLUDED_SCHEMAS:
        definitions.pop(name, None)

    # Rewrite $ref pointers that reference excluded schemas to be untyped
    _nullify_excluded_refs(definitions)

    filtered_count = len(definitions)
    print(f"  Definitions: {original_count} total, {original_count - filtered_count} excluded, {filtered_count} kept")

    # Wrap as a JSON Schema document so datamodel-codegen can parse it
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": definitions,
    }


def _nullify_excluded_refs(definitions: dict) -> None:  # noqa: ANN401
    """Walk the schema tree and replace $ref pointers to excluded schemas with {}."""
    for _name, schema in definitions.items():
        _walk_and_nullify(schema)


def _walk_and_nullify(node: dict | list) -> None:  # noqa: ANN401
    """Recursively walk a JSON structure, nullifying refs to excluded schemas."""
    if isinstance(node, dict):
        if "$ref" in node:
            ref_name = node["$ref"].rsplit("/", 1)[-1]
            if ref_name in EXCLUDED_SCHEMAS:
                # Replace the $ref with an untyped schema
                del node["$ref"]
                node["type"] = "object"
        for value in node.values():
            if isinstance(value, (dict, list)):
                _walk_and_nullify(value)
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, (dict, list)):
                _walk_and_nullify(item)


def run_codegen(schema: dict, output_file: Path) -> None:
    """Run datamodel-code-generator on the filtered schema."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(schema, f)
        temp_path = f.name

    cmd = [
        sys.executable, "-m", "datamodel_code_generator",
        "--input", temp_path,
        "--input-file-type", "jsonschema",
        "--output", str(output_file),
        "--output-model-type", "pydantic_v2.BaseModel",
        "--target-python-version", "3.10",
        "--use-annotated",
        "--field-constraints",
        "--use-default",
        "--collapse-root-models",
        "--use-standard-collections",
        "--no-allow-remote-refs",
        "--snake-case-field",
    ]

    print(f"  Running: datamodel-codegen → {output_file.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Clean up temp file
    Path(temp_path).unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"  ERROR: datamodel-codegen failed:\n{result.stderr}")
        sys.exit(1)

    # Print any warnings (but not the FutureWarning about formatters)
    stderr_lines = [
        line for line in result.stderr.splitlines()
        if line.strip() and "FutureWarning" not in line and "formatters" not in line
    ]
    for line in stderr_lines:
        print(f"  WARN: {line}")


def post_process(output_file: Path) -> None:
    """Replace BaseModel with GuruModel and fix imports."""
    content = output_file.read_text()

    # Replace the pydantic BaseModel import with GuruModel import
    # The generator produces: from pydantic import ..., BaseModel, ...
    # We need to add our GuruModel import and replace all `(BaseModel)` with `(GuruModel)`
    content = _replace_base_class(content)

    # Add module docstring at the top
    header = (
        '"""Auto-generated Pydantic v2 models from the Guru public API spec.\n'
        "\n"
        "DO NOT EDIT BY HAND. Re-generate with:\n"
        "    python scripts/generate_models.py\n"
        "\n"
        "Source: swagger/swagger.json\n"
        '"""\n\n'
    )

    # Replace the datamodel-codegen header comment
    content = re.sub(
        r"# generated by datamodel-codegen:.*?\n(?:#.*?\n)*\n",
        header,
        content,
        count=1,
    )

    output_file.write_text(content)
    print(f"  Post-processed: BaseModel → GuruModel, added module docstring")


def _replace_base_class(content: str) -> str:
    """Replace BaseModel inheritance with GuruModel."""
    # Add GuruModel import after the pydantic imports
    guru_import = "from guru_sdk.models._base import GuruModel\n"

    # Find the last pydantic import line and add ours after it
    lines = content.splitlines(True)

    # Note: we DON'T remove BaseModel from the pydantic import because
    # RootModel and other pydantic types may still need it. Instead, we
    # just add the GuruModel import.

    # Find insertion point: after last 'from pydantic' import
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("from pydantic"):
            insert_idx = i + 1

    lines.insert(insert_idx, "\n" + guru_import)
    content = "".join(lines)

    # Replace class inheritance: (BaseModel) → (GuruModel)
    # But NOT for RootModel or classes that already inherit from another generated class
    # Strategy: replace `(BaseModel):` at end of class definitions
    content = re.sub(r"\(BaseModel\):", "(GuruModel):", content)

    return content


def format_with_ruff(output_file: Path) -> None:
    """Format the generated file with ruff."""
    print(f"  Formatting with ruff")

    # ruff format
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "format", str(output_file)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  WARN: ruff format failed: {result.stderr}")

    # ruff check --fix (import sorting, etc.)
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--fix", str(output_file)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        # Some unfixable issues are expected in generated code
        fixable = [l for l in result.stdout.splitlines() if l.strip()]
        if fixable:
            print(f"  WARN: ruff check reported {len(fixable)} issues")


def print_summary(output_file: Path) -> None:
    """Print a summary of what was generated."""
    content = output_file.read_text()
    class_count = len(re.findall(r"^class \w+", content, re.MULTILINE))
    enum_count = len(re.findall(r"\(Enum\):", content))
    model_count = class_count - enum_count
    line_count = len(content.splitlines())

    print(f"\n  Generated: {output_file.relative_to(ROOT)}")
    print(f"  Lines:     {line_count}")
    print(f"  Classes:   {class_count} ({model_count} models, {enum_count} enums)")


# =============================================================================
# Main
# =============================================================================


def main() -> int:
    """Generate models from the Swagger spec."""
    print("guru-py-sdk: Model Generation Pipeline")
    print("=" * 50)

    if not SWAGGER_PATH.exists():
        print(f"\nERROR: Swagger spec not found at {SWAGGER_PATH}")
        print("Download it first:")
        print("  curl -o swagger/swagger.json https://api.getguru.com/api/v1/swagger.json")
        return 1

    # Step 1: Load and filter the spec
    print("\n1. Loading and filtering Swagger spec...")
    schema = load_and_filter_spec(SWAGGER_PATH)

    # Step 2: Run datamodel-code-generator
    print("\n2. Generating Pydantic v2 models...")
    run_codegen(schema, OUTPUT_FILE)

    # Step 3: Post-process (GuruModel base class, imports, docstring)
    print("\n3. Post-processing...")
    post_process(OUTPUT_FILE)

    # Step 4: Format with ruff
    print("\n4. Formatting...")
    format_with_ruff(OUTPUT_FILE)

    # Summary
    print_summary(OUTPUT_FILE)

    return 0


if __name__ == "__main__":
    sys.exit(main())
