#!/usr/bin/env python3
"""
Web-Nify Telegram Bot
Минимальная рабочая версия
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("Токен бота не найден! Установите переменную окружения BOT_TOKEN")
    exit(1)

OWNER_ID = int(os.environ.get('OWNER_ID', 8294608065))

# Простая база данных в памяти
users = {}

# ========== ОБРАБОТЧИКИ КОМАНД ==========

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Сохраняем пользователя
    user_id = user.id
    if user_id not in users:
        users[user_id] = {
            'id': user_id,
            'username': user.username,
            'first_name': user.first_name,
            'balance': 0,
            'unique_id': f"W-{user_id % 1000000:06d}"
        }
    
    await update.message.reply_text(
        "👋 Привет! Я Web-Nify бот!\n"
        "Я помогаю создавать сайты, боты и приложения.\n\n"
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/profile - Мой профиль\n"
        "/balance - Мой баланс\n"
        "/help - Помощь"
    )

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /profile"""
    user_id = update.effective_user.id
    
    if user_id not in users:
        await update.message.reply_text("Сначала используйте /start")
        return
    
    user_data = users[user_id]
    
    await update.message.reply_text(
        f"👤 *Ваш профиль*\n\n"
        f"*Имя:* {user_data['first_name']}\n"
        f"*ID:* `{user_data['unique_id']}`\n"
        f"*Баланс:* {user_data['balance']}₽\n\n"
        f"Для пополнения баланса напишите @webnify",
        parse_mode='Markdown'
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /balance"""
    user_id = update.effective_user.id
    
    if user_id not in users:
        await update.message.reply_text("Сначала используйте /start")
        return
    
    balance = users[user_id]['balance']
    await update.message.reply_text(f"💰 Ваш баланс: {balance}₽")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = (
        "📋 *Доступные команды:*\n\n"
        "/start - Запустить бота\n"
        "/profile - Мой профиль\n"
        "/balance - Мой баланс\n"
        "/catalog - Каталог услуг\n"
        "/support - Поддержка\n"
        "/help - Эта справка\n\n"
        "*Для администратора:*\n"
        "/addmoney - Пополнить баланс\n"
        "/users - Список пользователей"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /catalog"""
    catalog_text = (
        "🛍️ *Каталог услуг:*\n\n"
        "🌐 *Сайты:*\n"
        "• Сайт (Easy) - 49₽\n"
        "• Сайт (Hard) - 69₽\n\n"
        "🤖 *Telegram боты:*\n"
        "• Telegram Bot - 99₽\n\n"
        "📱 *Приложения:*\n"
        "• Для заказа напишите @webnify\n\n"
        "Для заказа напишите @webnify или используйте команды."
    )
    
    await update.message.reply_text(catalog_text, parse_mode='Markdown')

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /support"""
    await update.message.reply_text(
        "🛟 *Поддержка*\n\n"
        "Напишите ваш вопрос, и мы ответим в ближайшее время.\n"
        "Также можете написать напрямую: @webnify",
        parse_mode='Markdown'
    )

# ========== АДМИН КОМАНДЫ ==========

async def addmoney_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /addmoney"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Нет прав доступа!")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text(
            "Использование: /addmoney [user_id] [amount]\n"
            "Пример: /addmoney 123456 1000"
        )
        return
    
    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Неверный формат!")
        return
    
    if user_id not in users:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    users[user_id]['balance'] += amount
    
    # Уведомляем пользователя
    try:
        await context.bot.send_message(
            user_id,
            f"💰 Ваш баланс пополнен на {amount}₽!\n"
            f"Новый баланс: {users[user_id]['balance']}₽\n\n"
            f"Thanks For Donating!"
        )
    except Exception as e:
        logger.error(f"Не удалось уведомить пользователя: {e}")
    
    await update.message.reply_text(f"✅ Баланс пользователя {user_id} пополнен на {amount}₽")

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /users"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Нет прав доступа!")
        return
    
    if not users:
        await update.message.reply_text("📭 Пользователей пока нет")
        return
    
    users_list = "📋 *Список пользователей:*\n\n"
    for user_id, user_data in users.items():
        users_list += f"• {user_data['first_name']} (@{user_data['username']}) - {user_data['unique_id']} - {user_data['balance']}₽\n"
    
    await update.message.reply_text(users_list, parse_mode='Markdown')

# ========== ОБРАБОТЧИК СООБЩЕНИЙ ==========

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик обычных сообщений"""
    text = update.message.text
    
    if "привет" in text.lower():
        await update.message.reply_text("Привет! Как дела?")
    elif "баланс" in text.lower():
        await balance_command(update, context)
    elif "помощь" in text.lower():
        await help_command(update, context)
    else:
        await update.message.reply_text(
            "Не понял ваш запрос. Используйте /help для списка команд."
        )

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========

def main():
    """Запуск бота"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("profile", profile_command))
        application.add_handler(CommandHandler("balance", balance_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("catalog", catalog_command))
        application.add_handler(CommandHandler("support", support_command))
        application.add_handler(CommandHandler("addmoney", addmoney_command))
        application.add_handler(CommandHandler("users", users_command))
        
        # Обработчик текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Запускаем бота
        logger.info("🤖 Бот запускается...")
        print("=" * 50)
        print("Web-Nify Bot запущен!")
        print(f"Owner ID: {OWNER_ID}")
        print("=" * 50)
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == '__main__':
    main()
