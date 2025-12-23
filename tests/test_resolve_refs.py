from unittest import TestCase

from jadnschema.transform.resolve_references import resolve_references
# from resolve_references import resolve_references

class TestResolveReferences(TestCase):
    def test_resolve_references(self):
        # Define schema1 with a namespace and types
        schema1 = {
            "meta": {
                "package": "http://example.com/schema1"
            },
            "types": [
                ["Person", "Record", [], "A person record", [
                    [1, "name", "String", [], "The person's name."]
                ]]
            ]
        }

        # Define schema2 that references schema1 using the namespace
        schema2 = {
            "meta": {
                "package": "http://example.com/schema2",
                "namespaces": {
                    "ns1": "http://example.com/schema1"
                }
            },
            "types": [
                ["Employee", "Record", [], "An employee record", [
                    [1, "person", "ns1:Person", [], "Reference to a person."],
                    [2, "employee_id", "Integer", [], "The employee ID."]
                ]]
            ]
        }

        # Resolve schema2 using schema1 as a reference
        resolved_schema = resolve_references(schema2, [schema1])

        # Assert that the resolved schema contains both Person and Employee types
        resolved_type_names = [t[0] for t in resolved_schema["types"]]
        self.assertIn("Person", resolved_type_names)
        self.assertIn("Employee", resolved_type_names)

        # Assert that the Person type is correctly resolved
        person_type = next(t for t in resolved_schema["types"] if t[0] == "Person")
        self.assertEqual(person_type[1], "Record")
        self.assertEqual(person_type[4][0][1], "name")

        # Assert that the Employee type remains unchanged
        employee_type = next(t for t in resolved_schema["types"] if t[0] == "Employee")
        self.assertEqual(employee_type[4][0][2], "Person")  # Reference resolved to Person
        self.assertEqual(employee_type[4][1][1], "employee_id")