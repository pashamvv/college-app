import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, WebAppInfo
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = "7621000610:AAHgzBhpQ2xjaZFbqLrOMiJvPSM2AxOJHsY"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

users_data = {}

class Registration(StatesGroup):
    full_name = State()
    group = State()

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Показать расписание", callback_data="show_schedule")
    builder.button(text="📖 Показать методики", callback_data="show_methods")
    builder.button(text="🔔 Показать расписание звонков", callback_data="show_bell_schedule")
    builder.button(text="🚀 Открыть Mini App", web_app=WebAppInfo(url="https://mini-app-eabee.web.app/"))
    return builder.as_markup()

@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in users_data:
        await message.answer(f"Привет, {users_data[user_id]['full_name']}! 👋", reply_markup=get_main_menu())
    else:
        await message.answer("Привет! Давай зарегистрируем тебя. Напиши свое ФИО.")
        await state.set_state(Registration.full_name)

@dp.message(Registration.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Отлично! Теперь укажи свою группу.")
    await state.set_state(Registration.group)

@dp.message(Registration.group)
async def process_group(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    users_data[user_id] = {"full_name": data["full_name"], "group": message.text}
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🚀 Открыть Mini App", web_app=WebAppInfo(url="https://mini-app-eabee.web.app/"))]],
        resize_keyboard=True
    )
    await message.answer(f"✅ Регистрация завершена!", reply_markup=get_main_menu())
    await state.clear()

@dp.message(Command("miniapp"))
async def send_miniapp_button(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🚀 Открыть Mini App", web_app=WebAppInfo(url="https://mini-app-eabee.web.app/"))]],
        resize_keyboard=True
    )
    await message.answer("Нажмите кнопку ниже, чтобы открыть Mini App:", reply_markup=keyboard)

@dp.callback_query(F.data.in_(["show_schedule", "show_methods", "show_bell_schedule"]))
async def callback_handler(call: types.CallbackQuery):
    responses = {
        "show_schedule": "📅 *Расписание занятий:*\n🕘 08:00 - 09:30 | Пара 1\n🕙 09:45 - 11:15 | Пара 2",
        "show_methods": "📖 *Методические материалы:*\n1️⃣ Основы программирования\n2️⃣ Алгоритмы и структуры данных",
        "show_bell_schedule": "🔔 *Расписание звонков:*\n🕘 08:00 - 09:30 | 1-я пара\n🕙 09:45 - 11:15 | 2-я пара"
    }
    await call.message.answer(responses[call.data], parse_mode="Markdown")
    await call.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

    