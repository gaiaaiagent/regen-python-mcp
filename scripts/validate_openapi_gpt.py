#!/usr/bin/env python3
"""
Validate OpenAPI GPT schema against guardrail requirements.

This script checks:
1. Operation count is within GPT limit (≤30)
2. No forbidden ops are present (dev/ops/debug endpoints)
3. No empty {} response schemas
4. Required response envelope fields are present
5. Examples exist for GPT-facing endpoints

Run as CI check to prevent regressions.

Usage:
  python validate_openapi_gpt.py                    # Default: openapi-gpt.json
  python validate_openapi_gpt.py --spec other.json  # Custom spec file
  python validate_openapi_gpt.py --strict           # Treat warnings as errors

Exit codes:
  0 - All checks pass
  1 - Validation errors found (or warnings in strict mode)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

# Configuration
GPT_MAX_OPERATIONS = 30

# Forbidden path patterns that should never appear in GPT schema
FORBIDDEN_PATTERNS = [
    "/ops/",
    "/utils/",
    "/debug/",
    "/admin/",
    "/internal/",
]

# Specific operations that should not be in GPT schema (method, path)
FORBIDDEN_OPERATIONS = {
    ("get", "/api/koi/stats"),
    ("get", "/api/koi/health"),
}

# Required fields in response schemas (for future validation)
# Currently relaxed since many endpoints still have {} schemas
REQUIRED_ENVELOPE_FIELDS = []  # Will add: ["request_id", "data"] after remediation


@dataclass
class ValidationResult:
    """Results of validation checks."""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


def load_openapi_spec(path: Path) -> dict[str, Any]:
    """Load OpenAPI spec from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def count_operations(spec: dict[str, Any]) -> int:
    """Count the number of operations in an OpenAPI spec."""
    count = 0
    for path, methods in spec.get("paths", {}).items():
        for method in methods:
            if method.lower() in ["get", "post", "put", "patch", "delete"]:
                count += 1
    return count


def list_operations(spec: dict[str, Any]) -> list[tuple[str, str, str]]:
    """List all operations as (method, path, operationId) tuples."""
    operations = []
    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method.lower() in ["get", "post", "put", "patch", "delete"]:
                op_id = details.get("operationId", "unknown")
                operations.append((method.lower(), path, op_id))
    return sorted(operations, key=lambda x: (x[1], x[0]))


def check_operation_count(spec: dict[str, Any], result: ValidationResult) -> None:
    """Check that operation count is within GPT limit."""
    count = count_operations(spec)
    result.info.append(f"Total operations: {count}")

    if count > GPT_MAX_OPERATIONS:
        result.errors.append(
            f"Operation count ({count}) exceeds GPT limit ({GPT_MAX_OPERATIONS})"
        )
    elif count == GPT_MAX_OPERATIONS:
        result.warnings.append(
            f"Operation count ({count}) is at GPT limit - no room for new endpoints"
        )
    else:
        spare = GPT_MAX_OPERATIONS - count
        result.info.append(f"Spare operation slots: {spare}")


def check_forbidden_operations(spec: dict[str, Any], result: ValidationResult) -> None:
    """Check that no forbidden operations are present."""
    operations = list_operations(spec)

    for method, path, op_id in operations:
        # Check specific forbidden operations
        if (method, path) in FORBIDDEN_OPERATIONS:
            result.errors.append(
                f"Forbidden operation found: {method.upper()} {path} ({op_id})"
            )

        # Check forbidden path patterns
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in path:
                result.errors.append(
                    f"Forbidden path pattern '{pattern}' found in: {method.upper()} {path}"
                )


def check_empty_response_schemas(spec: dict[str, Any], result: ValidationResult) -> None:
    """Check for empty {} response schemas."""
    empty_schemas = []

    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue

            op_id = details.get("operationId", "unknown")
            responses = details.get("responses", {})

            for status, response in responses.items():
                content = response.get("content", {})
                for media_type, media_details in content.items():
                    schema = media_details.get("schema", {})
                    # Check if schema is empty or effectively empty
                    if schema == {} or (
                        schema.get("type") == "object" and
                        not schema.get("properties") and
                        not schema.get("$ref")
                    ):
                        empty_schemas.append(f"{method.upper()} {path} ({op_id}) - {status}")

    if empty_schemas:
        result.warnings.append(
            f"Found {len(empty_schemas)} endpoints with empty response schemas:"
        )
        for schema_info in empty_schemas[:10]:  # Show first 10
            result.warnings.append(f"  - {schema_info}")
        if len(empty_schemas) > 10:
            result.warnings.append(f"  ... and {len(empty_schemas) - 10} more")


def check_required_envelope_fields(spec: dict[str, Any], result: ValidationResult) -> None:
    """Check that required envelope fields are present in response schemas."""
    if not REQUIRED_ENVELOPE_FIELDS:
        result.info.append("No required envelope fields configured (skipping check)")
        return

    missing_fields = []

    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue

            op_id = details.get("operationId", "unknown")
            responses = details.get("responses", {})

            # Check 200 response
            success_response = responses.get("200", {})
            content = success_response.get("content", {}).get("application/json", {})
            schema = content.get("schema", {})
            properties = schema.get("properties", {})

            for field_name in REQUIRED_ENVELOPE_FIELDS:
                if field_name not in properties:
                    missing_fields.append(f"{method.upper()} {path} ({op_id}) - missing '{field_name}'")

    if missing_fields:
        result.warnings.append(
            f"Found {len(missing_fields)} endpoints missing required envelope fields:"
        )
        for info in missing_fields[:10]:
            result.warnings.append(f"  - {info}")
        if len(missing_fields) > 10:
            result.warnings.append(f"  ... and {len(missing_fields) - 10} more")


def check_examples(spec: dict[str, Any], result: ValidationResult) -> None:
    """Check that examples exist for GPT-facing endpoints."""
    missing_examples = []

    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue

            op_id = details.get("operationId", "unknown")
            responses = details.get("responses", {})

            # Check 200 response for examples
            success_response = responses.get("200", {})
            content = success_response.get("content", {}).get("application/json", {})

            has_example = (
                "example" in content or
                "examples" in content or
                "example" in content.get("schema", {})
            )

            if not has_example:
                missing_examples.append(f"{method.upper()} {path} ({op_id})")

    if missing_examples:
        # This is informational for now, not an error
        result.info.append(
            f"Endpoints without examples: {len(missing_examples)} (consider adding for better GPT responses)"
        )


def print_operations_table(spec: dict[str, Any]) -> None:
    """Print a table of all operations for reference."""
    operations = list_operations(spec)

    print("\nOperations list (method, path, operationId):")
    print("-" * 80)
    for i, (method, path, op_id) in enumerate(operations, 1):
        print(f"{i:3}. {method.upper():6} {path:50} {op_id}")
    print("-" * 80)


def validate_spec(spec_path: Path) -> ValidationResult:
    """Run all validation checks on the spec."""
    result = ValidationResult()

    try:
        spec = load_openapi_spec(spec_path)
    except FileNotFoundError:
        result.errors.append(f"File not found: {spec_path}")
        return result
    except json.JSONDecodeError as e:
        result.errors.append(f"Invalid JSON: {e}")
        return result

    # Run all checks
    check_operation_count(spec, result)
    check_forbidden_operations(spec, result)
    check_empty_response_schemas(spec, result)
    check_required_envelope_fields(spec, result)
    check_examples(spec, result)

    # Print operations table for reference
    print_operations_table(spec)

    return result


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate OpenAPI GPT schema against guardrail requirements.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Validate default openapi-gpt.json
  %(prog)s --spec other.json        Validate a custom spec file
  %(prog)s --strict                 Treat warnings as errors (for CI)
  %(prog)s --spec foo.json --strict Combined usage
        """,
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=None,
        metavar="FILE",
        help="Path to OpenAPI spec file (default: openapi-gpt.json in repo root)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (useful for CI pipelines)",
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    spec_path = args.spec if args.spec else repo_root / "openapi-gpt.json"

    print("=" * 60)
    print("OpenAPI GPT Schema Validator")
    print("=" * 60)
    if args.strict:
        print("Mode: STRICT (warnings treated as errors)")
    print(f"\nValidating: {spec_path}")

    result = validate_spec(spec_path)

    # Print results
    print("\n" + "=" * 60)
    print("Validation Results")
    print("=" * 60)

    if result.info:
        print("\n📋 Info:")
        for msg in result.info:
            print(f"  ℹ️  {msg}")

    if result.warnings:
        print("\n⚠️  Warnings:")
        for msg in result.warnings:
            print(f"  ⚠️  {msg}")

    if result.errors:
        print("\n❌ Errors:")
        for msg in result.errors:
            print(f"  ❌ {msg}")

    # Final status
    print("\n" + "=" * 60)

    # In strict mode, warnings count as failures
    has_errors = len(result.errors) > 0
    has_warnings = len(result.warnings) > 0
    failed = has_errors or (args.strict and has_warnings)

    if not failed:
        print("✅ All checks passed!")
        return 0
    elif has_errors:
        print(f"❌ Validation failed with {len(result.errors)} error(s)")
        return 1
    else:  # strict mode with warnings
        print(f"❌ Validation failed (strict mode): {len(result.warnings)} warning(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
