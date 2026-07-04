from enum import Enum
from pydantic import BaseModel
from typing import List

class NormalizationCategory(str, Enum):
    APPLICATION = "application"
    BRAND = "brand"
    TECHNICAL_TERM = "technical_term"
    OS_COMMAND = "os_command"
    ALIAS = "alias"
    USER_DEFINED = "user_defined"
    WHITESPACE = "whitespace"

class NormalizationChange(BaseModel):
    category: NormalizationCategory
    original: str
    normalized: str

class NormalizationResult(BaseModel):
    original_text: str
    normalized_text: str
    confidence: float
    changes: List[NormalizationChange] = []
