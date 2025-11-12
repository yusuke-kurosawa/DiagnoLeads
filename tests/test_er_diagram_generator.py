"""
Test suite for ER Diagram Generator

テスト内容:
- Markdown パーサー機能
- エンティティ抽出
- リレーション抽出
- 複数フォーマット出力
"""

import json
import tempfile
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from generate_er_diagram import ERDiagramParser, ERDiagramGenerator


def test_parse_entities():
    """Test entity parsing from DiagnoLeads spec"""
    spec_file = Path(__file__).parent.parent / 'openspec/specs/database/diagnoleads-data-model.md'
    
    parser = ERDiagramParser(str(spec_file))
    
    # Check entities found
    assert len(parser.entities) > 0, "No entities found"
    assert 'Tenant' in parser.entities, "Tenant entity not found"
    assert 'User' in parser.entities, "User entity not found"
    assert 'Assessment' in parser.entities, "Assessment entity not found"
    
    print(f"✅ Found {len(parser.entities)} entities")
    print(f"✅ Entities: {', '.join(parser.entities.keys())}")


def test_parse_relationships():
    """Test relationship parsing"""
    spec_file = Path(__file__).parent.parent / 'openspec/specs/database/diagnoleads-data-model.md'
    
    parser = ERDiagramParser(str(spec_file))
    
    # Check relationships found
    assert len(parser.relationships) > 0, "No relationships found"
    
    # Check specific relationships
    rel_map = {f"{r.from_entity}::{r.to_entity}": r for r in parser.relationships}
    
    assert "Tenant::User" in rel_map, "Tenant::User relationship not found"
    assert "Tenant::Assessment" in rel_map, "Tenant::Assessment relationship not found"
    assert rel_map["Tenant::User"].cardinality == "1:N", "Incorrect cardinality"
    
    print(f"✅ Found {len(parser.relationships)} relationships")
    print(f"✅ Sample: Tenant::User = {rel_map['Tenant::User'].cardinality}")


def test_entity_structure():
    """Test entity structure parsing"""
    spec_file = Path(__file__).parent.parent / 'openspec/specs/database/diagnoleads-data-model.md'
    
    parser = ERDiagramParser(str(spec_file))
    tenant = parser.entities['Tenant']
    
    # Check entity fields
    assert tenant.name == "Tenant"
    assert tenant.table == "tenants"
    assert len(tenant.fields) > 0, "No fields found in Tenant"
    
    # Check field properties
    field_names = [f.name for f in tenant.fields]
    assert 'id' in field_names, "id field not found"
    assert 'name' in field_names, "name field not found"
    
    # Check primary key
    id_field = next(f for f in tenant.fields if f.name == 'id')
    assert 'PK' in id_field.constraints, "Primary key constraint missing"
    
    print(f"✅ Tenant entity has {len(tenant.fields)} fields")
    print(f"✅ Fields: {', '.join(field_names[:5])}...")


def test_mermaid_output():
    """Test Mermaid ER diagram generation"""
    spec_file = Path(__file__).parent.parent / 'openspec/specs/database/diagnoleads-data-model.md'
    
    parser = ERDiagramParser(str(spec_file))
    generator = ERDiagramGenerator(parser)
    
    mermaid = generator.to_mermaid()
    
    # Check format
    assert mermaid.startswith("erDiagram"), "Mermaid diagram should start with erDiagram"
    assert "Tenant" in mermaid, "Tenant entity not in Mermaid output"
    assert "||--o{" in mermaid, "Cardinality notation not in output"
    
    print(f"✅ Mermaid output generated ({len(mermaid)} bytes)")


def test_plantuml_output():
    """Test PlantUML ER diagram generation"""
    spec_file = Path(__file__).parent.parent / 'openspec/specs/database/diagnoleads-data-model.md'
    
    parser = ERDiagramParser(str(spec_file))
    generator = ERDiagramGenerator(parser)
    
    plantuml = generator.to_plantuml()
    
    # Check format
    assert plantuml.startswith("@startuml"), "PlantUML should start with @startuml"
    assert "@enduml" in plantuml, "PlantUML should end with @enduml"
    assert "entity Tenant" in plantuml, "Tenant entity not in PlantUML output"
    
    print(f"✅ PlantUML output generated ({len(plantuml)} bytes)")


def test_json_output():
    """Test JSON output generation"""
    spec_file = Path(__file__).parent.parent / 'openspec/specs/database/diagnoleads-data-model.md'
    
    parser = ERDiagramParser(str(spec_file))
    generator = ERDiagramGenerator(parser)
    
    json_str = generator.to_json()
    
    # Parse JSON
    data = json.loads(json_str)
    
    # Check structure
    assert 'entities' in data, "entities key not in JSON"
    assert 'relationships' in data, "relationships key not in JSON"
    assert len(data['entities']) > 0, "No entities in JSON"
    assert len(data['relationships']) > 0, "No relationships in JSON"
    
    # Check entity structure
    tenant_entity = next((e for e in data['entities'] if e['name'] == 'Tenant'), None)
    assert tenant_entity is not None, "Tenant entity not in JSON"
    assert 'fields' in tenant_entity, "fields key not in entity"
    assert len(tenant_entity['fields']) > 0, "No fields in Tenant"
    
    # Check field structure
    id_field = next((f for f in tenant_entity['fields'] if f['name'] == 'id'), None)
    assert id_field is not None, "id field not found"
    assert 'constraints' in id_field, "constraints key not in field"
    
    print(f"✅ JSON output valid with {len(data['entities'])} entities")


def test_relationship_cardinality():
    """Test relationship cardinality parsing"""
    spec_file = Path(__file__).parent.parent / 'openspec/specs/database/diagnoleads-data-model.md'
    
    parser = ERDiagramParser(str(spec_file))
    
    # Check cardinalities
    cardinalities = set()
    for rel in parser.relationships:
        cardinalities.add(rel.cardinality)
        # Validate cardinality format
        assert rel.cardinality in ['1:N', 'N:N', '1:1'], f"Invalid cardinality: {rel.cardinality}"
    
    print(f"✅ Found cardinalities: {', '.join(sorted(cardinalities))}")


def test_cascade_delete():
    """Test ON DELETE behavior"""
    spec_file = Path(__file__).parent.parent / 'openspec/specs/database/diagnoleads-data-model.md'
    
    parser = ERDiagramParser(str(spec_file))
    
    # Check ON DELETE behaviors
    behaviors = set()
    for rel in parser.relationships:
        behaviors.add(rel.on_delete)
    
    print(f"✅ Found ON DELETE behaviors: {', '.join(sorted(behaviors))}")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_parse_entities,
        test_parse_relationships,
        test_entity_structure,
        test_mermaid_output,
        test_plantuml_output,
        test_json_output,
        test_relationship_cardinality,
        test_cascade_delete,
    ]
    
    print("=" * 60)
    print("ER DIAGRAM GENERATOR TEST SUITE")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            print(f"Running: {test_func.__name__}")
            test_func()
            passed += 1
            print()
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            print()
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            print()
            failed += 1
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
