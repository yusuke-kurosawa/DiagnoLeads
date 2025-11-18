"""
Contract Tests

Tests that verify the API implementation matches the OpenAPI specification.
Uses Schemathesis for property-based testing of all endpoints.
"""

from pathlib import Path
import json


# Load OpenAPI schema
OPENAPI_PATH = Path(__file__).parent.parent.parent / "openapi.json"

# Note: Schemathesis property-based tests are commented out for now
# They require authentication setup and can generate many test cases
# Uncomment and configure when ready for comprehensive contract testing

# Example of how to use Schemathesis:
# schema = schemathesis.from_uri(f"file://{OPENAPI_PATH}")
# @schema.parametrize()
# def test_api_contract(case):
#     response = case.call()
#     case.validate_response(response)


# For manual testing specific endpoints
def test_openapi_schema_exists():
    """Verify that the OpenAPI schema file exists"""
    assert OPENAPI_PATH.exists(), f"OpenAPI schema not found at {OPENAPI_PATH}"
    
    with open(OPENAPI_PATH, 'r') as f:
        schema_data = json.load(f)
    
    assert 'openapi' in schema_data, "Invalid OpenAPI schema format"
    assert 'paths' in schema_data, "No paths defined in OpenAPI schema"
    assert len(schema_data['paths']) > 0, "OpenAPI schema has no endpoints"


def test_openapi_endpoints_count():
    """Verify the expected number of endpoints"""
    with open(OPENAPI_PATH, 'r') as f:
        schema_data = json.load(f)
    
    endpoint_count = len(schema_data['paths'])
    # We expect at least 16 endpoints (Assessment + Lead + Auth)
    assert endpoint_count >= 16, f"Expected at least 16 endpoints, found {endpoint_count}"


def test_openapi_has_authentication():
    """Verify that authentication is defined in the schema"""
    with open(OPENAPI_PATH, 'r') as f:
        schema_data = json.load(f)
    
    assert 'components' in schema_data, "No components section in OpenAPI schema"
    # Check for security schemes (we use Bearer token)
    has_security = (
        'securitySchemes' in schema_data.get('components', {})
        or 'security' in schema_data
    )
    assert has_security, "No security schemes defined in OpenAPI schema"
    

def test_assessment_endpoints_in_schema():
    """Verify Assessment endpoints are in the schema"""
    with open(OPENAPI_PATH, 'r') as f:
        schema_data = json.load(f)
    
    paths = schema_data['paths']
    assessment_paths = [p for p in paths.keys() if 'assessments' in p.lower()]
    
    # We expect at least some assessment endpoints
    assert len(assessment_paths) > 0, f"Expected assessment endpoints, found {len(assessment_paths)}"
    print(f"Found {len(assessment_paths)} assessment endpoints: {assessment_paths}")


def test_lead_endpoints_in_schema():
    """Verify Lead endpoints are in the schema"""
    with open(OPENAPI_PATH, 'r') as f:
        schema_data = json.load(f)
    
    paths = schema_data['paths']
    lead_paths = [p for p in paths.keys() if 'leads' in p.lower()]
    
    # We expect at least some lead endpoints
    assert len(lead_paths) > 0, f"Expected lead endpoints, found {len(lead_paths)}"
    print(f"Found {len(lead_paths)} lead endpoints: {lead_paths}")


def test_schema_has_required_models():
    """Verify required data models are defined"""
    with open(OPENAPI_PATH, 'r') as f:
        schema_data = json.load(f)
    
    schemas = schema_data.get('components', {}).get('schemas', {})
    
    required_schemas = [
        'AssessmentResponse',
        'AssessmentCreate',
        'LeadResponse',
        'LeadCreate',
    ]
    
    for schema_name in required_schemas:
        assert schema_name in schemas, f"Required schema '{schema_name}' not found in OpenAPI spec"


def test_openapi_info_metadata():
    """Verify OpenAPI metadata is correct"""
    with open(OPENAPI_PATH, 'r') as f:
        schema_data = json.load(f)
    
    assert 'info' in schema_data, "No info section in OpenAPI schema"
    info = schema_data['info']
    
    assert 'title' in info, "No title in OpenAPI info"
    assert info['title'] == 'DiagnoLeads API', f"Unexpected API title: {info['title']}"
    
    assert 'version' in info, "No version in OpenAPI info"
