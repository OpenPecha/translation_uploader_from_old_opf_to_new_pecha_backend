'''
PAYLOAD EXAMPLE FOR TRANSLATION POST ENDPOINT
{
  "language": "en",
  "content": "AI generated translation...",
  "title": "AI Translation",
  "translator": {
    "ai": {
      "model": "GPT-4",
      "workflow": "translation",
      "prompt_id": "translate-v1"
    }
  },
  "annotation": {
    "id": "ai-annotation-001",
    "type": "alignment",
    "aligned_to": "source-annotation-id"
  }
}
'''
from pydantic import BaseModel
from enum import Enum
from typing import Dict, List

class TextType(Enum):
    TRANSLATION = "translation"
    COMMENTARY = "commentary"

class Annotation(BaseModel):
    Span: Dict[str, int]
    index: int
    alignment_index: List[str]

class AiDetails(BaseModel):
    ai: str

class AnnotationType(Enum):
    ALIGNMENT = "alignment"
    SEGMENTATION = "segmentation"

class Translator(BaseModel):
    ai: AiDetails

class TranslationPayload(BaseModel):
    language: str
    content: str
    title: str
    alt_title: Dict[str, str] | None = None
    translator: Translator
    original_annotation: List[Annotation]
    translation_annotation: List[Annotation]
