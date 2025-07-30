from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import logging
import os
import random  # ← нужно для симулятора

API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise RuntimeError("❌ Не задан BOT_TOKEN в переменных окружения")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# 1) Главное меню — 2 колонки
main_menu = InlineKeyboardMarkup(row_width=2)
main_menu.add(
    InlineKeyboardButton("📘 Базовый", callback_data="test_basic"),
    InlineKeyboardButton("🌀 Роспасы", callback_data="test_raspas"),
    InlineKeyboardButton("♣ Висты", callback_data="test_vists"),
    InlineKeyboardButton("🧠 Продвинутый", callback_data="test_advanced"),
    InlineKeyboardButton("🚀 Симулятор", callback_data="sim_main")
)

# 2) Тесты
tests = {
    "test_basic": [
        {
            "q": "Что такое прикуп?",
            "a": ["2 карты после сдачи", "Перерыв в игре", "Особая ставка"],
            "correct": 0,
            "explanation": "Прикуп — две карты, остающиеся после сдачи. Их берёт заказчик."
        },
        {
            "q": "Сколько человек может играть за столом?",
            "a": ["3", "4", "Либо 3 либо 4"],
            "correct": 2,
            "explanation": "В преферанс можно играть вчетвером (один на прикупе) или втроём (прикуп ничей)."
        },
        {
            "q": "Кто ходит первым после торговли?",
            "a": ["Игрок слева от сдающего", "Игрок, сделавший заказ", "Все одновременно"],
            "correct": 0,
            "explanation": "Первым ходит игрок, сидящий слева от сдающего."
        },
        {
            "q": "Сколько карт используется в классическом преферансе?",
            "a": ["32", "36", "52"],
            "correct": 0,
            "explanation": "В классическом русском преферансе играют колодой из 32 карт (7–туз)."
        },
        {
            "q": "Как называется контракт на отказ от всех взяток?",
            "a": ["Мизер", "Распасы", "Игра"],
            "correct": 0,
            "explanation": "«Мизер» — это контракт, при котором нужно уйти от всех взяток."
        },
        {
            "q": "Сколько карт получает каждый игрок при сдаче?",
            "a": ["10", "6", "8"],
            "correct": 0,
            "explanation": "Каждому игроку раздают по 10 карт, ещё 2 кладут в прикуп."
        },
        {
            "q": "Сколько козырей в преферансе?",
            "a": ["Один на всю игру", "Выбирается случайно", "Назначает игрок после прикупа"],
            "correct": 2,
            "explanation": "После торговли игрок, получивший прикуп, назначает козырь."
        },
    ],
    "test_raspas": [
        {
            "q": "Когда начинается распасовка?",
            "a": ["Если все пасуют", "Если есть мизер", "Если сильный козырь"],
            "correct": 0,
            "explanation": "Распас идёт, когда все пасуют и никто не берёт заказ."
        },
        {
            "q": "Участвуют ли в расчёте взяток карты из прикупа?",
            "a": ["Да", "Нет", "Только козыри"],
            "correct": 0,
            "explanation": "Карты из прикупа входят в общую кучку взяток."
        },
        {
            "q": "Кто делает первый ход в распасовке?",
            "a": ["Игрок слева от сдающего", "Сдающий", "Заказчик"],
            "correct": 0,
            "explanation": "В распасе первым ходит игрок слева от сдающего."
        },
        {
            "q": "Цель распаса?",
            "a": ["Не взять ни одной взятки", "Взять все козыри", "Набрать больше взяток"],
            "correct": 0,
            "explanation": "В распасе выигрывает тот, кто не взял ни одной взятки."
        },
        {
            "q": "Сколько очков «в гору» пишут за одну взятку?",
            "a": ["1", "5", "10"],
            "correct": 0,
            "explanation": "За каждую взятку в распасе начисляют 1 очко «в гору»."
        },
        {
            "q": "Можно ли играть распас на четверых?",
            "a": ["Да", "Нет, только втроём", "Только по договорённости"],
            "correct": 0,
            "explanation": "Да — сдающий раздаёт две карты «в темную» из прикупа."
        },
        {
            "q": "Что происходит, если кто-то взял все 10 взяток?",
            "a": ["Игра продолжается", "Распас переигрывается", "Меняют козырь"],
            "correct": 0,
            "explanation": "Если кто-то взял все взятки, остальные ему глубоко сочувствуют — игра продолжается."
        },
    ],
    "test_vists": [
        {
            "q": "Что такое вист?",
            "a": ["Ставка против заказчика", "Игра вслепую", "Особый прикуп"],
            "correct": 0,
            "explanation": "Вист — ставка игроков слева и справа против заказчика."
        },
        {
            "q": "Сколько вистов может быть?",
            "a": ["До двух", "Неограниченно", "Только один"],
            "correct": 0,
            "explanation": "Вистовать могут двое: слева и справа от заказчика."
        },
        {
            "q": "Можно ли отказаться от виста?",
            "a": ["Да", "Нет", "Только при мизере"],
            "correct": 0,
            "explanation": "Игрок может не выставлять вист, если не хочет участвовать."
        },
        {
            "q": "Против мизера вистов не бывает?",
            "a": ["Правда", "Неправда", "Иногда"],
            "correct": 0,
            "explanation": "Вист против мизера запрещён."
        },
        {
            "q": "Сколько очков «в гору» получает неудачный вист?",
            "a": ["1", "2", "5"],
            "correct": 0,
            "explanation": "Неудачный вист приносит 1 очко «в гору»."
        },
        {
            "q": "Кто платит за неудачный вист?",
            "a": ["Вистующий", "Заказчик", "Все игроки"],
            "correct": 0,
            "explanation": "Если вистующий не помешал заказчику, он получает штраф."
        },
    ],
    "test_advanced": [
        {
            "q": "Можно ли играть мизер при одном тузе в червах?",
            "a": ["Да", "Нет", "Только после распаса"],
            "correct": 1,
            "explanation": "Наличие сильной карты делает мизер рискованным."
        },
        {
            "q": "Как понять хороший распас?",
            "a": ["Мало старших карт", "Много козырей", "Много взяток"],
            "correct": 0,
            "explanation": "Хороший распас — руки со слабыми картами."
        },
    ]
}

# 3) Хранилище прогресса тестов
user_progress = {}

# 4) Хранилище состояния симулятора
user_sim = {}


# ==== ОБРАБОТЧИКИ ТЕСТОВ ====

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! 👋 Выбери пункт меню:", reply_markup=main_menu)

@dp.callback_query_handler(lambda c: c.data.startswith("test_"))
async def start_test(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    test_id = callback.data
    user_progress[user_id] = {"test_id": test_id, "q_idx": 0, "correct": 0}
    await callback.message.edit_text("📋 Начинаем тест!", reply_markup=None)
    await send_question(callback.message, user_id)

async def send_question(message: types.Message, user_id: int):
    prog = user_progress.get(user_id)
    if not prog:
        await message.answer("Ошибка прогресса. Попробуй /start")
        return

    test_id = prog["test_id"]
    q_idx = prog["q_idx"]
    test = tests[test_id]

    if q_idx >= len(test):
        total = len(test)
        correct = prog["correct"]
        await message.answer(f"✅ Тест завершён: {correct}/{total} правильных.", reply_markup=main_menu)
        return

    item = test[q_idx]
    kb = InlineKeyboardMarkup(row_width=1)
    for i, opt in enumerate(item["a"]):
        cb = f"answer|{test_id}|{q_idx}|{i}"
        kb.add(InlineKeyboardButton(opt, callback_data=cb))

    await message.answer(f"❓ {item['q']}", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("answer|"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split("|")
    _, test_id, q_idx, ans_idx = parts
    q_idx = int(q_idx); ans_idx = int(ans_idx)

    prog = user_progress.get(user_id)
    if not prog or prog["test_id"] != test_id:
        prog = {"test_id": test_id, "q_idx": q_idx, "correct": 0}
        user_progress[user_id] = prog

    question = tests[test_id][q_idx]
    correct = question["correct"]
    text = "✅ Правильно!" if ans_idx == correct else f"❌ Неправильно, верный ответ: {question['a'][correct]}"
    expl = question.get("explanation")
    if expl:
        text += f"\nℹ️ {expl}"

    await callback.message.answer(text)
    prog["q_idx"] = q_idx + 1
    await send_question(callback.message, user_id)


# ==== СИМУЛЯТОР РАЗДАЧ (ТОРГОВЛЯ) ====

@dp.callback_query_handler(lambda c: c.data == "sim_main")
async def sim_main(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🃏 Торговля", callback_data="sim_trade"),
        InlineKeyboardButton("🏁 В меню", callback_data="sim_exit")
    )
    await callback.message.edit_text("🚀 Симулятор раздач:\nВыберите режим:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "sim_exit")
async def sim_exit(callback: types.CallbackQuery):
    await callback.message.edit_text("Вы вернулись в главное меню.", reply_markup=main_menu)

@dp.callback_query_handler(lambda c: c.data == "sim_trade")
async def sim_trade(callback: types.CallbackQuery):
    # сгенерировать колоду и раздать
    suits = ["♠","♥","♦","♣"]
    ranks = ["7","8","9","10","J","Q","K","A"]
    deck = [r + s for s in suits for r in ranks]
    random.shuffle(deck)
    hand = deck[:10]
    prikup = deck[10:12]

    uid = callback.from_user.id
    user_sim[uid] = {"mode": "trade", "hand": hand, "prikup": prikup}

    text = (
        f"🃏 Симулятор торговли 🃏\n\n"
        f"Ваша рука:\n{' '.join(hand)}\n\n"
        f"Прикуп:\n{' '.join(prikup)}\n\n"
        "Выберите контракт:"
    )
    kb = InlineKeyboardMarkup(row_width=3)
    for opt in ["8","9","10","мизер","распас"]:
        kb.add(InlineKeyboardButton(opt, callback_data=f"sim_ans|{opt}"))
    kb.add(InlineKeyboardButton("🏁 В меню", callback_data="sim_exit"))
    await callback.message.edit_text(text, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("sim_ans|"))
async def sim_answer(callback: types.CallbackQuery):
    uid = callback.from_user.id
    state = user_sim.get(uid)
    if not state or state.get("mode") != "trade":
        await callback.message.answer("❗️ Симулятор не запущен. Наберите /start")
        return

    chosen = callback.data.split("|",1)[1]
    # простая логика: «правильный» контракт — 10
    correct = "10"
    if chosen == correct:
        res = "✅ Правильно! По книге Лесного, «10» — оптимальный контракт при множестве старших карт."
    else:
        res = f"❌ Неверно. Оптимальный контракт — 10."

    # вернуть в меню симулятора
    await callback.message.edit_text(res)
    # заново предложить режимы симулятора
    await sim_main(callback)

# ==== ЗАПУСК ====

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
