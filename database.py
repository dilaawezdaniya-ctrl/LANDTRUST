import os
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_connection():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


# ------------------------------------------------
# SAVE LAND RECORD
# ------------------------------------------------

def save_land_record(
    fields,
    verified_land_area,
    verification_status,
    verifier_name
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO land_records (
            district,
            tehsil,
            village,
            khata_number,
            survey_number,
            land_owner,
            extracted_land_area,
            verified_land_area,
            land_classification,
            verification_status,
            verifier_name,
            verified_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
    """

    values = (
        fields.get("district"),
        fields.get("tehsil"),
        fields.get("village"),
        fields.get("khata_number"),
        fields.get("survey_number"),
        fields.get("land_owner"),
        fields.get("land_area"),
        verified_land_area,
        fields.get("land_classification"),
        verification_status,
        verifier_name,
        datetime.now()
    )

    cursor.execute(query, values)

    record_id = cursor.lastrowid

    connection.commit()

    cursor.close()
    connection.close()

    return record_id


# ------------------------------------------------
# SAVE AUDIT HISTORY
# ------------------------------------------------

def save_audit_history(
    record_id,
    field_name,
    old_value,
    new_value,
    action,
    verifier_name
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO audit_history (
            record_id,
            field_name,
            old_value,
            new_value,
            action,
            verifier_name
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        record_id,
        field_name,
        old_value,
        new_value,
        action,
        verifier_name
    )

    cursor.execute(query, values)

    connection.commit()

    cursor.close()
    connection.close()


# ------------------------------------------------
# GET ALL LAND RECORDS
# ------------------------------------------------

def get_all_land_records():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            record_id,
            district,
            tehsil,
            village,
            khata_number,
            survey_number,
            land_owner,
            verified_land_area,
            verification_status,
            verified_at
        FROM land_records
        ORDER BY record_id DESC
    """

    cursor.execute(query)

    records = cursor.fetchall()

    cursor.close()
    connection.close()

    return records


# ------------------------------------------------
# GET AUDIT HISTORY
# ------------------------------------------------

def get_audit_history(record_id):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            audit_id,
            record_id,
            field_name,
            old_value,
            new_value,
            action,
            verifier_name,
            action_timestamp
        FROM audit_history
        WHERE record_id = %s
        ORDER BY audit_id DESC
    """

    cursor.execute(query, (record_id,))

    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return history


# ------------------------------------------------
# DASHBOARD STATISTICS
# ------------------------------------------------

def get_dashboard_stats():

    connection = get_connection()
    cursor = connection.cursor()

    # Total documents processed
    cursor.execute("""
        SELECT COUNT(*)
        FROM land_records
    """)

    documents_processed = cursor.fetchone()[0]

    # Verified records
    cursor.execute("""
        SELECT COUNT(*)
        FROM land_records
        WHERE verification_status IN
        ('Approved', 'Corrected & Verified')
    """)

    verified_records = cursor.fetchone()[0]

    # Currently pending records
    cursor.execute("""
        SELECT COUNT(*)
        FROM land_records
        WHERE verification_status = 'Pending'
    """)

    pending_verification = cursor.fetchone()[0]

    # Historical corrections
    cursor.execute("""
        SELECT COUNT(*)
        FROM audit_history
        WHERE action = 'Corrected'
    """)

    corrections_tracked = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return {
        "documents_processed": documents_processed,
        "verified_records": verified_records,
        "pending_verification": pending_verification,
        "corrections_tracked": corrections_tracked
    }