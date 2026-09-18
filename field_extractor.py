import re


def extract_land_fields(text):

    fields = {}

    # Normalize text
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Field names used in the LANDTRUST demo document
    field_names = {
        "District": "district",
        "Tehsil": "tehsil",
        "Village": "village",
        "Khata Number": "khata_number",
        "Survey Number": "survey_number",
        "Land Owner": "land_owner",
        "Land Area": "land_area",
        "Land Classification": "land_classification"
    }

    # Extract value appearing on the line immediately
    # after each field name
    for i, line in enumerate(lines):

        for label, field_key in field_names.items():

            if line.lower() == label.lower():

                if i + 1 < len(lines):

                    value = lines[i + 1].strip()

                    # Ignore the table header "Value"
                    if value.lower() != "value":

                        fields[field_key] = value

    # Make sure every expected field exists
    for field_key in field_names.values():

        if field_key not in fields:

            fields[field_key] = "Not found"

    return fields