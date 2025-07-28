from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import logging
import os

API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise RuntimeError("❌ Не задан BOT_TOKEN в переменных окружения")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Главное меню — 2 колонки
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
            "a": ["2 карты после сдачи", "Перерыв в игре", "Особая ставка"],
            "correct": 0,
            "explanation": "Прикуп — две карты, которые остаются после сдачи. Их берёт заказчик."
        },
        {
            "q": "Кто ходит первым после торговли?",
            "a": ["Игрок слева от сдающего", "Игрок, сделавший заказ", "Все одновременно"],
            "correct": 1,
            "explanation": "Первым ходит заказчик — игрок, выигравший торг."
        }
    ],
    "test_raspas": [
        {
            "q": "Когда начинается распасовка?",
            "a": ["Если все пасуют", "Если есть мизер", "Если сильный козырь"],
            "correct": 0,
            "explanation": "Распасовка запускается, когда никто не берёт заказ."
        },
        {
            "q": "Цель распаса?",
            "a": ["Взять много взяток", "Не взять ни одной", "Взять все козыри"],
            "correct": 1,
            "explanation": "В распасовке нужно избежать взяток — желательно ни одной."
        }
    ],
    "test_vists": [
        {
            "q": "Что такое вист?",
            "a": ["Ставка против заказчика", "Игра вслепую", "Особый прикуп"],
            "correct": 0,
            "explanation": "Вист — это ставка против игрока, взявшего прикуп (заказчика)."
        },
        {
            "q": "Сколько вистов может быть?",
            "a": ["До двух", "Неограниченно", "Ноль"],
            "correct": 0,
            "explanation": "Вистовать могут двое: слева и справа от заказчика."
        }
    ],
    "test_advanced": [
        {
            "q": "Можно ли играть мизер при тузе червей?",
            "a": ["Да", "Нет", "Только в распасе"],
            "correct": 1,
            "explanation": "Мизер с сильной картой на руках слишком рискован."
        },
        {
            "q": "Как понять хороший распас?",
            "a": ["Мало старших карт", "Много козырей", "Много взяток"],
            "correct": 0,
            "explanation": "Лучший распас — когда у вас слабые, невзятковые карты."
        }
    ]
}

# Хранилище прогресса
user_progress = {}

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! 👋 Выбери тест:", reply_markup=main_menu)

@dp.callback_query_handler(lambda c: c.data.startswith("test_"))
async def start_test(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    test_id = callback.data
    user_progress[user_id] = {"test_id": test_id, "q_idx": 0, "correct": 0}
    await callback.message.edit_text("📋 Начинаем тест!")
    await send_question(callback.message, user_id)

async def send_question(message: types.Message, user_id: int):
    prog = user_progress.get(user_id)
    if not prog:
        await message.answer("Ошибка прогресса. Попробуй /start")
        return

    test_id = prog["test_id"]
    q_idx = prog["q_idx"]
    test = tests[test_id]

    # Если вопросы закончились
    if q_idx >= len(test):
        total = len(test)
        correct = prog["correct"]
        await message.answer(f"✅ Тест завершён: {correct}/{total} правильных.", reply_markup=main_menu)
        return

    item = test[q_idx]
    kb = InlineKeyboardMarkup()
    for i, opt in enumerate(item["a"]):
        cb = f"answer|{test_id}|{q_idx}|{i}"
        kb.add(InlineKeyboardButton(opt, callback_data=cb))

    await message.answer(f"❓ {item['q']}", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("answer|"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split("|")
    if len(parts) != 4:
        await callback.message.answer("Ошибка формата. Попробуй /start")
        return

    _, test_id, q_idx, ans_idx = parts
    q_idx = int(q_idx); ans_idx = int(ans_idx)

    prog = user_progress.get(user_id)
    if not prog or prog["test_id"] != test_id:
        prog = {"test_id": test_id, "q_idx": q_idx, "correct": 0}
        user_progress[user_id] = prog

    question = tests[test_id][q_idx]
    correct = question["correct"]
    explanation = question.get("explanation", "")

    if ans_idx == correct:
        prog["correct"] += 1
        text = "✅ Правильно!"
    else:
        text = f"❌ Неправильно, верный ответ: {question['a'][correct]}."

    if explanation:
        text += f"\nℹ️ {explanation}"

    await callback.message.answer(text)
    prog["q_idx"] = q_idx + 1
    await send_question(callback.message, user_id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
