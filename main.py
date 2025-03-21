from anki.db import DB
from anki.collection import Collection
from rich import print as rprint
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
import typer
import random

from anki_training.get_words import get_words_from_collection
from anki_training.datatypes import WordInfo

def main():
    words = get_words_from_collection()
    while True:
        word = random.choice(words)
        field_name, field_value = get_random_field(word)

        typer.secho(field_value, fg=typer.colors.GREEN)
        user_input = input(f"")

        if user_input.strip() == "":
            rprint(f"{field_name} - {word.translation}\n")
        else:
            raise typer.Exit()


def get_random_field(word: WordInfo):
    fields = ['simple_past', 'past_participle', 'present']
    field_name = random.choice(fields)
    return field_name, getattr(word, field_name)


if __name__ == "__main__":
    typer.run(main)
