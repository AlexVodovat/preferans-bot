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
main_menu = InlineKeyboardMarkup(row_width=2)
main_menu.add(
    InlineKeyboardButton("📘 Базовый", callback_data="test_basic"),
    InlineKeyboardButton("🌀 Роспасы", callback_data="test_raspas"),
    InlineKeyboardButton("♣ Висты", callback_data="test_vists"),
    InlineKeyboardButton("🧠 Продвинутый", callback_data="test_advanced")
)

# Словарь тестов
tests = {
    "test_basic": [
        {
            "q": "Что такое прикуп?",
            "a": ["2 карты, оставшиеся после сдачи", "Перерыв в игре", "Проигрыш"],
            "correct": 0,
            "explanation": "Прикуп — это 2 карты, которые остаются после сдачи. Их берёт игрок, выигравший торг."
        },
        {
            "q": "Кто делает первый ход?",
            "a": ["Игрок слева от сдающего", "Игрок, сделавший заказ", "Любой игрок по желанию"],
            "correct": 1,
            "explanation": "Первым всегда ходит игрок, который выиграл торг и сделал заказ."
        },
    ],
    "test_raspas": [
        {
            "q": "Когда чаще всего играют распасы?",
            "a": ["Когда никто не взял заказ", "Когда есть туз червей", "Когда выигрываешь пулю"],
            "correct": 0,
            "explanation": "Распасы начинаются, если все трое пасуют — никто не берёт заказ."
        },
        {
            "q": "Цель распасов?",
            "a": ["Набрать больше взяток", "Избежать взяток", "Взять туза треф"],
            "correct": 1,
            "explanation": "В распасах выигрывает тот, кто набрал меньше взяток, желательно — ни одной."
        },
    ],
    "test_vists": [
        {
            "q": "Что такое вист?",
            "a": ["Игра втемную", "Защита против заказчика", "Подача карты с руки"],
            "correct": 1,
            "explanation": "Вист — это защита против игрока, который сделал заказ. Ты пытаешься не дать ему выполнить его."
        },
        {
            "q": "Сколько очков за успешный вист в пулю?",
            "a": ["4", "2", "6"],
            "correct": 1,
            "explanation": "Успешный вист приносит 2 очка в пулю. Если ты не помешал — 2 штрафа."
        },
    ],
    "test_advanced": [
        {
            "q": "Можно ли играть мизер с шестёркой червей на руке?",
            "a": ["Да, если есть козыри", "Нет, это плохой план", "Только на прикупе"],
            "correct": 1,
            "explanation": "Шестёрка червей — опасная карта, особенно без козырей. Мизер почти обречён на провал."
        },
        {
            "q": "Как отличить хороший распас?",
            "a": ["Если много старших карт — плохой", "Много козырей — хорошо", "Сдача не имеет значения"],
            "correct": 0,
            "explanation": "Хороший распас — это когда на руках младшие карты. Чем меньше старших — тем лучше."
        },
    ]
}

user_progress = {}

# Стартовая команда
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привет! 👋\nВыбери один из тестов по преферансу:", reply_markup=main_menu)

# Запуск теста
@dp.callback_query_handler(lambda c: c.data.startswith("test_"))
async def start_test(callback: types.CallbackQuery):
    test_id = callback.data
    user_id = callback.from_user.id
    user_progress[user_id] = {"test_id": test_id, "q": 0, "correct": 0}
    await callback.message.edit_text("📋 Начинаем тест!")
    await send_question(callback.message, user_id)

# Отправка вопроса
async def send_question(message, user_id):
    progress = user_progress[user_id]
    test_id = progress["test_id"]
    test = tests[test_id]
    idx = progress["q"]

    if idx >= len(test):
        result = f"✅ Тест завершён!\nТы ответил правильно на {progress['correct']} из {len(test)} вопросов."
        await message.answer(result, reply_markup=main_menu)
        return

    q = test[idx]
    keyboard = InlineKeyboardMarkup()
    for i, option in enumerate(q["a"]):
        callback_data = f"answer_{test_id}_{idx}_{i}"
        keyboard.add(InlineKeyboardButton(option, callback_data=callback_data))

    await message.answer(f"❓ {q['q']}", reply_markup=keyboard)

# Обработка ответа
@dp.callback_query_handler(lambda c: c.data.startswith("answer_"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split("_", 3)
    if len(parts) != 4:
        await callback.message.answer("Произошла ошибка. Попробуй /start")
        return

    _, test_id, q_idx, answer_idx = parts
    q_idx = int(q_idx)
    answer_idx = int(answer_idx)

    if user_id not in user_progress or user_progress[user_id]["test_id"] != test_id:
        user_progress[user_id] = {"test_id": test_id, "q": q_idx, "correct": 0}

    test = tests[test_id]
    question = test[q_idx]
    correct = question["correct"]

    explanation = question.get("explanation", "")
    if answer_idx == correct:
        user_progress[user_id]["correct"] += 1
        feedback = "✅ Верно!"
    else:
        feedback = f"❌ Неверно. Правильный ответ: {question['a'][correct]}"

    if explanation:
        feedback += f"\nℹ️ {explanation}"

    await callback.message.answer(feedback)
    user_progress[user_id]["q"] = q_idx + 1
    await send_question(callback.message, user_id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
