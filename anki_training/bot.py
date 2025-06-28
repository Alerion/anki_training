import random
from enum import Enum

import anthropic
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from anki_training.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


class DeutschLevel(str, Enum):
    B1 = "B1"
    B2 = "B2"


class DeutschTime(str, Enum):
    PRÄSENS = "Präsens"
    PERFEKT = "Perfekt"
    PRÄTERITUM = "Präteritum"
    FUTUR1 = "Futur I"


class State(Enum):
    IDLE = 1
    WAITING_FOR_TRANSLATION = 2
    WAITING_FOR_QUESTION = 3


# TODO
def generate_focused_sentence_prompt(session):
    context_hints = {
        "PRÄSENS": "повсякденні дії, звички",
        "PERFEKT": "завершені дії, досвід",
        "PRÄTERITUM": "розповіді про минуле",
        "FUTUR1": "плани, наміри",
    }

    return f"""Створи речення українською ({session.level.value}):
- Час: {session.tense.value} - {context_hints.get(session.tense.value, "")}
- 1-2 прикметники для тренування відмінювання
- 1 прийменник з чіткою відмінкою
- Речення має бути життєвим, не штучним

Тільки речення, без коментарів."""


def start_bot():
    # python -m main start_bot
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("new", new_exercise))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot started!")
    application.run_polling()


class UserSession:
    def __init__(self):
        self.state = State.IDLE
        self.current_sentence = ""
        self.conversation_history = []
        self.counter = 0
        self.level = None
        self.tense = None

    def reset_exercise(self):
        self.current_sentence = ""
        self.conversation_history = []
        self.level = None
        self.tense = None


user_sessions: dict[int, UserSession] = {}


def get_user_session(user_id: int) -> UserSession:
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    return user_sessions[user_id]


def get_random_deutsch_level() -> DeutschLevel:
    return random.choice(list(DeutschLevel))


def get_random_deutsch_time() -> DeutschTime:
    return random.choice(list(DeutschTime))


async def call_anthropic(prompt: str, conversation_history: list = None) -> str:
    try:
        messages = []

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": prompt})

        system_prompt = """Ти викладач німецької для українців рівня B1-B2. Правила:
- Відповідай українською, коротко і по суті
- Фокусуйся на практичних помилках: порядок слів, відмінки, артиклі
- Давай конкретні поради, не загальні правила
- Приклади тільки якщо потрібно прояснити складне правило
- Відмінки: Nominative, Accusative, Dative, Genitive"""

        message = client.messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=1000, messages=messages, system=system_prompt
        )

        return message.content[0].text
    except Exception as e:
        return f"Anthropic API error: {str(e)}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /start"""
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    session.state = State.IDLE

    keyboard = [
        [InlineKeyboardButton("🎯 Почати вправу", callback_data="start_exercise")],
        [InlineKeyboardButton("ℹ️ Довідка", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = """
🇩🇪 Вітаю! Я бот для вивчення німецької мови.

Я допоможу вам практикувати переклад з української на німецьку мову.

Натисніть "Почати вправу" щоб розпочати!
"""

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /help"""
    help_text = """
🆘 **Як користуватися ботом:**

1️⃣ Натисніть "Почати вправу"
2️⃣ Я дам вам речення українською для перекладу
3️⃣ Введіть ваш переклад німецькою
4️⃣ Я перевірю переклад і дам поради
5️⃣ Можете задати питання або перейти до наступного речення

**Команди:**
/start - Головне меню
/help - Ця довідка
/new - Нова вправа

**Під час вправи:**
• Введіть "+" для наступного речення
• Або задайте питання про переклад
"""

    keyboard = [[InlineKeyboardButton("🏠 Головне меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")


async def new_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /new"""
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    session.reset_exercise()
    session.state = State.IDLE

    await start_new_exercise(update, context, user_id)


async def start_new_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    session = get_user_session(user_id)
    session.counter += 1
    session.level = get_random_deutsch_level()
    session.tense = get_random_deutsch_time()
    session.state = State.WAITING_FOR_TRANSLATION

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    prompt = f"""Створи речення українською для перекладу на німецьку:
- Рівень: {session.level.value}
- Час: {session.tense.value}
- Включи 1-2 прикметники (для відмінювання), не більше!
- Включи 1-2 прийменники з відмінками
- Зроби речення практичним та корисним.
- Речення має бути не більше 15 слів, щоб переклад не займав багато часу.

Поверни тільки речення."""

    sentence = await call_anthropic(prompt)
    session.current_sentence = sentence
    session.conversation_history = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": sentence},
    ]

    message_text = f"""
📚 **Вправа #{session.counter}**
🎯 Рівень: {session.level.value}
⏰ Час: {session.tense.value}

🇺🇦 **Речення для перекладу:**
{sentence}

Введіть ваш переклад німецькою мовою:
"""

    if update.callback_query:
        await update.callback_query.edit_message_text(message_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(message_text, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    user_text = update.message.text.strip()

    if session.state == State.IDLE:
        await update.message.reply_text("Натисніть /start щоб почати або /new для нової вправи")
        return

    if session.state == State.WAITING_FOR_TRANSLATION:
        await handle_translation(update, context, user_id, user_text)

    elif session.state == State.WAITING_FOR_QUESTION:
        if user_text == "+":
            await start_new_exercise(update, context, user_id)
        else:
            await handle_question(update, context, user_id, user_text)


async def handle_translation(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, user_translation: str
):
    session = get_user_session(user_id)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    prompt = f"""Оригінальне речення: "{session.current_sentence}"
Мій переклад: "{user_translation}"

Перевір переклад та:
1. Виправ помилки (*курсивом* в markdown)
2. Поясни ключові помилки стисло
3. Дай 1-2 практичні поради щодо граматики/структури
4. Відмінки пиши англійською: Nominative, Accusative, Dative, Genitive

Якщо переклад правильний - напиши "Правильно!" та дай одну корисну пораду про вжите правило."""

    session.conversation_history.append({"role": "user", "content": prompt})

    response = await call_anthropic(prompt, session.conversation_history)

    session.conversation_history.append({"role": "assistant", "content": response})
    session.state = State.WAITING_FOR_QUESTION

    keyboard = [
        [InlineKeyboardButton("➕ Наступне речення", callback_data="next_sentence")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = f"✅ **Перевірка перекладу:**\n\n{response}\n\n❓ Маєте питання? Просто напишіть їх, або натисніть кнопку нижче:"

    await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_question(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, question: str
):
    session = get_user_session(user_id)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    prompt = f"Маю уточнююче питання: {question}"

    session.conversation_history.append({"role": "user", "content": prompt})

    response = await call_anthropic(prompt, session.conversation_history)

    session.conversation_history.append({"role": "assistant", "content": response})

    keyboard = [
        [InlineKeyboardButton("➕ Наступне речення", callback_data="next_sentence")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"💡 **Відповідь:**\n\n{response}", reply_markup=reply_markup, parse_mode="Markdown"
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    session = get_user_session(user_id)

    if query.data == "start_exercise":
        await start_new_exercise(update, context, user_id)

    elif query.data == "next_sentence":
        await start_new_exercise(update, context, user_id)

    elif query.data == "main_menu":
        session.state = State.IDLE
        keyboard = [
            [InlineKeyboardButton("🎯 Почати вправу", callback_data="start_exercise")],
            [InlineKeyboardButton("ℹ️ Довідка", callback_data="help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_text = """
🇩🇪 **Головне меню**

Оберіть дію:
"""
        await query.edit_message_text(
            welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
        )

    elif query.data == "help":
        help_text = """
🆘 **Як користуватися ботом:**

1️⃣ Натисніть "Почати вправу"
2️⃣ Я дам вам речення українською для перекладу
3️⃣ Введіть ваш переклад німецькою
4️⃣ Я перевірю переклад і дам поради
5️⃣ Можете задати питання або перейти до наступного речення

**Команди:**
/start - Головне меню
/help - Ця довідка
/new - Нова вправа
"""

        keyboard = [[InlineKeyboardButton("🏠 Головне меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")
