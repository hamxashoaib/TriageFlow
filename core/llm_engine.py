import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from core.schemas import TriageResult
from core.guardrails import check_immediate_red_flags

SYSTEM_PROMPT = """You are an expert emergency triage AI assistant deployed in an emergency department or clinic.
Your objective is to evaluate patient symptom descriptions accurately and assign an appropriate clinical urgency tier.

Triage Urgency Tiers:
- **Emergency**: Life-threatening situations (e.g., suspected stroke, cardiac chest pain, respiratory arrest/choking, major uncontrolled bleeding). Requires immediate attention.
- **Urgent**: Serious, potentially deteriorating conditions (e.g., high persistent fever, severe dehydration, unrelenting abdominal pain, persistent vomiting). Needs evaluation within 30-60 minutes.
- **Routine**: Stable, non-urgent minor illnesses or inquiries (e.g., mild cold, minor cough, slight scratch, routine medication questions). Suitable for OPD waiting queue.

Languages to support: English, Urdu, and Roman Urdu.

Rules:
1. Detect the patient's language accurately.
2. Extract primary clinical symptoms clearly.
3. Provide a crisp 1-2 sentence clinical summary for the triage nurse.
4. Provide safe, concise patient next-step guidance.
"""

USER_PROMPT_TEMPLATE = """Patient description:
{patient_input}

Evaluate the severity and return the structured triage assessment."""

def evaluate_patient(patient_input: str, api_key: str | None = None) -> TriageResult:
    """
    Evaluates patient symptoms.
    First runs through deterministic safety guardrails.
    If no hard red flag triggers, it delegates to Google Gemini with structured output.
    """
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("Google API Key not found. Please provide one or set GOOGLE_API_KEY.")

    # Guardrail check
    is_hard_emergency = check_immediate_red_flags(patient_input)

    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        google_api_key=key,
        temperature=0.1
    )

    structured_llm = llm.with_structured_output(TriageResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT_TEMPLATE)
    ])

    chain = prompt | structured_llm
    result: TriageResult = chain.invoke({"patient_input": patient_input})

    # If the deterministic guardrail caught an emergency but LLM under-triaged, enforce Emergency
    if is_hard_emergency and result.urgency_level != "Emergency":
        result.urgency_level = "Emergency"
        result.recommended_action = "IMMEDIATE TRIAGE RED-FLAG: Direct patient to the resuscitation bay or emergency room immediately."

    return result