
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import os
from datetime import datetime  # Vaqtni olish uchun modul
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
# Botni tokeni va admin ID
API_TOKEN = '7220680847:AAFLYHndMlV4KyGwFu2ZC-A0z0kV3uu1yco'
ADMIN_IDS = [1754231198, 7029300410, 777307464,281437924,5883507130,281437924]  # Bir nechta admin ID'lari
NOTIFY_USER_ID = 7029300410
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Excel fayl nomi
EXCEL_FILE = 'hisobot.xlsx'
# Bot ishga tushganda xabar yuborish funksiyasi


# Excel faylni yaratish agar mavjud bo'lmasa
def create_excel_file():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=['User ID', 'FISH', 'Username', 'Taklif', 'Time'])
        df.to_excel(EXCEL_FILE, index=False)




# Fikrni Excel faylga qo'shish (vaqtni qo'shib)
def add_feedback_to_excel(user_id, full_name, username, feedback):
    df = pd.read_excel(EXCEL_FILE)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Hozirgi vaqtni olish
    new_row = pd.DataFrame({
        'User ID': [user_id],
        'FISH': [full_name],  # FISH ustuni uchun to'ldirish
        'Username': [username],
        'Taklif': [feedback],
        'Time': [current_time]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)


# /clear buyrug'i admin tomonidan faylni tozalash
@dp.message_handler(commands=['clear'])
async def clear_excel(message: types.Message):
    if message.from_user.id in ADMIN_IDS:  # Foydalanuvchi ID'sini admin ro'yxatidan tekshirish
        # Excel faylini tozalash
        df = pd.DataFrame(columns=['User ID', 'FISH', 'Username', 'Taklif', 'Time'])
        df.to_excel(EXCEL_FILE, index=False)
        await message.answer("Excel fayli tozalandi.")
    else:
        await message.answer("Sizga bu buyruqdan foydalanishga ruxsat yo'q.")


# /start buyrug'i
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # Til tanlash keyboardi
    language_keyboard = InlineKeyboardMarkup(row_width=2)
    uzb_button = InlineKeyboardButton('🇺🇿 UZB', callback_data='lang_uz')
    rus_button = InlineKeyboardButton('🇷🇺 RUS', callback_data='lang_ru')
    language_keyboard.add(uzb_button, rus_button)

    await message.answer(
        "🔸<b>Assalomu alaykum hurmatli fuqaro!</b>\nNavoiy viloyati Prokuraturasi hamda IIB JXX Yo'l harakat xavfsizligi boshqarmasi tomonidan tashkil etilgan telegram botiga Xush kelibsiz! <i>Tilni tanlang:</i>\n\n"
        "🔸<b>Здравствуйте, уважаемый гражданин!</b>\nДобро пожаловать в телеграм-бот, организованный Прокуратурой Навоийской области и управлением безопасности дорожного движения! <i>Выберите язык:</i>",
        parse_mode='HTML', reply_markup=language_keyboard)


# Yangi holatlar: ism va familiya kiritish uchun
class FeedbackState(StatesGroup):
    waiting_for_name_uz = State()
    waiting_for_name_ru = State()
    waiting_for_feedback = State()
    waiting_for_feedback_rus = State()


# Til tanlanganda
@dp.callback_query_handler(lambda c: c.data in ['lang_uz', 'lang_ru'])
async def language_selected(callback_query: types.CallbackQuery):
    lang = callback_query.data

    if lang == 'lang_uz':
        await bot.send_message(callback_query.from_user.id, "Iltimos, ism va familiyangizni kiriting:")
        await FeedbackState.waiting_for_name_uz.set()  # Yangi holat ism kiritish uchun
    elif lang == 'lang_ru':
        await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите ваше имя и фамилию:")
        await FeedbackState.waiting_for_name_ru.set()  # Ruscha ism kiritish uchun yangi holat

    await bot.answer_callback_query(callback_query.id)


# Foydalanuvchi ism va familiyasini kiritganda (O'zbekcha)
@dp.message_handler(state=FeedbackState.waiting_for_name_uz, content_types=types.ContentType.TEXT)
async def process_name_uz(message: types.Message, state: FSMContext):
    full_name = message.text


    # Excel faylga ism-familiyani yozish
    df = pd.read_excel(EXCEL_FILE)
    new_row = pd.DataFrame({

        'FISH': [full_name],  # Foydalanuvchi ismi va familiyasi

    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    # Taklifni kiritishni davom ettirish
    keyboard = InlineKeyboardMarkup()
    feedback_button = InlineKeyboardButton('✏️ Taklif kiritish', callback_data='give_feedback_uz')
    keyboard.add(feedback_button)
    await message.answer("🚔 Yo'l transport hodisalarining oldini olish bo'yicha qanday takliflaringiz bor?",
                         reply_markup=keyboard)

    await state.finish()


# Foydalanuvchi ism va familiyasini kiritganda (Ruscha)
@dp.message_handler(state=FeedbackState.waiting_for_name_ru, content_types=types.ContentType.TEXT)
async def process_name_ru(message: types.Message, state: FSMContext):
    full_name = message.text
    user_id = message.from_user.id
    username = message.from_user.username

    # Excel faylga ism-familiyani yozish
    df = pd.read_excel(EXCEL_FILE)
    new_row = pd.DataFrame({

        'FISH': [full_name],  # Foydalanuvchi ismi va familiyasi

    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    # Taklifni kiritishni davom ettirish
    keyboard = InlineKeyboardMarkup()
    feedback_button = InlineKeyboardButton('️ ✏️ Сделать предложение', callback_data='give_feedback_rus')
    keyboard.add(feedback_button)
    await message.answer("🚔 Какие у вас есть предложения по предотвращению дорожно-транспортных происшествий?",
                         reply_markup=keyboard)

    await state.finish()


# Taklif kiritish (O'zbekcha)
@dp.callback_query_handler(lambda c: c.data == 'give_feedback_uz')
async def give_feedback_uz(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "✍️ Iltimos, taklifingizni yozing:")
    await FeedbackState.waiting_for_feedback.set()
    await bot.answer_callback_query(callback_query.id)


# Taklif yozilganda (O'zbekcha)
@dp.message_handler(state=FeedbackState.waiting_for_feedback, content_types=types.ContentType.TEXT)
async def process_feedback_uz(message: types.Message, state: FSMContext):
    user_feedback = message.text
    user_id = message.from_user.id
    user_name = message.from_user.full_name  # Foydalanuvchi nomi
    username = message.from_user.username  # Username
    add_feedback_to_excel(user_id, user_name, username, user_feedback)

    # Rahmat xabarini yuborish
    await message.answer("✅ Rahmat! Sizning taklifingiz qabul qilindi.")

    # Yana "Taklif kiritish" va "Boshqa taklif yo'q" tugmalari
    keyboard = InlineKeyboardMarkup(row_width=1)
    feedback_button = InlineKeyboardButton('✏️ Taklif kiritish', callback_data='give_feedback_uz')
    no_feedback_button = InlineKeyboardButton('🚫 Menda boshqa taklif yo\'q', callback_data='no_more_feedback_uz')
    keyboard.add(feedback_button, no_feedback_button)
    await message.answer("Yana qanday takliflaringiz bor?", reply_markup=keyboard)

    await state.finish()


# Taklif kiritish (Ruscha)
@dp.callback_query_handler(lambda c: c.data == 'give_feedback_rus')
async def give_feedback_rus(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "✍️ Пожалуйста, напишите ваше предложение:")
    await FeedbackState.waiting_for_feedback_rus.set()
    await bot.answer_callback_query(callback_query.id)


# Taklif yozilganda (Ruscha)
@dp.message_handler(state=FeedbackState.waiting_for_feedback_rus, content_types=types.ContentType.TEXT)
async def process_feedback_rus(message: types.Message, state: FSMContext):
    user_feedback = message.text
    user_id = message.from_user.id
    user_name = message.from_user.full_name  # Foydalanuvchi nomi
    username = message.from_user.username  # Username
    add_feedback_to_excel(user_id, user_name, username, user_feedback)

    # Rahmat xabarini yuborish
    await message.answer("✅ Спасибо! Ваше предложение принято.")

    # Yana "Taklif kiritish" va "Boshqa taklif yo'q" tugmalari
    keyboard = InlineKeyboardMarkup(row_width=1)
    feedback_button = InlineKeyboardButton('️ ✏️ Сделать предложение', callback_data='give_feedback_rus')
    no_feedback_button = InlineKeyboardButton('🚫 У меня больше нет предложений', callback_data='no_more_feedback_rus')
    keyboard.add(feedback_button, no_feedback_button)
    await message.answer("У вас есть еще предложения?", reply_markup=keyboard)

    await state.finish()


# Foydalanuvchi boshqa taklif yo'q tugmasini bosganda (O'zbekcha)
@dp.callback_query_handler(lambda c: c.data == 'no_more_feedback_uz')
async def no_more_feedback_uz(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "✅ Taklifingiz uchun Rahmat!")

    # # Botni /start buyrug'iga qaytarish
    # await start_command(callback_query.message)
    #
    # await bot.answer_callback_query(callback_query.id)


# Foydalanuvchi boshqa taklif yo'q tugmasini bosganda (Ruscha)
@dp.callback_query_handler(lambda c: c.data == 'no_more_feedback_rus')
async def no_more_feedback_rus(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
                           "✅ Спасибо за Ваше приглашение!")

    # # Botni /start buyrug'iga qaytarish
    # await start_command(callback_query.message)
    #
    # await bot.answer_callback_query(callback_query.id)


# Excel fayl nomi
EXCEL_FILE = 'hisobot.xlsx'


# /hisobot buyrug'i adminlar uchun: Excel faylni yuborish
@dp.message_handler(commands=['hisobot'])
async def send_excel_report(message: types.Message):
    if message.from_user.id in ADMIN_IDS:  # Foydalanuvchini admin ro'yxatidan tekshirish
        if os.path.exists(EXCEL_FILE):
            # Excel fayl mavjud bo'lsa, uni yuboramiz
            await message.answer_document(types.InputFile(EXCEL_FILE))
        else:
            await message.answer("Excel fayli mavjud emas.")
    else:
        await message.answer("Sizga bu buyruqdan foydalanishga ruxsat yo'q.")

async def on_startup(dp):
    await bot.send_message(NOTIFY_USER_ID, "Bot ishga tushdi!")
if __name__ == '__main__':
    create_excel_file()  # Bot ishga tushganda Excel fayl mavjud bo'lmasa, yaratadi
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)  # on_startup qo'shildi

async def remove_webhook():
    await bot.delete_webhook()

asyncio.run(remove_webhook())

if __name__ == '__main__':
    create_excel_file()  # Bot ishga tushganda Excel fayl mavjud bo'lmasa, yaratadi
    executor.start_polling(dp, skip_updates=True)









