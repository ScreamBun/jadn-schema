"""
Import namespaced type definitions into a base package.

Search all packages in SCHEMA_DIR for referenced definitions, put resolved base file in OUTPUT_DIR.
"""

import jadn
import os
from .resolve import resolve_imports

def resolve(schema_name: str, schema: dict, schema_list: list) -> list | str:
    print(f'Installed JADN version: {jadn.__version__}\n')
    filename, ext = os.path.splitext(schema_name)
    # get all referenced def
    references = schema['meta']['namespaces'] if 'namespaces' in schema['meta'] else {}
    if len(references) == 0:
        raise ValueError("No references to resolve")
    sc2 = resolve_imports(schema, schema_list, references)        # Resolve referenced definitions
    schema = jadn.dumps(sc2)   # Save resolved base package
    return [{'schema_name': filename + '-resolved', "schema_fmt": 'jadn', 'schema': schema }]
    #return schema
    
# resolve_references.py

def resolve_references(base_schema, reference_schemas):
    """
    Resolves references in the base schema using the provided reference schemas.

    Args:
        base_schema (dict): The schema to be resolved.
        reference_schemas (list): A list of schemas that the base schema can reference.

    Returns:
        dict: The resolved schema.
    """
    # Map nsid URLs to their corresponding reference schemas
    nsid_to_schema = {
        schema["meta"]["package"]: schema
        for schema in reference_schemas
    }

    # Extract namespaces from the base schema
    namespaces = base_schema.get("meta", {}).get("namespaces", {})

    # Collect all types from the base schema
    resolved_types = {t[0]: t for t in base_schema.get("types", [])}

    # Iterate through the types in the base schema
    for type_def in base_schema.get("types", []):
        for field in type_def[4]:  # Fields are in the 5th position of the type definition
            field_type = field[2]
            if ":" in field_type:  # Check if the field type uses an nsid
                nsid, type_name = field_type.split(":")
                if nsid in namespaces:
                    ref_schema_url = namespaces[nsid]
                    ref_schema = nsid_to_schema.get(ref_schema_url)
                    if ref_schema:
                        # Find the referenced type in the referenced schema
                        for ref_type in ref_schema.get("types", []):
                            if ref_type[0] == type_name and type_name not in resolved_types:
                                resolved_types[type_name] = ref_type
                        # Update the field type to remove the namespace prefix
                        field[2] = type_name

    # Update the base schema with the resolved types
    base_schema["types"] = list(resolved_types.values())
    return base_schema