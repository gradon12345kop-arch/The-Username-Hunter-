import asyncio
import random
import requests
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ==========================================
# ВСТАВЬ СЮДА СВОЙ ТОКЕН И ПАРОЛЬ
# ==========================================
BOT_TOKEN = "8505647675:AAEzw6ymrZ-Qota90XyEVtsxxqNt8jTojvw"
BOT_PASSWORD = "01612"  # <--- ПРИДУМАЙ И ВСТАВЬ СЮДА ПАРОЛЬ

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Состояния для ввода пароля
class AuthState(StatesGroup):
    waiting_for_password = State()

# ==========================================
# БАЗА СЛОВ
# ==========================================
WORDS_5 = [
    "brave", "pizza", "satan", "trade", "magic", "queen", "vibes", "crazy", "happy", "smile", 
    "light", "darkx", "coach", "black", "white", "green", "money", "power", "super", "world", 
    "music", "drink", "night", "angel", "demon", "sword", "crown", "kingz", "queen", "beast",
    "ghost", "storm", "blaze", "frost", "cyber", "ninja", "pixel", "hackz", "vibe", "alpha",
    "bravo", "delta", "omega", "steel", "stone", "ocean", "river", "flame", "venom", "rebel"
]

WORDS_6 = [
    "coffee", "devilz", "future", "master", "legend", "gaming", "crypto", "market", "social", "player",
    "shadow", "dragon", "wizard", "knight", "gaming", "gamer", "legend", "matrix", "system", "hacker",
    "vision", "dreams", "action", "energy", "silver", "golden", "bronze", "plasma", "cosmos", "galaxy",
    "rocket", "strike", "sniper", "tactic", "danger", "escape", "mystic", "secret", "battle", "combat"
]

# ==========================================
# ФУНКЦИИ
# ==========================================
def check_username(username):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    tg_url = f"https://t.me/{username}"
    try:
        resp = requests.get(tg_url, headers=headers, timeout=5)
        if resp.status_code == 404:
            return True
        if "If you have Telegram, you can contact" not in resp.text and "tgme_page_title" not in resp.text:
            return True
    except Exception:
        pass
    return False

def gen_random(length):
    letters = "abcdefghijklmnopqrstuvwxyz"
    return ''.join(random.choice(letters) for _ in range(length))

def make_cool_username(base_word):
    variants = [base_word] 
    leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
    
    for letter, num in leet_map.items():
        if letter in base_word:
            variants.append(base_word.replace(letter, num, 1))
            
    variants.append(base_word + random.choice("xyz"))
    variants.append(base_word + str(random.randint(1, 9)))
    variants.append(base_word[:-1] + str(random.randint(1, 9)))

    return random.choice(variants)

def get_username(length, mode):
    if mode == "rand":
        return gen_random(length)
    
    word_list = WORDS_5 if length == 5 else WORDS_6
    base = random.choice(word_list)
    final_name = make_cool_username(base)
    return final_name[:length] if len(final_name) > length else final_name

# ==========================================
# КРАСИВОЕ МЕНЮ
# ==========================================
def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎲 5 БУКВ | Рандом", callback_data="f_5_rand"))
    builder.row(InlineKeyboardButton(text="💎 5 БУКВ | Слова", callback_data="f_5_word"))
    builder.row(InlineKeyboardButton(text="🔥 6 БУКВ | Слова", callback_data="f_6_word"))
    builder.row(InlineKeyboardButton(text="🎰 6 БУКВ | Рандом", callback_data="f_6_rand"))
    return builder.as_markup()

# ==========================================
# АВТОРИЗАЦИЯ И ХЕНДЛЕРЫ
# ==========================================
@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.set_state(AuthState.waiting_for_password)
    await message.answer(
        "🔒 <b>Доступ закрыт!</b>\n\n"
        "Чтобы войти в систему, введи секретный пароль:",
        parse_mode="HTML"
    )

@router.message(AuthState.waiting_for_password)
async def check_password(message: Message, state: FSMContext):
    if message.text == BOT_PASSWORD:
        await state.clear()
        await message.answer(
            "✅ <b>Пароль верный! Добро пожаловать в элитный клуб.</b>\n\n"
            "🚀 Я — бот-охотник за никами.\n"
            "Выбирай режим, и я найду для тебя лучшие свободные юзернеймы.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ <b>Неверный пароль!</b>\n"
            "Попробуй еще раз, или нажми /start чтобы начать заново.",
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("f_"))
async def find_handler(call: CallbackQuery):
    await call.answer("Начинаю поиск...")
    data = call.data.split("_")
    length = int(data[1])
    mode = data[2]

    await call.message.edit_text(f"🔍 <b>Поиск {length}-буквенных ({mode})...</b>\nПроверяю 25 вариантов. Подожди чуток...", parse_mode="HTML")

    found_count = 0
    
    for _ in range(25): 
        username = get_username(length, mode)
        
        if check_username(username):
            found_count += 1
            await call.message.answer(
                f"✅ <b>@{username}</b> — возможно свободен!\n"
                f"👉 Проверь вручную: https://t.me/{username}",
                parse_mode="HTML"
            )
            await asyncio.sleep(1)
        
        await asyncio.sleep(0.5)

    if found_count == 0:
        await call.message.answer("😔 <b>Ничего не нашёл.</b> Все ники заняты. Попробуй еще раз!", parse_mode="HTML")
    else:
        await call.message.answer(f"🏁 <b>Готово!</b> Нашёл {found_count} свободных ников.", parse_mode="HTML")
    
    await call.message.answer("Выбери режим поиска:", reply_markup=get_main_menu())

# ==========================================
# ЗАПУСК
# ==========================================
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())  # <--- ВОТ ТУТ БЫЛА ОШИБКА, ТЕПЕРЬ ИСПРАВЛЕНО
