from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import logging
import os

API_TOKEN = os.getenv("BOT_TOKEN") or "сюда_вставь_токен_бота"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# Главное меню
main_menu = InlineKeyboardMarkup(row_width=1)
main_menu.add(
    InlineKeyboardButton("🟨 Тест по распасам", callback_data="test_raspas"),
    InlineKeyboardButton("🟦 Тест по вистам", callback_data="test_vists"),
    InlineKeyboardButton("🟥 Продвинутый тест", callback_data="test_advanced")
    InlineKeyboardButton("🟩 Тест по правилам", callback_data="test_rules")
)

# Вопросы
tests = {
    "test_rules": [
    {
        "q": "Сколько карт в руке у каждого игрока?",
        "a": ["8", "10", "12"],
        "correct": 2
    },
    {
        "q": "Что такое прикуп?",
        "a": ["Дополнительные карты", "Вист", "Мизер"],
        "correct": 0
    }
],

    "test_raspas": [
        {
            "q": "Когда чаще всего играют распасы?",
            "a": ["Когда никто не заявил игру", "Когда есть туз червей", "Когда выигрываешь пулю"],
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
            "q": "Сколько очков за успешный вист на шестерной в пулю?",
            "a": ["4", "2", "6"],
            "correct": 1
        },
    ],
    "test_advanced": [
        {
            "q": "Можно ли играть мизер при семерке червей на руке?",
            "a": ["Да, если есть козыри", "Да, если и другие карты позволяют играть", "Только на прикупе"],
            "correct": 1
        },
        {
            "q": "Как отличить хороший распас от плохого?",
            "a": ["Если есть много старших карт — плохой", "Много козырей — хорошо", "Сдача не имеет значения"],
            "correct": 0
        },
    ]
}

# Состояние пользователя
user_progress = {}

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привет! 👋\nВыбери один из тестов по преферансу:", reply_markup=main_menu)

@dp.callback_query_handler(lambda c: c.data.startswith("test_"))
async def start_test(callback: types.CallbackQuery):
    test_id = callback.data
    user_id = callback.from_user.id
    user_progress[user_id] = {"test_id": test_id, "q": 0, "correct": 0}
    await callback.message.edit_text("📋 Начинаем тест!")
    await send_question(callback.message, user_id)

async def send_question(message, user_id):
    progress = user_progress.get(user_id)
    if not progress:
        await message.answer("Ошибка состояния. Попробуй /start")
        return

    test_id = progress["test_id"]
    test = tests[test_id]
    q_index = progress["q"]

    if q_index >= len(test):
        result = f"✅ Тест завершён!\nТы ответил правильно на {progress['correct']} из {len(test)} вопросов."
        await message.answer(result, reply_markup=main_menu)
        return

    question = test[q_index]
    keyboard = InlineKeyboardMarkup()
    for i, option in enumerate(question["a"]):
        callback_data = f"answer|{test_id}|{q_index}|{i}"
        keyboard.add(InlineKeyboardButton(option, callback_data=callback_data))

    await message.answer(f"❓ {question['q']}", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("answer|"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    try:
        _, test_id, q_idx, ans_idx = callback.data.split("|")
        q_idx = int(q_idx)
        ans_idx = int(ans_idx)
    except Exception:
        await callback.message.answer("Произошла ошибка. Попробуй /start")
        return

    if user_id not in user_progress or user_progress[user_id]["test_id"] != test_id:
        user_progress[user_id] = {"test_id": test_id, "q": q_idx, "correct": 0}

    correct = tests[test_id][q_idx]["correct"]
    if ans_idx == correct:
        user_progress[user_id]["correct"] += 1

    user_progress[user_id]["q"] = q_idx + 1
    await send_question(callback.message, user_id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)


