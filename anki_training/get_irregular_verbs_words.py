import random
import re

from bs4 import BeautifulSoup
from rich import print as rprint

from .anki_utils import get_notes_from_deck
from .datatypes import AuxiliaryVerb, IrregularVerbCard, VerbCard, WordInfo

DECK_NAME = "Deutsch::07 Irregular Verbs"

VERBOSE_FIELD_NAME = {
    "simple_past": "past",
    "past_participle": "perfect",
    "present": "present",
}


def get_irregular_verbs_cards(words: list[WordInfo]) -> list[IrregularVerbCard]:
    word_cards = []

    for word in words:
        for field, verbose_name in VERBOSE_FIELD_NAME.items():
            word_cards.append(
                IrregularVerbCard(
                    translation=word.translation,
                    word=getattr(word, field),
                    time=verbose_name,
                )
            )
    random.shuffle(word_cards)
    return word_cards


def get_irregular_verbs_from_collection() -> list[WordInfo]:
    notes = get_notes_from_deck(DECK_NAME)

    words = []
    for note in notes:
        try:
            words.append(parse_note_back_field(note["Back"]))
        except Exception:
            rprint(note["Back"])
            raise

    return words


def parse_note_back_field(html_content) -> WordInfo:
    soup = BeautifulSoup(html_content, "html.parser")
    word_info = WordInfo()

    translation_tag = soup.find("font", color="#c12d30")
    word_info.translation = translation_tag.get_text().strip()

    simple_past_span = soup.find("span", string=re.compile(r"Simple past"))
    simple_past_value_span = simple_past_span.find_next("span")
    word_info.simple_past = simple_past_value_span.get_text().strip()

    past_participle_span = soup.find("span", string=re.compile(r"Past participle"))
    past_participle_value_span = past_participle_span.find_next("span")
    word_info.past_participle = past_participle_value_span.get_text().strip()

    present_span = soup.find("span", string=re.compile("er/sie/es"))
    present_value_span = present_span.find_next("span")
    if present_value_span is None:
        present_value_span = present_span.find_next("b")
    word_info.present = present_value_span.get_text().strip()

    return word_info


def get_verb_cards_from_words(
    words: list[WordInfo], auxiliary_verb: AuxiliaryVerb
) -> list[VerbCard]:
    cards = []
    for word in words:
        cards.append(
            VerbCard(
                word=word,
                auxiliary_verb=auxiliary_verb,
            )
        )
    return cards
