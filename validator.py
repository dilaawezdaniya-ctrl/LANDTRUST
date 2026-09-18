def validate_record(fields):

    validation_results = {}

    expected_values = {
        "district": "Pune",
        "tehsil": "Mulshi",
        "village": "Example Village",
        "khata_number": "452",
        "survey_number": "127/2",
        "land_owner": "Ramesh Kumar",
        "land_area": "2.74 Hectare",
        "land_classification": "Agricultural"
    }

    for field, extracted_value in fields.items():

        reference_value = expected_values.get(field)

        if reference_value is None:
            validation_results[field] = {
                "value": extracted_value,
                "reference": None,
                "confidence": 95,
                "status": "Verified"
            }

        elif extracted_value == reference_value:
            validation_results[field] = {
                "value": extracted_value,
                "reference": reference_value,
                "confidence": 95,
                "status": "Verified"
            }

        else:
            validation_results[field] = {
                "value": extracted_value,
                "reference": reference_value,
                "confidence": 60,
                "status": "Conflict"
            }

    return validation_results