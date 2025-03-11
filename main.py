import os
import sqlite3
import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN" )
if not API_TOKEN:
    raise ValueError("No API token provided. Set the TELEGRAM_API_TOKEN environment variable.")


# States
class UserStates(StatesGroup):
    language_selection = State()
    main_menu = State()


# Database setup
def setup_db():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        user_id INTEGER PRIMARY KEY,
        chosen_language TEXT
    )
    ''')
    conn.commit()
    conn.close()


def get_user_language(user_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT chosen_language FROM user_data WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def save_user_language(user_id, language):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_data (user_id, chosen_language) VALUES (?, ?)",
                   (user_id, language))
    conn.commit()
    conn.close()


# Multilingual content
texts = {
    "ru": {
        "welcome": "Здравствуйте, рады приветствовать вас! 🌿\n\n"
                   "Вы общаетесь с ботом благотворительного проекта Ilmli Uzbek. Здесь каждый человек важен, а каждое доброе дело бесценно. "
                   "Мы верим, что именно доброта и милосердие способны изменить этот мир, и надеемся, что сделаем это вместе с вами!\n\n"
                   "🌟 Ilmli Uzbek – Меняем мир через милосердие!\n\n"
                   "Выберите язык, на котором вам удобно общаться:",
        "welcome_back": "🌟 С возвращением! Очень рады видеть вас снова! Вместе к добру и свету! ✨\n\n"
                        "Мы верим, что именно доброта и милосердие способны изменить этот мир, и надеемся, что сделаем это вместе с вами!\n\n"
                        "🌟 Ilmli Uzbek – Меняем мир через милосердие!\n\n",
        "language_selected": "Вы выбрали русский язык.",
        "main_menu": "Главное меню:",
        "about_us": "О нас",
        "donate": "Пожертвовать",
        "contact": "Связаться с нами",
        "back": "Назад в меню",
        "about_us_text": "📌 Коротко о нас\n\n"
                         "Проект Ilmli Uzbek был основан в начале 2024 года.\n"
                         "Наша цель — пробуждать в людях доброту и милосердие, создавая культуру заботы и взаимопомощи в обществе. "
                         "Мы стремимся не просто оказывать помощь, а вдохновлять каждого человека быть внимательным и отзывчивым к другим. "
                         "Вместе с вами мы верим, что можем изменить мир к лучшему! 🌿\n\n"
                         "📊 Ilmli Uzbek в цифрах\n\n"
                         "💰 На сегодняшний день уже пожертвовано более 20 000 000 сум. И это результат вашей щедрости и доверия!\n\n"
                         "👥 Сейчас в нашей команде 25 неравнодушных человек, но мы хотим расти дальше, приглашая вас присоединиться и вместе сделать ещё больше!\n\n"
                         "Вместе наполним мир добром и милосердием! ✨",
        "donate_text": "🌱 Любая ваша помощь, даже самый скромный вклад, становится зерном, прорастающим во сто крат! "
                       "Пусть каждый сум, пожертвованный вами, вернётся к вам многократно, принося процветание и благо!\n\n"
                       "💳 5614 6812 5610 0490 – Abdullayev Behruz\n"
                       "💳 9860 1701 1462 2237 – Sultanbek Azimov",
        "contact_text": "🤝 Хотите стать частью большой и доброй истории? Мы всегда открыты к сотрудничеству, и не важно, "
                        "материальный это вклад или личное участие – каждое проявление добра ценно для нас!\n\n"
                        "📩 Пишите нам прямо сейчас:\n"
                        "• @sultnavw\n"
                        "• @abdlv_bekhruz\n"
                        "• @ab177771"
    },
    "uz": {
        "welcome": "Assalomu alaykum, xush kelibsiz! 🌿\n\n"
                   "Siz hozir Ilmli Uzbek xayriya loyihasining botidasiz. Bu yerda har bir inson qadrlanadi, har bir ezgu ish esa ulkan ahamiyatga ega. "
                   "Biz mehr orqali dunyoni yaxshilik sari o'zgartiramiz va siz bilan birga bunga erishamiz deb umid qilamiz!\n\n"
                   "🌟 Ilmli Uzbek – Mehr bilan dunyoni o'zgartiramiz!\n\n"
                   "Sizga muloqot qilish qulay bo'lgan tilni tanlang:",
        "welcome_back": "🌟 Assalomu alaykum! Sizni yana ko'rganimizdan juda mamnunmiz! Birga yaxshilik sari! ✨\n\n"
                        "Biz mehr orqali dunyoni yaxshilik sari o'zgartiramiz va siz bilan birga bunga erishamiz deb umid qilamiz!\n\n"
                        "🌟 Ilmli Uzbek – Mehr bilan dunyoni o'zgartiramiz!\n\n",
        "language_selected": "Siz o'zbek tilini tanladingiz.",
        "main_menu": "Asosiy menyu:",
        "about_us": "Biz haqimizda",
        "donate": "Ehson qilish",
        "contact": "Bog'lanish",
        "back": "Menyuga qaytish",
        "about_us_text": "📌 Biz haqimizda qisqacha\n\n"
                         "Ilmli Uzbek loyihasi 2024-yil boshida tashkil etilgan.\n"
                         "Biz inson qalbidagi yaxshilik va mehrni uyg'otib, jamiyatda haqiqiy ezgulik madaniyatini shakllantirishga harakat qilamiz. "
                         "Bizning vazifamiz faqatgina yordam berish emas, balki har bir insonning qalbida boshqa insonlarga muhabbat va mehr uyg'otishdir. "
                         "Siz bilan birga bu dunyoni yaxshilik sari o'zgartira olishimizga ishonamiz! 🌿\n\n"
                         "📊 Ilmli Uzbek raqamlarda\n\n"
                         "💰 Bugungacha 20 000 000 so'mdan ortiq mablag' ehson qilindi. Bu – har biringizning ishonch va mehringiz natijasidir.\n\n"
                         "👥 Bizning safimizda ayni paytda 25 nafar mehribon inson bor, ammo biz siz bilan yanada kattaroq va yanada ta'sirli jamoaga aylanishni xohlaymiz!\n\n"
                         "Birga bo'lsak, dunyoni yaxshilikka to'ldira olamiz! ✨",
        "donate_text": "🌱 Sizning har bir ehsoningiz, har bir kichik xayringiz yuzlab barobar hosil beruvchi yaxshilik urug'iga aylanadi! "
                       "Qilgan xayr-saxovatingiz o'zingizga ko'payib, rizqingiz kengaysin, yaxshiliklaringiz ko'paysin!\n\n"
                       "💳 5614 6812 5610 0490 – Abdullayev Behruz\n"
                       "💳 9860 1701 1462 2237 – Sultanbek Azimov",
        "contact_text": "🤝 Katta va xayrli hikoyamizning bir qismiga aylanishni istaysizmi? Biz hamkorlik uchun doimo ochiqmiz! "
                        "Moddiy yoki amaliy yordam — har qanday ko'rinishdagi ko'mak biz uchun bebaho.\n\n"
                        "📩 Bizga bog'laning:\n"
                        "• @sultnavw\n"
                        "• @abdlv_bekhruz\n"
                        "• @ab177771"
    }
}


def get_main_menu_keyboard(language):
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text=texts[language]["about_us"])
    keyboard.button(text=texts[language]["donate"])
    keyboard.button(text=texts[language]["contact"])
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def get_back_keyboard(language):
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text=texts[language]["back"])
    return keyboard.as_markup(resize_keyboard=True)


# Create a router
router = Router()


# Handler for start command
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # Clear previous state
    await state.clear()

    # Check if user already has a language preference
    user_id = message.from_user.id
    language = get_user_language(user_id)

    if language:
        # User already has a language preference, show welcome back message
        await message.answer(
            texts[language]["welcome_back"],
            reply_markup=get_main_menu_keyboard(language)
        )
        await state.set_state(UserStates.main_menu)
    else:
        # New user, show language selection
        keyboard = ReplyKeyboardBuilder()
        keyboard.button(text="Русский 🇷🇺")
        keyboard.button(text="O'zbekcha 🇺🇿")
        keyboard.adjust(2)

        # Get welcome message - first line only to keep it short for the initial greeting
        ru_welcome = texts["ru"]["welcome"].split("\n")[0]
        uz_welcome = texts["uz"]["welcome"].split("\n")[0]

        # Send welcome message with language options
        await message.answer(f"{ru_welcome}\n{uz_welcome}", reply_markup=keyboard.as_markup(resize_keyboard=True))
        await state.set_state(UserStates.language_selection)


# Handler for language selection
@router.message(UserStates.language_selection)
async def process_language(message: Message, state: FSMContext):
    language = None

    if message.text == "Русский 🇷🇺":
        language = "ru"
    elif message.text == "O'zbekcha 🇺🇿":
        language = "uz"
    else:
        # Invalid selection, ask again
        keyboard = ReplyKeyboardBuilder()
        keyboard.button(text="Русский 🇷🇺")
        keyboard.button(text="O'zbekcha 🇺🇿")
        keyboard.adjust(2)
        await message.answer("Пожалуйста, выберите язык / Iltimos, tilni tanlang:",
                             reply_markup=keyboard.as_markup(resize_keyboard=True))
        return

    # Save user's language preference
    user_id = message.from_user.id
    save_user_language(user_id, language)

    # Notify user about the selection
    await message.answer(texts[language]["language_selected"])

    # Show main menu
    await message.answer(
        texts[language]["main_menu"],
        reply_markup=get_main_menu_keyboard(language)
    )
    await state.set_state(UserStates.main_menu)


# Handler for main menu
@router.message(UserStates.main_menu)
async def process_main_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = get_user_language(user_id)

    if not language:
        # If language is not set (which shouldn't happen), restart
        await cmd_start(message, state)
        return

    if message.text == texts[language]["about_us"]:
        # Send About Us information with image
        try:
            photo = FSInputFile('about_us.jpg')
            await message.answer_photo(
                photo=photo,
                caption=texts[language]["about_us_text"],
                reply_markup=get_back_keyboard(language)
            )
        except FileNotFoundError:
            # If image not found, just send the text
            await message.answer(
                texts[language]["about_us_text"],
                reply_markup=get_back_keyboard(language)
            )

    elif message.text == texts[language]["donate"]:
        # Send donation information
        await message.answer(
            texts[language]["donate_text"],
            reply_markup=get_back_keyboard(language)
        )

    elif message.text == texts[language]["contact"]:
        # Send contact information
        await message.answer(
            texts[language]["contact_text"],
            reply_markup=get_back_keyboard(language)
        )

    elif message.text == texts[language]["back"]:
        # Return to main menu
        await message.answer(
            texts[language]["main_menu"],
            reply_markup=get_main_menu_keyboard(language)
        )

    else:
        # Handle unexpected input
        await message.answer(
            texts[language]["main_menu"],
            reply_markup=get_main_menu_keyboard(language)
        )


# Handler for language command
@router.message(Command("language"))
async def cmd_change_language(message: Message, state: FSMContext):
    # Show language selection regardless of current state
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="Русский 🇷🇺")
    keyboard.button(text="O'zbekcha 🇺🇿")
    keyboard.adjust(2)

    # Get bilingual message
    ru_message = "Выберите язык:"
    uz_message = "Tilni tanlang:"

    # Send message with language options
    await message.answer(f"{ru_message}\n{uz_message}", reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(UserStates.language_selection)


async def ensure_about_us_image():
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Check if about_us.jpg needs to be created or resized
        if not os.path.exists('about_us.jpg'):
            # Use the provided image if available
            if os.path.exists('attached_assets/_DSC4241.JPG'):
                # Open and resize the image instead of just copying
                img = Image.open('attached_assets/_DSC4241.JPG')
                # Resize to a reasonable size (max 1600px width, maintain aspect ratio)
                max_width = 1600
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.LANCZOS)
                # Save with reduced quality to keep file size small
                img.save('about_us.jpg', quality=85, optimize=True)
                logging.info("Using resized image as about_us.jpg")
            else:
                # Create a text-based image if no image is available
                img = Image.new('RGB', (800, 400), color=(73, 109, 137))
                d = ImageDraw.Draw(img)

                # Add some text
                d.text((10, 10), "Ilmli Uzbek", fill=(255, 255, 0))
                d.text((10, 50), "Charity Project", fill=(255, 255, 0))

                # Save the image
                img.save('about_us.jpg')
                logging.info("Created a default about_us.jpg image")
    except ImportError:
        logging.warning("PIL not installed, cannot create or resize image")
        if not os.path.exists('about_us.jpg') and os.path.exists('attached_assets/_DSC4241.JPG'):
            import shutil
            shutil.copy('attached_assets/_DSC4241.JPG', 'about_us.jpg')
            logging.warning("Copied image without resizing - may be too large for Telegram")


async def main():
    # Setup database
    setup_db()
    await ensure_about_us_image()

    # Initialize bot and dispatcher
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # Include the router in the dispatcher
    dp.include_router(router)

    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())