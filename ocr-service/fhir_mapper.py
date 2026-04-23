from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import Optional, List
from pydantic_ai.exceptions import UnexpectedModelBehavior

# 1. Define the Agent
# We use 'Patient' directly as the result_type
class SimplifiedPatient(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # String instead of 'date' to avoid format errors
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    redacted_fields: List[str] = Field(default_factory=list) # To track what's missing

# Update your Agent
medical_mapper = Agent(
    'google-gla:gemini-2.5-flash',
    output_type=SimplifiedPatient, # Swap to the simpler model
    system_prompt=(
        "Extract basic patient info from the OCR text. "
        "If a field is redacted (e.g., [REDACTED]), add the field name to the 'redacted_fields' list."
    )
)

async def extract_to_fhir(ocr_markdown: str):
    # The agent uses the fhir.resources schema to 'force' the LLM into compliance
    result = None

    try:
        result = await medical_mapper.run(ocr_markdown)
        # result.data is now a full fhir.resources.patient.Patient object
        return result.output.model_dump_json(indent=2)
    except UnexpectedModelBehavior as e:
        # This will show you exactly which FHIR field failed validation
        print(f"❌ Mapping Failed for this PDF: {e}")
        return {"error": "Validation failed", "details": str(e)}
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return {"error": "System error", "message": str(e)}
    
    
