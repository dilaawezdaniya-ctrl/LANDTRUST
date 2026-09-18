from flask import Flask, render_template, request

from pdf_reader import extract_text_from_pdf
from field_extractor import extract_land_fields
from validator import validate_record

from database import (
    save_land_record,
    save_audit_history,
    get_all_land_records,
    get_audit_history,
    get_dashboard_stats
)


app = Flask(__name__)


# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------

@app.route("/")
def dashboard():
    stats = get_dashboard_stats()

    return render_template(
        "dashboard.html",
        stats=stats
    )


# ------------------------------------------------
# TRUSTED RECORDS
# ------------------------------------------------

@app.route("/records")
def records():
    all_records = get_all_land_records()

    return render_template(
        "records.html",
        records=all_records
    )


# ------------------------------------------------
# AUDIT HISTORY
# ------------------------------------------------

@app.route("/audit/<int:record_id>")
def audit(record_id):
    history = get_audit_history(record_id)

    return render_template(
        "audit.html",
        history=history,
        record_id=record_id
    )


# ------------------------------------------------
# UPLOAD LAND RECORD
# ------------------------------------------------

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        file = request.files.get("land_record")

        if not file:
            return "No file selected."

        file_path = "uploaded_land_record.pdf"

        file.save(file_path)

        extracted_text = extract_text_from_pdf(file_path)

        fields = extract_land_fields(extracted_text)

        validation_results = validate_record(fields)

        has_conflict = any(
            result["status"] == "Conflict"
            for result in validation_results.values()
        )

        if has_conflict:

            return render_template(
                "verification.html",
                validation_results=validation_results,
                raw_text=extracted_text
            )

        return render_template(
            "extraction.html",
            fields=fields,
            raw_text=extracted_text,
            validation_results=validation_results
        )

    return render_template("upload.html")


# ------------------------------------------------
# HUMAN VERIFICATION
# ------------------------------------------------

@app.route("/verify", methods=["POST"])
def verify():

    action = request.form.get("action")

    corrected_land_area = request.form.get(
        "corrected_land_area"
    )

    verifier_name = "Authorized Verifier"


    # ------------------------------------------------
    # APPROVE RECORD
    # ------------------------------------------------

    if action == "approve":

        extracted_land_area = corrected_land_area

        fields = {
            "district": "Pune",
            "tehsil": "Mulshi",
            "village": "Example Village",
            "khata_number": "452",
            "survey_number": "127/2",
            "land_owner": "Ramesh Kumar",
            "land_area": extracted_land_area,
            "land_classification": "Agricultural"
        }

        record_id = save_land_record(
            fields,
            extracted_land_area,
            "Approved",
            verifier_name
        )

        save_audit_history(
            record_id,
            "land_area",
            extracted_land_area,
            extracted_land_area,
            "Approved",
            verifier_name
        )

        return render_template(
            "verification_success.html",
            record_id=record_id,
            status="Approved",
            corrected_land_area=extracted_land_area
        )


    # ------------------------------------------------
    # CORRECT AND VERIFY
    # ------------------------------------------------

    elif action == "correct":

        original_value = "3.21 Hectare"

        if not corrected_land_area:

            return "Please enter a corrected land area."

        fields = {
            "district": "Pune",
            "tehsil": "Mulshi",
            "village": "Example Village",
            "khata_number": "452",
            "survey_number": "127/2",
            "land_owner": "Ramesh Kumar",
            "land_area": original_value,
            "land_classification": "Agricultural"
        }

        record_id = save_land_record(
            fields,
            corrected_land_area,
            "Corrected & Verified",
            verifier_name
        )

        save_audit_history(
            record_id,
            "land_area",
            original_value,
            corrected_land_area,
            "Corrected",
            verifier_name
        )

        return render_template(
            "verification_success.html",
            record_id=record_id,
            status="Corrected & Verified",
            corrected_land_area=corrected_land_area
        )


    return "Invalid verification request."


# ------------------------------------------------
# RUN APPLICATION
# ------------------------------------------------

if __name__ == "__main__":
    app.run()