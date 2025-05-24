from openai import OpenAI

from anki_training.config import settings


def translate_command():
    client = OpenAI(api_key=settings.OPEN_AI_API_KEY)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[{"role": "user", "content": "write a haiku about ai"}],
    )

    print(completion.choices[0].message)
