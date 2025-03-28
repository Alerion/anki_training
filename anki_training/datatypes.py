from dataclasses import dataclass
from enum import Enum


class AuxiliaryVerb(str, Enum):
    sein = "sein"
    haben = "haben"


@dataclass
class WordInfo:
    translation: str = ""
    simple_past: str = ""
    past_participle: str = ""
    present: str = ""


@dataclass
class IrregularVerbCard:
    translation: str
    word: str
    time: str


@dataclass
class VerbCard:
    word: WordInfo
    auxiliary_verb: AuxiliaryVerb
