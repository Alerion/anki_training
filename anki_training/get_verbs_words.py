import re
from rich import print as rprint
from anki.collection import Collection, Note
from .config import COLLECTION_PATH
from .datatypes import WordInfo
from .anki_utils import get_notes_from_deck
from bs4 import BeautifulSoup

SEIN_VERBS_DECK_NAME = "Deutsch::08 Verbs with sein"
ALL_WORDS_DECK_NAME = "Deutsch::09 German Words"
CLEAN_HTML_RE = re.compile('<.*?>')


def get_verbs_with_sein() -> list[WordInfo]:
    notes = get_notes_from_deck(SEIN_VERBS_DECK_NAME)

    words = []
    for note in notes:
        try:
            if word := parse_verb_note(note):
                words.append(word)
        except Exception:
            rprint(note.joined_fields())
            raise

    return words


def get_verbs_with_haben() -> list[WordInfo]:
    notes = get_notes_from_deck(ALL_WORDS_DECK_NAME)

    words = []
    for note in notes:
        try:
            if word := parse_verb_note(note):
                words.append(word)
        except Exception:
            rprint(note.joined_fields())
            raise

    return words


def parse_verb_note(note: Note) -> WordInfo | None:
    word_type = CLEAN_HTML_RE.sub("", note["Info"])
    if word_type != "VERB":
        return None

    word = WordInfo()
    word.translation = CLEAN_HTML_RE.sub("", note["Back"]).replace("&nbsp;", " ")

    front = BeautifulSoup(note["Front"], 'html.parser')
    word.present = front.find("h2").get_text().strip()

    example = BeautifulSoup(note["Example"], 'html.parser')
    word.simple_past = example.find(class_="prateritum-value").get_text().strip()
    word.past_participle = example.find(class_="partizip2-value").get_text().strip()

    return word
