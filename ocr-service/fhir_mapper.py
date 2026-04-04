from fhir.resources.patient import Patient
from fhir.resources.identifier import Identifier
from fhir.resources.humanname import HumanName
import datetime

def create_fhir_patient(raw_data: dict):
    patient = Patient()
    
    # 1. Map Name (Splitting "John Doe" into Given/Family)
    name_parts = raw_data.get("name", "Unknown").split(" ")
    hn = HumanName()
    hn.family = name_parts[-1]
    hn.given = name_parts[:-1]
    patient.name = [hn]

    # 2. Map DOB (Ensuring FHIR format YYYY-MM-DD)
    # If your OCR gives '01/20/1980', we must convert it
    try:
        dob_raw = raw_data.get("dob", "")
        # Basic conversion logic - adjust based on John Snow Labs format
        dob_date = datetime.datetime.strptime(dob_raw, "%d/%m/%Y").date()
        patient.birthDate = dob_date.isoformat()
    except Exception:
        print("⚠️ Warning: Could not format DOB correctly")

    # 3. Map Gender (Must be lowercase per FHIR spec)
    gender = raw_data.get("gender", "unknown").lower()
    if gender in ["male", "female", "other", "unknown"]:
        patient.gender = gender

    # 4. Map SSN as an Identifier
    ssn_val = raw_data.get("ssn")
    if ssn_val:
        ident = Identifier()
        ident.system = "http://hl7.org/fhir/sid/us-ssn"
        ident.value = ssn_val
        patient.identifier = [ident]

    return patient.json(indent=2)
