from enum import Enum

import keyboard
import typer
from rich import print as rprint
from rich.console import Console
from rich.text import Text

from anki_training.get_irregular_verbs_words import (
    get_irregular_verbs_cards,
    get_irregular_verbs_from_collection,
)


class Event(Enum):
    CORRECT = 1
    INCORRECT = 2
    SHOW_ANSWER = 3
    EXIT = 4


def irregular_verbs_command():
    words = get_irregular_verbs_from_collection()
    word_cards = get_irregular_verbs_cards(words)
    rprint(f"Found {len(words)} words.")
    rprint("ESC to exit.")
    rprint("SPACE to show answer.")
    rprint("4 if you knew answer.")
    rprint("1 if you did not know answer.\n")
    i = 1
    correct = 0
    incorrect = 0
    is_waiting_result_validation = False

    word_card = word_cards.pop(0)
    typer.secho(f"{i}: {word_card.word}", fg=typer.colors.GREEN)

    def finish():
        total = correct + incorrect
        if total:
            rprint(f"CORRECT: {correct}, {correct / total:.1%}")
            rprint(f"INCORRECT: {incorrect}, {incorrect / total:.1%}")
        raise typer.Exit()

    while True:
        event = wait_for_event()

        if event == Event.EXIT:
            finish()

        if event == Event.SHOW_ANSWER:
            console = Console()
            styled_text = Text()
            styled_text.append(word_card.translation, style="bold orange4")
            styled_text.append("    ", style="default")
            styled_text.append(word_card.time, style="bold blue")
            styled_text.append("\n", style="default")
            console.print(styled_text)
            is_waiting_result_validation = True
            continue

        if not is_waiting_result_validation:
            continue

        if event == Event.CORRECT:
            correct += 1
        if event == Event.INCORRECT:
            incorrect += 1

        if len(word_cards) == 0:
            finish()

        i += 1
        word_card = word_cards.pop(0)
        typer.secho(f"{i}: {word_card.word}", fg=typer.colors.GREEN)
        is_waiting_result_validation = False


def wait_for_event() -> Event:
    while True:
        keyboard_event = keyboard.read_event(suppress=True)
        if keyboard_event.event_type != keyboard.KEY_DOWN:
            continue

        if keyboard_event.name == "esc":
            return Event.EXIT
        if keyboard_event.name == "4":
            return Event.CORRECT
        if keyboard_event.name == "1":
            return Event.INCORRECT
        if keyboard_event.name == "space":
            return Event.SHOW_ANSWER
