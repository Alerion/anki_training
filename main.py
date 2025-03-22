from anki.db import DB
from anki.collection import Collection
from rich import print as rprint
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
import typer
import random
import keyboard
from enum import Enum
from rich.console import Console
from rich.text import Text

from anki_training.get_words import get_words_from_collection
from anki_training.datatypes import WordInfo


class Event(Enum):
    CORRECT = 1
    INCORRECT = 2
    SHOW_ANSWER = 3
    EXIT = 4



VERBOSE_FIELD_NAME = {
    "simple_past": "past",
    "past_participle": "perfect",
    "present": "present",
}


def main():
    words = get_words_from_collection()
    rprint(f"Found {len(words)} words.")
    rprint("ESC to exit.")
    rprint("SPACE to show answer.")
    rprint("1 if you knew answer.")
    rprint("2 if you did not know answer.\n")
    i = 1
    correct = 0
    incorrect = 0
    is_waiting_result_validation = False

    word = random.choice(words)
    field_name, field_value = get_random_field(word)
    typer.secho(f"{i}: {field_value}", fg=typer.colors.GREEN)

    while True:
        event = wait_for_event()

        if event == Event.EXIT:
            total = correct + incorrect
            if total:
                rprint(f"CORRECT: {correct}, {correct / total:.1%}")
                rprint(f"INCORRECT: {incorrect}, {incorrect / total:.1%}")
            raise typer.Exit()

        if event == Event.SHOW_ANSWER:
            console = Console()
            styled_text = Text()
            styled_text.append(word.translation, style="bold orange4")
            styled_text.append("    ", style="default")
            styled_text.append(VERBOSE_FIELD_NAME[field_name], style="bold blue")
            console.print(styled_text)
            rprint("Press 1 if correct, otherwise 2...\n")
            is_waiting_result_validation = True
            continue

        if not is_waiting_result_validation:
            continue

        if event == Event.CORRECT:
            correct += 1
        if event == Event.INCORRECT:
            incorrect += 1

        i += 1
        word = random.choice(words)
        field_name, field_value = get_random_field(word)
        typer.secho(f"{i}: {field_value}", fg=typer.colors.GREEN)
        is_waiting_result_validation = False


def wait_for_event() -> Event:
    while True:
        keyboard_event = keyboard.read_event(suppress=True)
        if keyboard_event.event_type != keyboard.KEY_DOWN:
            continue

        if keyboard_event.name == "esc":
            return Event.EXIT
        if keyboard_event.name == "1":
            return Event.CORRECT
        if keyboard_event.name == "2":
            return Event.INCORRECT
        if keyboard_event.name == "space":
            return Event.SHOW_ANSWER


def get_random_field(word: WordInfo):
    fields = ['simple_past', 'past_participle', 'present']
    field_name = random.choice(fields)
    return field_name, getattr(word, field_name)


if __name__ == "__main__":
    typer.run(main)
