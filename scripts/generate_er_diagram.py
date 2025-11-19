#!/usr/bin/env python3
"""
OpenSpec ER 図生成ツール

OpenSpec Markdown 形式のデータモデル定義から
複数フォーマットの ER 図を自動生成します。

使用例:
  python scripts/generate_er_diagram.py \
    openspec/specs/database/diagnoleads-data-model.md \
    --format mermaid \
    --output diagrams/er_diagram.md
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Field:
    """Entity field definition"""

    name: str
    type: str
    constraints: List[str]
    description: str


@dataclass
class Entity:
    """Entity definition"""

    name: str
    table: str
    description: str
    fields: List[Field]


@dataclass
class Relationship:
    """Entity relationship"""

    from_entity: str
    to_entity: str
    cardinality: str  # 1:N, N:N, 1:1
    reference: str
    on_delete: str
    description: str


class ERDiagramParser:
    """Parse OpenSpec Markdown ER definition"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = Path(file_path).read_text(encoding="utf-8")
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.parse()

    def parse(self):
        """Parse OpenSpec Markdown format"""
        self._parse_entities()
        self._parse_relationships()

    def _parse_entities(self):
        """Extract entities from markdown"""
        # Find "## Entities" section (may have emoji prefix)
        entities_match = re.search(
            r"##\s+.+?Entities(.*?)(?=\n##\s+|\Z)", self.content, re.DOTALL
        )
        if not entities_match:
            return

        entities_section = entities_match.group(1)

        # Find each ### [Entity Name]
        entity_pattern = r"### (\w+)\n\*\*Table\*\*: `([^`]+)`\s*\n\*\*Description\*\*: ([^\n]+)\n\n\| Field \| Type \| Constraint \| Description \|(.*?)(?=\n### |\n## |\Z)"

        for match in re.finditer(entity_pattern, entities_section, re.DOTALL):
            entity_name = match.group(1)
            table_name = match.group(2)
            description = match.group(3)
            fields_section = match.group(4)

            # Parse fields table
            fields = self._parse_fields_table(fields_section)

            self.entities[entity_name] = Entity(
                name=entity_name,
                table=table_name,
                description=description,
                fields=fields,
            )

    def _parse_fields_table(self, table_text: str) -> List[Field]:
        """Parse field table rows"""
        fields = []
        # Skip header separator line
        lines = table_text.strip().split("\n")

        for line in lines[1:]:  # Skip |---|...| header
            if not line.strip() or line.startswith("|---|"):
                continue

            parts = [
                p.strip() for p in line.split("|")[1:-1]
            ]  # Remove empty first/last
            if len(parts) >= 4:
                name, ftype, constraint, desc = parts[0], parts[1], parts[2], parts[3]
                constraints = [c.strip() for c in constraint.split(",")]
                fields.append(
                    Field(
                        name=name, type=ftype, constraints=constraints, description=desc
                    )
                )

        return fields

    def _parse_relationships(self):
        """Extract relationships from markdown"""
        # Find all relationship sections (### Xxx Relationships)
        rel_sections = re.finditer(
            r"###\s+.+?Relationships\n(.*?)(?=\n###|\n##\s+|\Z)",
            self.content,
            re.DOTALL,
        )

        # Also try to find main ## Relationships section (may have emoji)
        main_rel_match = re.search(
            r"##\s+.+?Relationships(.*?)(?=\n##\s+|\Z)", self.content, re.DOTALL
        )

        all_sections = []
        for section_match in rel_sections:
            all_sections.append(section_match.group(1))

        if main_rel_match:
            all_sections.append(main_rel_match.group(1))

        # Parse each section
        for rel_section in all_sections:
            # Find each - **[EntityA]::[EntityB]** = [cardinality]
            rel_pattern = r"- \*\*(\w+)::(\w+)\*\* = ([\w:N]+)\s*\n\s+- Reference: ([^\n]+)\n\s+- On Delete: ([^\n]+)\n\s+- Description: ([^\n]+)"

            for match in re.finditer(rel_pattern, rel_section):
                from_entity = match.group(1)
                to_entity = match.group(2)
                cardinality = match.group(3)
                reference = match.group(4)
                on_delete = match.group(5)
                description = match.group(6)

                self.relationships.append(
                    Relationship(
                        from_entity=from_entity,
                        to_entity=to_entity,
                        cardinality=cardinality,
                        reference=reference,
                        on_delete=on_delete,
                        description=description,
                    )
                )


class ERDiagramGenerator:
    """Generate ER diagrams in multiple formats"""

    def __init__(self, parser: ERDiagramParser):
        self.entities = parser.entities
        self.relationships = parser.relationships

    def to_mermaid(self) -> str:
        """Generate Mermaid ER diagram"""
        lines = ["erDiagram", ""]

        # Add entities (Mermaid doesn't require explicit entity definitions)
        # Add relationships
        for rel in self.relationships:
            # Cardinality: 1:N → "||--o{"
            # Mermaid: "||" (one) "--" (many) "o" (zero or more)
            if rel.cardinality == "1:N":
                cardinality_str = "||--o{"
            elif rel.cardinality == "N:N":
                cardinality_str = "}o--o{"
            elif rel.cardinality == "1:1":
                cardinality_str = "||--||"
            else:
                cardinality_str = "||--o{"

            line = f"    {rel.from_entity} {cardinality_str} {rel.to_entity} : {rel.description}"
            lines.append(line)

        return "\n".join(lines)

    def to_plantuml(self) -> str:
        """Generate PlantUML ER diagram"""
        lines = ["@startuml", "!define ENTITY_BG #FFF9C4"]

        # Add entities
        for entity_name, entity in self.entities.items():
            lines.append(f"entity {entity_name} {{")

            # Add fields
            for field in entity.fields:
                constraint_str = " ".join(field.constraints)
                if constraint_str:
                    lines.append(f"  * {field.name} : {field.type} [{constraint_str}]")
                else:
                    lines.append(f"  * {field.name} : {field.type}")

            lines.append("}")
            lines.append("")

        # Add relationships
        for rel in self.relationships:
            # Cardinality mapping
            if rel.cardinality == "1:N":
                card_str = "||--o{"
            elif rel.cardinality == "N:N":
                card_str = "}o--o{"
            else:
                card_str = "||--||"

            lines.append(
                f"{rel.from_entity} {card_str} {rel.to_entity} : {rel.description}"
            )

        lines.append("")
        lines.append("@enduml")
        return "\n".join(lines)

    def to_json(self) -> str:
        """Generate JSON metadata"""
        data = {
            "entities": [
                {
                    "name": entity_name,
                    "table": entity.table,
                    "description": entity.description,
                    "fields": [
                        {
                            "name": f.name,
                            "type": f.type,
                            "constraints": f.constraints,
                            "description": f.description,
                        }
                        for f in entity.fields
                    ],
                }
                for entity_name, entity in self.entities.items()
            ],
            "relationships": [
                {
                    "from": rel.from_entity,
                    "to": rel.to_entity,
                    "cardinality": rel.cardinality,
                    "reference": rel.reference,
                    "on_delete": rel.on_delete,
                    "description": rel.description,
                }
                for rel in self.relationships
            ],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate ER diagrams from OpenSpec Markdown"
    )
    parser.add_argument("spec_file", help="Path to OpenSpec data model file")
    parser.add_argument(
        "--format",
        choices=["mermaid", "plantuml", "json", "all"],
        default="mermaid",
        help="Output format (default: mermaid)",
    )
    parser.add_argument("--output", help="Output file path (without extension)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Parse OpenSpec file
    if args.verbose:
        print(f"📖 Parsing: {args.spec_file}")

    er_parser = ERDiagramParser(args.spec_file)

    if args.verbose:
        print(f"✅ Found {len(er_parser.entities)} entities")
        print(f"✅ Found {len(er_parser.relationships)} relationships")

    # Generate diagrams
    generator = ERDiagramGenerator(er_parser)

    output_path = Path(args.output) if args.output else Path("diagrams/er_diagram")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format in ["mermaid", "all"]:
        mermaid_output = generator.to_mermaid()
        mermaid_file = str(output_path.with_suffix(".md"))
        Path(mermaid_file).write_text(mermaid_output, encoding="utf-8")
        if args.verbose:
            print(f"✅ Generated: {mermaid_file}")

    if args.format in ["plantuml", "all"]:
        plantuml_output = generator.to_plantuml()
        plantuml_file = str(output_path.with_suffix(".pu"))
        Path(plantuml_file).write_text(plantuml_output, encoding="utf-8")
        if args.verbose:
            print(f"✅ Generated: {plantuml_file}")

    if args.format in ["json", "all"]:
        json_output = generator.to_json()
        json_file = str(output_path.with_suffix(".json"))
        Path(json_file).write_text(json_output, encoding="utf-8")
        if args.verbose:
            print(f"✅ Generated: {json_file}")

    print("✅ ER diagram generation complete!")


if __name__ == "__main__":
    main()
