#!/usr/bin/env python3
"""
Generate OpenAPI specification from FastAPI application

This script generates the OpenAPI specification (openapi.json) from the FastAPI app.
This is the Single Source of Truth for the API contract.

Usage:
    python scripts/generate_openapi.py
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


def generate_openapi():
    """Generate OpenAPI specification and save to file"""
    
    # Get OpenAPI spec from FastAPI
    openapi_spec = app.openapi()
    
    # Output path (project root)
    output_path = Path(__file__).parent.parent.parent / "openapi.json"
    
    # Write to file with pretty formatting
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OpenAPI specification generated: {output_path}")
    print(f"📊 Endpoints: {len(openapi_spec.get('paths', {}))}")
    print(f"📦 Schemas: {len(openapi_spec.get('components', {}).get('schemas', {}))}")
    
    return output_path


def validate_spec(spec):
    """Basic validation of OpenAPI spec"""
    
    errors = []
    
    # Check required fields
    if "openapi" not in spec:
        errors.append("Missing 'openapi' field")
    
    if "info" not in spec:
        errors.append("Missing 'info' field")
    
    if "paths" not in spec:
        errors.append("Missing 'paths' field")
    
    # Check that all paths have operationId
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                if "operationId" not in operation:
                    errors.append(f"Missing operationId for {method.upper()} {path}")
    
    if errors:
        print("⚠️  Validation warnings:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Specification validation passed")
    
    return len(errors) == 0


if __name__ == "__main__":
    try:
        output_path = generate_openapi()
        
        # Validate the generated spec
        with open(output_path, "r", encoding="utf-8") as f:
            spec = json.load(f)
        
        validate_spec(spec)
        
        print("\n🎉 OpenAPI specification generation complete!")
        print("\nNext steps:")
        print("  1. Review the specification: cat openapi.json | jq")
        print("  2. Generate frontend types: cd frontend && npm run generate:types")
        print("  3. Commit the changes: git add openapi.json && git commit")
        
    except Exception as e:
        print(f"❌ Error generating OpenAPI specification: {e}", file=sys.stderr)
        sys.exit(1)
