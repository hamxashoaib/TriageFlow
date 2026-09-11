import re

# Red-flag emergency keywords across English, Roman Urdu, and Urdu
EMERGENCY_PATTERNS = [
    # Chest / Cardiac
    r"\b(chest\s*pain|heart\s*attack|cardiac|pressure\s*in\s*chest)\b",
    r"\b(seene\s*m(e|ai)n?\s*dard|chhati\s*m(e|ai)n?\s*dard|bazu\s*ki\s*taraf)\b",
    r"سینے\s*میں\s*(شدید\s*)?(درد|دباؤ)",

    # Respiratory / Choking
    r"\b(can'?t\s*breathe|shortness\s*of\s*breath|choking|gasping)\b",
    r"\b(sa+ns\s*n(a|e)h(i|ee)n?\s*a+\s*rah(i|ee)|dum\s*ghut)\b",
    r"سانس\s*نہیں\s*آ\s*رہ(ی|ا)|دم\s*گھٹ",

    # Neurological / Stroke / Fainting
    r"\b(unconscious|fainted|loss\s*of\s*speech|paralysis|stroke)\b",
    r"\b(behosh|bol\s*n(a|e)h(i|ee)n?\s*pa\s*rah|move\s*n(a|e)h(i|ee)n?)\b",
    r"بے\s*ہوش|فالج|بول\s*نہیں",

    # Severe Trauma / Heavy Bleeding
    r"\b(severe\s*bleeding|uncontrolled\s*bleeding|head\s*injury)\b",
    r"\b(khoon\s*ruk\s*n(a|e)h(i|ee)n?\s*rah|bohat\s*zyada\s*khoon)\b",
    r"خون\s*بہہ|خون\s*رک\s*نہیں"
]

def check_immediate_red_flags(text: str) -> bool:
    """
    Returns True if an unambiguous red-flag emergency pattern is detected.
    Deterministic rule-based safety barrier.
    """
    text_lower = text.lower()
    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, text_lower, re.UNICODE):
            return True
    return False