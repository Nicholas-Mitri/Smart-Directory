import json
from pathlib import Path
import jsonschema
import argparse


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
        # Create full path by joining base path with current name
        current_path = base_path / name

        if node["type"] == "directory":
            # Create directory and recursively process contents
            current_path.mkdir(exist_ok=True)
            if "contents" in node:
                create_structure(current_path, node["contents"])

        elif node["type"] == "file":
            # Create parent directories if they don't exist
            current_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file content, defaulting to empty string if not specified
            content = node.get("content", "")
            current_path.write_text(content)


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Create project structure from schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --schema flask                  # Create Flask project in parent directory
    python main.py --schema django --output-path . # Create Django project in current directory

Available schemas:
    flask  - Basic Flask web application with authentication
    django - Basic Django web application structure
        """,
    )
    parser.add_argument(
        "--schema",
        default="flask",
        type=str,
        help="Schema to use for project structure (default: flask)",
    )
    parser.add_argument(
        "--output-path",
        default=Path.cwd().parent,
        type=str,
        help="Base path for creating the project structure (default: parent directory)",
    )
    args = parser.parse_args()

    # Load the schema
    schema_path = Path("schemas") / f"{args.schema}.json".lower()
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
        base_path = Path(args.output_path)
        create_structure(base_path, schema)

        print("Project structure created successfully!")
    except Exception as e:
        print(f"Error creating project structure: {e}")


if __name__ == "__main__":
    main()
