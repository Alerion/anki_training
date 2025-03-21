from dataclasses import dataclass


@dataclass
class WordInfo:
    translation: str = ""
    simple_past: str = ""
    past_participle: str = ""
    present: str = ""
