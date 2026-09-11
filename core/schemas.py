from pydantic import BaseModel, Field
from typing import List, Literal

class TriageResult(BaseModel):
    urgency_level: Literal["Emergency", "Urgent", "Routine"] = Field(
        description="Assigned triage priority level based on severity of symptoms."
    )
    detected_language: str = Field(
        description="Language detected: English, Urdu, or Roman Urdu."
    )
    identified_symptoms: List[str] = Field(
        description="List of primary symptoms extracted from the patient description."
    )
    clinical_summary: str = Field(
        description="Concise 1-2 sentence clinical summary for the triage nurse or doctor."
    )
    recommended_action: str = Field(
        description="Immediate guidance for the patient (e.g., immediate ER room, priority queue, standard OPD)."
    )