from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import logging
import os

API_TOKEN = os.getenv("BOT_TOKEN") or "сюда_вставь_токен_бота"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# Главное меню с выбором теста
main_menu = InlineKeyboardMarkup(row_width=1)
main_menu.add(
    InlineKeyboardButton("🟨 Тест по распасам", callback_data="test_raspas"),
    InlineKeyboardButton("🟦 Тест по вистам", callback_data="test_vists"),
    InlineKeyboardButton("🟥 Продвинутый тест", callback_data="test_advanced")
)

# Вопросы
tests = {
    "test_raspas": [
        {
            "q": "Когда чаще всего играют распасы?",
            "a": ["Когда никто не взял заказ", "Когда есть туз червей", "Когда выигрываешь пулю"],
            "correct": 0
        },
        {
            "q": "Какая цель в распасах?",
            "a": ["Набрать больше взяток", "Избежать взяток", "Взять туза треф"],
            "correct": 1
        },
    ],
    "test_vists": [
        {
            "q": "Что такое вист?",
            "a": ["Игра втемную", "Защита против играющего", "Подача карты с руки"],
            "correct": 1
        },
        {
            "q": "Сколько очков за успешный вист в пулю?",
            "a": ["4", "2", "6"],
            "correct": 1
        },
    ],
    "test_advanced": [
        {
            "q": "Можно ли играть мизер при шестёрке червей на руке?",
            "a": ["Да, если есть козыри", "Нет, это плохой план", "Только на прикупе"],
            "correct": 1
        },
        {
            "q": "Как отличить хороший распас от плохого?",
            "a": ["Если есть много старших карт — плохой", "Много козырей — хорошо", "Сдача не имеет значения"],
            "correct": 0
        },
    ]
}

user_progress = {}

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привет! 👋\nВыбери один из тестов по преферансу:", reply_markup=main_menu)

@dp.callback_query_handler(lambda c: c.data.startswith("test_"))
async def start_test(callback: types.CallbackQuery):
    test_id = callback.data
    user_id = callback.from_user.id
    user_progress[user_id] = {
        "test_id": test_id,
        "q": 0,
        "correct": 0
    }
    await callback.message.edit_text("📋 Начинаем тест!\n")
    await send_question(callback.message, user_id)

async def send_question(message, user_id):
    progress = user_progress[user_id]
    test = tests[progress["test_id"]]
    idx = progress["q"]

    if idx >= len(test):
        result = f"✅ Тест завершён!\nТы ответил правильно на {progress['correct']} из {len(test)} вопросов."
        await message.answer(result, reply_markup=main_menu)
        return

    q = test[idx]
    keyboard = InlineKeyboardMarkup()
    for i, option in enumerate(q["a"]):
        keyboard.add(InlineKeyboardButton(option, callback_data=f"answer_{i}"))
    await message.answer(f"❓ {q['q']}", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("answer_"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    progress = user_progress.get(user_id)
    if not progress:
        await callback.message.answer("Пожалуйста, начни сначала /start")
        return

    answer_idx = int(callback.data.split("_")[1])
    current_question = tests[progress["test_id"]][progress["q"]]

    if answer_idx == current_question["correct"]:
        progress["correct"] += 1

    progress["q"] += 1
    await send_question(callback.message, user_id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

