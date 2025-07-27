from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import logging
import os

API_TOKEN = os.getenv("BOT_TOKEN")

if not API_TOKEN:
    raise ValueError("❌ BOT_TOKEN не установлен в переменных окружения.")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Главное меню
main_menu = InlineKeyboardMarkup(row_width=1)
main_menu.add(
    InlineKeyboardButton("🟨 Тест по распасам", callback_data="test_raspas"),
    InlineKeyboardButton("🟦 Тест по вистам", callback_data="test_vists"),
    InlineKeyboardButton("🟥 Продвинутый тест", callback_data="test_advanced")
)

# Тесты
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
        }
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
        }
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
        }
    ]
}

# Хранение прогресса пользователей
user_progress = {}

# Команда старт
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! 👋\nВыбери один из тестов по преферансу:", reply_markup=main_menu)

# Обработка выбора теста
@dp.callback_query_handler(lambda c: c.data.startswith("test_"))
async def start_test(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    test_id = callback.data

    user_progress[user_id] = {
        "test_id": test_id,
        "q_idx": 0,
        "correct": 0
    }

    await callback.message.edit_text("📋 Начинаем тест!\n")
    await send_question(callback.message, user_id)

# Отправка вопроса
async def send_question(message, user_id):
    progress = user_progress[user_id]
    test = tests[progress["test_id"]]
    idx = progress["q_idx"]

    if idx >= len(test):
        total = len(test)
        correct = progress["correct"]
        await message.answer(f"✅ Тест завершён!\nТы ответил правильно на {correct} из {total} вопросов.", reply_markup=main_menu)
        return

    q_data = test[idx]
    keyboard = InlineKeyboardMarkup()
    for i, ans in enumerate(q_data["a"]):
        cb_data = f"answer|{progress['test_id']}|{idx}|{i}"
        keyboard.add(InlineKeyboardButton(ans, callback_data=cb_data))

    await message.answer(f"❓ {q_data['q']}", reply_markup=keyboard)

# Обработка ответов
@dp.callback_query_handler(lambda c: c.data.startswith("answer|"))
async def handle_answer(callback: types.CallbackQuery):
    try:
        _, test_id, q_idx, answer_idx = callback.data.split("|")
        user_id = callback.from_user.id
        q_idx = int(q_idx)
        answer_idx = int(answer_idx)

        test = tests[test_id]
        correct = test[q_idx]["correct"]

        if user_id not in user_progress:
            await callback.message.answer("Произошла ошибка. Начни заново командой /start")
            return

        if answer_idx == correct:
            user_progress[user_id]["correct"] += 1

        user_progress[user_id]["q_idx"] += 1
        await send_question(callback.message, user_id)

    except Exception as e:
        logging.error(f"Ошибка при обработке ответа: {e}")
        await callback.message.answer("Произошла ошибка. Попробуй снова через /start")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)




