import json
import os
from pathlib import Path
import jsonschema


def validate_schema(schema):
    """Validate the schema structure"""
    schema_definition = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["directory", "file"]},
            "contents": {"type": "object"},
            "content": {"type": "string"},
        },
        "required": ["type"],
    }

    def validate_node(node):
        jsonschema.validate(instance=node, schema=schema_definition)
        if node["type"] == "directory" and "contents" in node:
            for child in node["contents"].values():
                validate_node(child)

    for root_item in schema.values():
        validate_node(root_item)


def create_structure(base_path: Path, structure: dict):
    """Recursively create directories and files based on the schema"""
    for name, node in structure.items():
        current_path = base_path / name

        if node["type"] == "directory":
            current_path.mkdir(exist_ok=True)
            if "contents" in node:
                create_structure(current_path, node["contents"])

        elif node["type"] == "file":
            # Create parent directories if they don't exist
            current_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file content
            content = node.get("content", "")
            current_path.write_text(content)


def main():
    # Load the schema
    schema_path = Path("schemas/django.json")
    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file not found at {schema_path}")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in schema file")
        return

    try:
        # Validate the schema
        validate_schema(schema)
    except jsonschema.ValidationError as e:
        print(f"Schema validation error: {e}")
        return

    # Create the directory structure
    try:
        base_path = Path.cwd()
        create_structure(base_path, schema)
        print("Project structure created successfully!")
    except Exception as e:
        print(f"Error creating project structure: {e}")


if __name__ == "__main__":
    main()
