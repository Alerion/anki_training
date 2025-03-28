from anki.db import DB
from anki.collection import Collection
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
import typer
import random
import keyboard
from enum import Enum
from rich.console import Console
from rich.text import Text
from rich import print as rprint

from anki_training.get_irregular_verbs_words import (
    get_irregular_verbs_from_collection, get_irregular_verbs_cards, get_verb_cards_from_words
)
from anki_training.datatypes import AuxiliaryVerb
from anki_training.get_verbs_words import get_verbs_with_sein, get_verbs_with_haben
from anki_training.irregular_verbs_command import irregular_verbs_command
from anki_training.sein_oder_haben_command import sein_oder_haben_command

app = typer.Typer()

# python -m main irregular_verbs
app.command("irregular_verbs")(irregular_verbs_command)
# python -m main sein_oder_haben
app.command("sein_oder_haben")(sein_oder_haben_command)


if __name__ == "__main__":
    app()
