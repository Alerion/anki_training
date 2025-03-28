import random
from enum import Enum

import keyboard
import typer
from rich import print as rprint
from rich.console import Console
from rich.text import Text

from anki_training.datatypes import AuxiliaryVerb
from anki_training.get_irregular_verbs_words import (
    get_verb_cards_from_words,
)
from anki_training.get_verbs_words import get_verbs_with_haben, get_verbs_with_sein


class Event(Enum):
    SEIN = 1
    HABEN = 2
    SKIP = 3
    EXIT = 4


def sein_oder_haben_command() -> None:
    # python -m main sein_oder_haben
    verbs_with_sein = get_verbs_with_sein()
    verbs_with_haben = get_verbs_with_haben()

    rprint(f"Found {len(verbs_with_sein)} verbs with sein.")
    rprint(f"Found {len(verbs_with_haben)} verbs with haben.")
    rprint("ESC to exit.")
    rprint("SPACE to skip word.")
    rprint("W if auxiliary verb is sein.")
    rprint("Q if auxiliary verb is haben.\n")

    random.shuffle(verbs_with_haben)
    verbs_with_haben = verbs_with_haben[: len(verbs_with_sein)]

    cards = get_verb_cards_from_words(verbs_with_haben, AuxiliaryVerb.haben)
    cards += get_verb_cards_from_words(verbs_with_haben, AuxiliaryVerb.sein)
    random.shuffle(cards)

    i = 1
    correct = 0
    incorrect = 0

    card = cards.pop(0)
    typer.secho(f"{i}: {card.word.past_participle}", fg=typer.colors.GREEN)

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

        if event == Event.SEIN:
            is_correct = card.auxiliary_verb == AuxiliaryVerb.sein
        elif event == Event.HABEN:
            is_correct = card.auxiliary_verb == AuxiliaryVerb.haben
        elif event == Event.SKIP:
            is_correct = False
        else:
            raise RuntimeError(f"Undefined event {event}")

        if is_correct:
            correct += 1
        else:
            incorrect += 1

        console = Console()
        styled_text = Text()
        if is_correct:
            styled_text.append(card.auxiliary_verb, style="bold green")
        else:
            styled_text.append(card.auxiliary_verb, style="bold red")
        styled_text.append("    ", style="default")
        styled_text.append(card.word.translation, style="bold orange4")
        styled_text.append("    ", style="default")
        styled_text.append(card.word.present, style="bold blue")
        styled_text.append("\n", style="default")
        console.print(styled_text)

        if len(cards) == 0:
            finish()

        i += 1
        card = cards.pop(0)
        typer.secho(f"{i}: {card.word.past_participle}", fg=typer.colors.GREEN)


def wait_for_event() -> Event:
    while True:
        keyboard_event = keyboard.read_event(suppress=True)
        if keyboard_event.event_type != keyboard.KEY_DOWN:
            continue

        if keyboard_event.name == "esc":
            return Event.EXIT
        if keyboard_event.name == "w":
            return Event.SEIN
        if keyboard_event.name == "q":
            return Event.HABEN
        if keyboard_event.name == "space":
            return Event.SKIP
