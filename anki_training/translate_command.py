import random
from enum import Enum

from openai import OpenAI
from openai.types.responses import Response
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text

from anki_training.config import settings

openai = OpenAI(api_key=settings.OPEN_AI_API_KEY)

MESSAGE_STYLE = "bold green"
RESPONSE_STYLE = "bold orange4"


class DeutschLevel(str, Enum):
    B1 = "B1"
    B2 = "B2"
    # C1 = "C1"


class DeutschTime(str, Enum):
    Präsens = "Präsens"
    Perfekt = "Perfekt"
    Präteritum = "Präteritum"
    Futur1 = "Futur I"


class State(Enum):
    START = 1
    WAITING_FOR_TRANSLATION = 2
    WAITING_FOR_QUESTION = 3


def translate_command():
    # python -m main translate
    print_message("Дай одне речення українською для перекладу на німецьку.\n")

    state = State.START
    exercise = Exercise()
    counter = 0

    while True:
        if state is State.START:
            counter += 1
            response = exercise.get_sentence()
            print_sentence(counter, response)
            state = State.WAITING_FOR_TRANSLATION
            continue

        if state is State.WAITING_FOR_TRANSLATION:
            translation = Prompt.ask(Text("Мій переклад", MESSAGE_STYLE)).strip()
            rprint("")
            response = exercise.check_translation(translation)
            print_response(response)
            state = State.WAITING_FOR_QUESTION
            continue

        if state is State.WAITING_FOR_QUESTION:
            message = Prompt.ask(
                Text("Маєш питання чи введи + для наступного речення?", RESPONSE_STYLE)
            ).strip()
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
        deutsch_level = get_random_deutsch_level()
        deutsch_time = get_random_deutsch_time()
        print_bot_message(f"Рівень: {deutsch_level.value}. Час: {deutsch_time.value}")
        response = openai.responses.create(
            model="gpt-4.1",
            instructions="Ти викладач німецької мови.",
            input=f"""
Дай одне речення українською на рівні {deutsch_level} для перекладу на німецьку.
Це речення має бути німецькою буде в {deutsch_time}.
Також можеш використовути Adjektive, щоб я тренував Deklination.
Також Präpositionen, щоб я вчив відмінювання слів з ними.
Це все не обов'язково додавати в одне речення. Обери щось випадково.
Поверни лише речення, не потрібно додаткових коментарів.
""",
        )
        self._last_response = response
        return response

    def check_translation(self, translation: str) -> Response:
        response = openai.responses.create(
            model="gpt-4.1-mini",
            input=f'Мій переклад: "{translation}" Виправ помилки та поясни чому ти виправив.'
            f" Якщо є помилки, то відили *курсивом* в markdown те, що ти виправив."
            f" Якщо немає помилок, то не потрібно додаткових пояснень."
            f" Назви відмінків пиши англійською: Nominative, Accusative, Dative, Genitive.",
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


def print_message(message: str) -> None:
    console = Console()
    styled_text = Markdown(message, MESSAGE_STYLE)
    console.print(styled_text)


def print_sentence(number: int, response: Response) -> None:
    console = Console()
    sentence = response.output[0].content[0].text
    md = Markdown(f"({number}) {sentence}", style=RESPONSE_STYLE)
    console.print(md)
    console.print("")


def print_response(response: Response) -> None:
    console = Console()
    md = Markdown(response.output[0].content[0].text, style=RESPONSE_STYLE)
    console.print(md)
    console.print("")


def print_bot_message(message: str) -> None:
    console = Console()
    styled_text = Markdown(message, RESPONSE_STYLE)
    console.print(styled_text)


def get_random_deutsch_level() -> DeutschLevel:
    return random.choice(list(DeutschLevel))


def get_random_deutsch_time() -> DeutschTime:
    return random.choice(list(DeutschTime))
