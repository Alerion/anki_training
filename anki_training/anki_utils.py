from anki.collection import Collection, Note

from .config import settings


def get_notes_from_deck(
    deck_name: str,
    collection_path: str = settings.COLLECTION_PATH,
) -> list[Note]:
    collection = Collection(collection_path)
    deck = collection.decks.by_name(deck_name)
    deck_id = deck["id"]
    card_ids = collection.decks.cids(deck_id)

    note_ids = set()
    notes = []
    for card_id in card_ids:
        card = collection.get_card(card_id)
        if card.nid not in note_ids:
            notes.append(card.note())
            note_ids.add(card.nid)

    return notes
