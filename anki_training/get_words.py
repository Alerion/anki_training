from anki.collection import Collection
from rich import print as rprint
from bs4 import BeautifulSoup
import re

from .datatypes import WordInfo

COLLECTION_PATH = "c:/Users/user/AppData/Roaming/Anki2/User 1/collection.anki2"
DECK_NAME = "Deutsch::07 Irregular Verbs"


def get_words_from_collection():
    collection = Collection(COLLECTION_PATH)
    deck = collection.decks.by_name(DECK_NAME)
    deck_id = deck['id']
    card_ids = collection.decks.cids(deck_id)

    words = []
    for card_id in card_ids:
        card = collection.get_card(card_id)
        note = card.note()
        try:
            words.append(parse_note_back_field(note["Back"]))
        except Exception:
            rprint(note["Back"])
            raise

    return words



def parse_note_back_field(html_content) -> WordInfo:
    soup = BeautifulSoup(html_content, 'html.parser')
    word_info = WordInfo()

    translation_tag = soup.find('font', color="#c12d30")
    word_info.translation = translation_tag.get_text().strip()

    simple_past_span = soup.find('span', string=re.compile(r"Simple past"))
    simple_past_value_span = simple_past_span.find_next('span')
    word_info.simple_past = simple_past_value_span.get_text().strip()

    past_participle_span = soup.find('span', string=re.compile(r'Past participle'))
    past_participle_value_span = past_participle_span.find_next('span')
    word_info.past_participle = past_participle_value_span.get_text().strip()

    present_span = soup.find('span', string=re.compile("er/sie/es"))
    present_value_span = present_span.find_next('span')
    if present_value_span is None:
        present_value_span = present_span.find_next('b')
    word_info.present = present_value_span.get_text().strip()

    return word_info