import os
import sys
import django
import asyncio
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from asgiref.sync import sync_to_async

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'secret_santa.settings')
django.setup()

from django.conf import settings
from santa_game.models import Participant, GameSession
from santa_game.utils import get_participant_match, link_telegram_user

# Оборачиваем синхронные функции для использования в async контексте
get_participant_match_async = sync_to_async(get_participant_match, thread_sensitive=True)
link_telegram_user_async = sync_to_async(link_telegram_user, thread_sensitive=True)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_main_keyboard():
    """Создает основную клавиатуру с командами"""
    keyboard = [
        [KeyboardButton("🎁 Мой получатель"), KeyboardButton("ℹ️ Информация")],
        [KeyboardButton("🔔 Напоминание"), KeyboardButton("❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def get_game_session():
    """Получает активную игровую сессию"""
    return await sync_to_async(GameSession.objects.filter(is_active=True).first)()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user
    telegram_id = user.id
    
    # Проверяем, есть ли уже зарегистрированный участник
    try:
        participant = await sync_to_async(Participant.objects.get)(telegram_user_id=telegram_id, is_active=True)
        
        # Получаем информацию о распределении
        match_info = await get_participant_match_async(telegram_id)
        
        if match_info['success']:
            receiver = match_info['receiver']
            
            # Получаем информацию об активной игре
            game_session = await sync_to_async(GameSession.objects.filter(is_active=True).first)()
            
            game_session = await get_game_session()
            
            message = (
                f"🎅 С возвращением, {participant.name}!\n\n"
                f"🎁 Ты тайный Санта для:\n"
                f"👤 {receiver.name}\n\n"
            )
            
            if game_session:
                if game_session.gift_date:
                    message += f"📅 Дата вручения: {game_session.gift_date.strftime('%d.%m.%Y')}\n"
                if game_session.budget:
                    message += f"💰 Бюджет: {int(game_session.budget):,} сум\n"
                
                if game_session.gift_date:
                    from datetime import date
                    days_left = (game_session.gift_date - date.today()).days
                    if days_left > 0:
                        message += f"⏰ Осталось: {days_left} дней\n"
                    elif days_left == 0:
                        message += f"⏰ Сегодня день вручения!\n"
            
            message += "\n🤫 Помни: это секрет!\n"
            message += "🎄 Удачи в выборе подарка!"
        else:
            if match_info['error'] == 'match_not_generated':
                message = (
                    f"Привет, {participant.name}!\n\n"
                    f"Вы зарегистрированы в игре, но распределение ещё не проведено.\n"
                    f"Подождите, пока администратор запустит игру."
                )
            else:
                message = "Произошла ошибка. Обратитесь к администратору."
        
        await update.message.reply_text(message, reply_markup=get_main_keyboard())
        
    except Participant.DoesNotExist:
        # Участник не найден, просим поделиться номером телефона
        keyboard = [[KeyboardButton("📱 Поделиться номером", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        message = (
            "🎅 Добро пожаловать в игру Secret Santa! 🎄\n\n"
            "Для участия в игре, пожалуйста, поделитесь своим номером телефона.\n"
            "Этот номер должен быть зарегистрирован администратором."
        )
        
        await update.message.reply_text(message, reply_markup=reply_markup)


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка полученного контакта"""
    contact = update.message.contact
    phone_number = contact.phone_number
    telegram_id = update.effective_user.id
    
    # Нормализуем номер телефона (убираем +)
    phone_number = phone_number.replace('+', '')
    
    # Пробуем связать участника с Telegram аккаунтом
    result = await link_telegram_user_async(phone_number, telegram_id)
    
    if result['success']:
        participant = result['participant']
        
        # Получаем информацию о распределении
        match_info = await get_participant_match_async(telegram_id)
        
        if match_info['success']:
            receiver = match_info['receiver']
            
            # Получаем информацию об активной игре
            game_session = await sync_to_async(GameSession.objects.filter(is_active=True).first)()
            
            game_session = await get_game_session()
            
            message = (
                f"✅ Отлично, {participant.name}!\n"
                f"  Вы успешно вошли в игру!\n\n"
                f"🎁 Ты тайный Санта для:\n"
                f"👤 {receiver.name}\n\n"
            )
            
            if game_session:
                if game_session.gift_date:
                    message += f"📅 Дата вручения: {game_session.gift_date.strftime('%d.%m.%Y')}\n"
                if game_session.budget:
                    message += f"💰 Бюджет: {int(game_session.budget):,} сум\n"
                
                if game_session.gift_date:
                    from datetime import date
                    days_left = (game_session.gift_date - date.today()).days
                    if days_left > 0:
                        message += f"⏰ Осталось: {days_left} дней\n"
                    elif days_left == 0:
                        message += f"⏰ Сегодня день вручения!\n"
            
            message += "\n🤫 Помни: это секрет!\n"
            message += "🎄 Удачи в выборе подарка!"
        else:
            if match_info['error'] == 'match_not_generated':
                message = (
                    f"✅ Отлично, {participant.name}! Вы зарегистрированы.\n\n"
                    f"Распределение ещё не проведено.\n"
                    f"Подождите, пока администратор запустит игру."
                )
            else:
                message = "Произошла ошибка. Обратитесь к администратору."
    else:
        message = (
            "❌ К сожалению, ваш номер телефона не найден в списке участников.\n"
            "Обратитесь к администратору для регистрации."
        )
    
    await update.message.reply_text(message, reply_markup=get_main_keyboard())


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /info - информация об игре"""
    user = update.effective_user
    telegram_id = user.id
    
    try:
        participant = await sync_to_async(Participant.objects.get)(telegram_user_id=telegram_id, is_active=True)
        game_session = await sync_to_async(GameSession.objects.filter(is_active=True).first)()
        
        if not game_session:
            await update.message.reply_text("Активная игра не найдена.")
            return
        
        message = f"🎅 {game_session.name}\n\n"
        
        if game_session.description:
            message += f"📝 Описание:\n{game_session.description}\n\n"
        
        if game_session.gift_date:
            message += f"📅 Дата вручения: {game_session.gift_date.strftime('%d.%m.%Y')}\n"
            
            from datetime import date
            days_left = (game_session.gift_date - date.today()).days
            if days_left > 0:
                message += f"⏰ Осталось {days_left} дней\n"
            elif days_left == 0:
                message += f"⏰ Сегодня день вручения!\n"
        
        if game_session.budget:
            message += f"💰 Бюджет на подарок: {int(game_session.budget):,} сум\n"
        
        message += "\n🎄 Правила:\n"
        message += "• Держите получателя в секрете\n"
        message += "• Соблюдайте бюджет\n"
        message += "• Упакуйте красиво\n"
        message += "• Подпишите получателя (без отправителя)\n"
        message += "• Принесите в офис: ул. Мукимий 17, Ташкент\n\n"
        message += "✨ Пусть праздник будет волшебным!"

        await update.message.reply_text(message, reply_markup=get_main_keyboard())
        
    except Participant.DoesNotExist:
        await update.message.reply_text(
            "Вы не зарегистрированы в игре. Нажмите /start для регистрации."
        )


async def reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /reminder - напоминание о получателе"""
    user = update.effective_user
    telegram_id = user.id
    
    try:
        participant = await sync_to_async(Participant.objects.get)(telegram_user_id=telegram_id, is_active=True)
        match_info = await get_participant_match_async(telegram_id)
        
        if match_info['success']:
            receiver = match_info['receiver']
            game_session = await sync_to_async(GameSession.objects.filter(is_active=True).first)()
            
            message = (
                f"🔔 Напоминание\n\n"
                f"🎁 Ты тайный Санта для:\n"
                f"👤 {receiver.name}\n\n"
            )
            
            if game_session:
                if game_session.gift_date:
                    from datetime import date
                    days_left = (game_session.gift_date - date.today()).days
                    if days_left > 0:
                        message += f"⏰ Осталось {days_left} дней\n"
                    elif days_left == 0:
                        message += f"⏰ Сегодня день вручения!\n"
                    message += "\n"
                
                if game_session.budget:
                    message += f"💰 Бюджет: {int(game_session.budget):,} сум\n\n"
            
            message += "🤫 Помни: это секрет!\n"
            message += "🎄 Удачи в выборе подарка!"
            
            await update.message.reply_text(message, reply_markup=get_main_keyboard())
        else:
            await update.message.reply_text(
                "Распределение ещё не проведено. Подождите, пока администратор запустит игру.",
                reply_markup=get_main_keyboard()
            )
            
    except Participant.DoesNotExist:
        await update.message.reply_text(
            "Вы не зарегистрированы в игре. Нажмите /start для регистрации."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /help"""
    message = (
        "🎅 Secret Santa Bot - Справка\n\n"
        "📱 Команды:\n"
        "• 🎁 Мой получатель - узнать своего получателя\n"
        "• ℹ️ Информация - детали игры\n"
        "• 🔔 Напоминание - кому дарить подарок\n"
        "• ❓ Помощь - эта справка\n\n"
        "🎮 Как играть:\n"
        "1. Поделитесь номером телефона\n"
        "2. Узнайте своего получателя\n"
        "3. Купите подарок в рамках бюджета\n"
        "4. Упакуйте и подпишите (только получателя)\n"
        "5. Принесите в офис\n"
        "6. Держите в секрете! 🤫\n\n"
        "💡 Используйте кнопки внизу\n\n"
        "❓ Вопросы? Обратитесь к администратору"
    )
    
    await update.message.reply_text(message, reply_markup=get_main_keyboard())


async def my_receiver_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает только получателя без дополнительных деталей"""
    user = update.effective_user
    telegram_id = user.id
    
    try:
        participant = await sync_to_async(Participant.objects.get)(telegram_user_id=telegram_id, is_active=True)
        match_info = await get_participant_match_async(telegram_id)
        
        if match_info['success']:
            receiver = match_info['receiver']
            
            message = (
                f"🎁 Твой получатель:\n\n"
                f"👤 {receiver.name}\n\n"
                f"🤫 Помни: это секрет!"
            )
            
            await update.message.reply_text(message, reply_markup=get_main_keyboard())
        else:
            await update.message.reply_text(
                "Распределение ещё не проведено. Подождите, пока администратор запустит игру.",
                reply_markup=get_main_keyboard()
            )
            
    except Participant.DoesNotExist:
        await update.message.reply_text(
            "Вы не зарегистрированы в игре. Нажмите /start для регистрации."
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений от кнопок"""
    text = update.message.text
    
    if text == "🎁 Мой получатель":
        await my_receiver_command(update, context)
    elif text == "ℹ️ Информация":
        await info_command(update, context)
    elif text == "🔔 Напоминание":
        await reminder_command(update, context)
    elif text == "❓ Помощь":
        await help_command(update, context)
    else:
        # Игнорируем другие текстовые сообщения
        pass


async def main():
    """Запуск бота"""
    token = settings.TELEGRAM_BOT_TOKEN
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не установлен в настройках!")
        return
    
    # Создаем приложение
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("reminder", reminder_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Инициализация и запуск
    await application.initialize()
    await application.start()
    
    logger.info("Бот запущен!")
    
    # Запуск polling
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    # Держим бота запущенным
    try:
        import signal
        stop = asyncio.Event()
        
        def signal_handler(sig, frame):
            stop.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        await stop.wait()
    except KeyboardInterrupt:
        pass
    finally:
        # Остановка бота
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
