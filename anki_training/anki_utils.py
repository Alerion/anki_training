from anki.collection import Collection, Note
from .config import COLLECTION_PATH


def get_notes_from_deck(
    deck_name: str,
    collection_path: str = COLLECTION_PATH,
) -> list[Note]:
    collection = Collection(collection_path)
    deck = collection.decks.by_name(deck_name)
    deck_id = deck['id']
    card_ids = collection.decks.cids(deck_id)

    notes = []
    for card_id in card_ids:
        card = collection.get_card(card_id)
        notes.append(card.note())

    return notes
