from enum import Enum

import typer
from openai import OpenAI
from openai.types.responses import Response
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown

from anki_training.config import settings

openai = OpenAI(api_key=settings.OPEN_AI_API_KEY)


class State(Enum):
    START = 1
    WAITING_FOR_TRANSLATION = 2
    WAITING_FOR_QUESTION = 3


def translate_command():
    # python -m main translate
    rprint("Ти викладач німецької мови.")
    rprint("Дай одне речення українською на рівні B1-B2 для перекладу на німецьку.\n")

    state = State.START
    exercise = Exercise()

    while True:
        if state is State.START:
            response = exercise.get_sentence()
            print_response(response)
            state = State.WAITING_FOR_TRANSLATION
            continue

        if state is State.WAITING_FOR_TRANSLATION:
            translation = typer.prompt("Переклад").strip()
            rprint("")
            response = exercise.check_translation(translation)
            print_response(response)
            state = State.WAITING_FOR_QUESTION
            continue

        if state is State.WAITING_FOR_QUESTION:
            message = typer.prompt("Маєш питання чи введи + для наступного речення").strip()
            rprint("")
            if message == "+":
                exercise = Exercise()
                state = State.START
            elif message:
                response = exercise.answer_question(message)
                print_response(response)
            continue

        raise RuntimeError(f"Undefined state: {state}")


class Exercise:
    def __init__(self) -> None:
        self._last_response: Response | None = None

    @property
    def previous_response_id(self) -> str | None:
        if self._last_response is None:
            return None
        return self._last_response.id

    def get_sentence(self) -> Response:
        response = openai.responses.create(
            model="gpt-4.1-mini",
            instructions="Ти викладач німецької мови.",
            input="Дай одне речення українською на рівні B1-B2 для перекладу на німецьку.",
        )
        self._last_response = response
        return response

    def check_translation(self, translation: str) -> Response:
        response = openai.responses.create(
            model="gpt-4.1-mini",
            input=f'Мій переклад: "{translation}" Виправ помилки та поясни ці помилки, чому правильно інакше.'
            f" Якщо немає помилок, то не потрібно додаткових пояснень.",
            previous_response_id=self.previous_response_id,
        )
        self._last_response = response
        return response

    def answer_question(self, question: str) -> Response:
        response = openai.responses.create(
            model="gpt-4.1-mini",
            input=f"Маю уточнююче питання: {question}",
            previous_response_id=self.previous_response_id,
        )
        self._last_response = response
        return response


def print_response(response: Response) -> None:
    console = Console()
    md = Markdown(response.output[0].content[0].text)
    console.print(md)
    console.print("")
